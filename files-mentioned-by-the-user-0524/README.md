# Waukesha Cleaning Pros Website

Static website for waukeshacleaningpros.com.

## Deploying to Cloudflare Pages

1. Create a new GitHub repository.
2. Push this folder to the repository.
3. In Cloudflare, open Workers & Pages > Pages > Create project > Connect to Git.
4. Select the repository.
5. Use these build settings:
   - Framework preset: None
   - Build command: leave blank
   - Build output directory: / or leave blank
6. Add custom domains:
   - waukeshacleaningpros.com
   - www.waukeshacleaningpros.com
7. In DNS, point the domain to Cloudflare Pages as instructed by Cloudflare.

## Important files

- index.html: homepage
- areas-we-serve.html: service-area hub
- areas-we-serve/: city pages
- industries-we-serve.html: industry hub
- industries-we-serve/: industry pages
- assets/: images and logo
- sitemap.xml: SEO sitemap
- robots.txt: crawler instructions
- _headers: Cloudflare Pages security/cache headers
- _redirects: redirects www to apex domain

## Video note

The landing page video is embedded from Vimeo to keep the GitHub/Cloudflare deploy lightweight.

## Form note

All 18 estimate and walkthrough forms use Web3Forms and deliver to
fernandojr@waukeshacleaningpros.com. The access key in the HTML is intentionally
public. Manage recipients in the Web3Forms dashboard for Waukesha Cleaning Pros.

JavaScript redirects to /thank-you.html only after a confirmed successful
submission. Server errors, rejected responses, network failures, and timeouts
preserve the customer's entries and show a retry/call message. Duplicate submits
are blocked while a request is pending. The native HTML form works without JS.

## Form regression tests

Install Python and Playwright; the tests currently launch Brave from
/usr/bin/brave-browser-stable. Run `python tests/test_quote_forms.py` from this
folder. Browser tests intercept provider requests; they do not send real emails.
The suite exercises all 18 forms plus success, failure, validation, pending-submit,
and timeout behavior.
