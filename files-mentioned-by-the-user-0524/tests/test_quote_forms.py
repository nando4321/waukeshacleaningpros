"""Quote-form regression tests. Requires Python, Playwright, and Brave."""
import functools
from html.parser import HTMLParser
import http.server
import json
from pathlib import Path
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
KEY='a8eb4e24-7588-4a69-910f-84a32740526c'
ENDPOINT='https://api.web3forms.com/submit'
EXPECTED_FORMS=18

class Forms(HTMLParser):
    def __init__(self):
        super().__init__(); self.forms=[]; self.current=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='form':
            self.current={'attrs':attrs,'inputs':{}};self.forms.append(self.current)
        elif tag=='input' and self.current is not None:
            self.current['inputs'][attrs.get('name')]=attrs
    def handle_endtag(self,tag):
        if tag=='form':self.current=None


def quote_pages():
    pages=[]
    for path in sorted(ROOT.rglob('*.html')):
        parser=Forms();parser.feed(path.read_text())
        for form in parser.forms:
            if set(form['attrs'].get('class','').split()) & {'estimate-card','seo-short-form'}:
                pages.append((path.relative_to(ROOT).as_posix(),form))
    return pages

class QuoteMarkupTests(unittest.TestCase):
    def test_all_forms_have_working_native_provider_configuration(self):
        pages=quote_pages();self.assertEqual(len(pages),EXPECTED_FORMS)
        for path,form in pages:
            with self.subTest(page=path):
                self.assertEqual(form['attrs'].get('action'),ENDPOINT)
                self.assertEqual(form['attrs'].get('method','').upper(),'POST')
                inputs=form['inputs']
                self.assertEqual(inputs['access_key']['value'],KEY)
                self.assertEqual(inputs['redirect']['value'],'https://waukeshacleaningpros.com/thank-you.html')
                self.assertEqual(inputs['email']['type'],'email')
                self.assertIn('required',inputs['email'])
                self.assertIn('subject',inputs)
                self.assertEqual(inputs['botcheck']['type'],'checkbox')
                self.assertFalse(any(n.startswith('_') for n in inputs if n))

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,format,*args):pass

class QuoteBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/brave-browser-stable',headless=True,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close()
    def setUp(self):
        self.context=self.browser.new_context(reduced_motion='reduce')
        self.context.route('**/*',lambda r:r.continue_() if r.request.url.startswith(self.base) else r.abort())
        self.page=self.context.new_page();self.requests=[]
    def tearDown(self):self.context.close()
    def fill(self,path='index.html'):
        self.page.goto(f'{self.base}/{path}')
        form=self.page.locator('form.estimate-card,form.seo-short-form')
        for field in form.locator('input[required]').all():
            typ=field.get_attribute('type')
            if typ=='checkbox':field.check()
            else:field.fill('diagnostic@example.com' if typ=='email' else 'REGRESSION TEST — not a customer')
        return form
    def response(self,status=200,body=None):
        def respond(route):
            self.requests.append(route.request.post_data_json)
            route.fulfill(status=status,content_type='application/json',body=json.dumps(body if body is not None else {'success':True}))
        self.context.route(ENDPOINT,respond)
    def test_provider_500_preserves_details_on_page(self):
        from playwright.sync_api import expect
        self.response(500,{'success':False})
        form=self.fill();url=self.page.url;form.locator('button[type=submit]').click()
        expect(form.locator('[role=status]')).to_contain_text('could not')
        self.assertEqual(self.page.url,url)
        self.assertEqual(form.locator('[name=email]').input_value(),'diagnostic@example.com')
        expect(form.locator('button[type=submit]')).to_be_enabled()
    def test_every_form_can_submit_and_reach_the_success_page(self):
        self.response()
        for path,_ in quote_pages():
            with self.subTest(page=path):
                before=len(self.requests);form=self.fill(path)
                form.locator('button[type=submit]').click();self.page.wait_for_url('**/thank-you.html')
                self.assertEqual(len(self.requests),before+1)
                data=self.requests[-1]
                self.assertEqual(data['access_key'],KEY)
                self.assertEqual(data['email'],'diagnostic@example.com')
                self.assertNotIn('redirect',data)
                if path=='index.html':self.assertEqual(data['consent'],'Yes')
    def test_rejected_response_does_not_claim_success(self):
        from playwright.sync_api import expect
        self.response(200,{'success':False});form=self.fill('areas-we-serve/pewaukee.html')
        form.locator('button[type=submit]').click()
        expect(form.locator('[role=status]')).to_contain_text('could not')
        self.assertNotIn('thank-you',self.page.url)
    def test_network_error_preserves_entries(self):
        from playwright.sync_api import expect
        self.context.route(ENDPOINT,lambda route:route.abort());form=self.fill()
        form.locator('button[type=submit]').click()
        expect(form.locator('[role=status]')).to_contain_text('could not')
        expect(form.locator('button[type=submit]')).to_be_enabled()
        self.assertEqual(form.locator('[name=email]').input_value(),'diagnostic@example.com')
    def test_invalid_response_does_not_claim_success(self):
        from playwright.sync_api import expect
        self.context.route(ENDPOINT,lambda route:route.fulfill(status=200,content_type='text/html',body='<h1>500 server error</h1>'))
        form=self.fill();form.locator('button[type=submit]').click()
        expect(form.locator('[role=status]')).to_contain_text('could not')
        self.assertNotIn('thank-you',self.page.url)
    def test_required_fields_prevent_sending(self):
        self.response();self.page.goto(self.base+'/index.html')
        form=self.page.locator('form.estimate-card');form.locator('button[type=submit]').click()
        self.assertEqual(self.requests,[]);self.assertFalse(form.evaluate('f=>f.checkValidity()'))
    def test_duplicate_submissions_are_blocked_while_sending(self):
        from playwright.sync_api import expect
        self.page.add_init_script('window.fetch=()=>new Promise(()=>{})')
        form=self.fill();form.locator('button[type=submit]').click()
        expect(form.locator('button[type=submit]')).to_be_disabled()
        expect(form).to_have_attribute('aria-busy','true')
        expect(form.locator('[role=status]')).to_contain_text('Sending')
    def test_timeout_releases_button_and_preserves_entries(self):
        from playwright.sync_api import expect
        self.page.add_init_script('''const nativeTimeout=window.setTimeout;window.setTimeout=(f,t,...args)=>nativeTimeout(f,t===20000?25:t,...args);window.fetch=(url,opts)=>new Promise((resolve,reject)=>opts.signal.addEventListener('abort',()=>reject(new Error('timed out'))))''')
        form=self.fill();form.locator('button[type=submit]').click()
        expect(form.locator('[role=status]')).to_contain_text('could not')
        expect(form.locator('button[type=submit]')).to_be_enabled()
        self.assertEqual(form.locator('[name=email]').input_value(),'diagnostic@example.com')

if __name__=='__main__':unittest.main(verbosity=2)
