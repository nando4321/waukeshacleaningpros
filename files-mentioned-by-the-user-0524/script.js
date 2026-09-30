const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector(".site-nav");
const menuLinks = document.querySelectorAll(".site-nav a");
const year = document.querySelector("#year");
const calculator = document.querySelector("#impact-calculator");
const frequency = document.querySelector("#frequency");
const frequencyOutput = document.querySelector("#frequency-output");
const sickDays = document.querySelector("#sick-days");
const productivity = document.querySelector("#productivity");

if (year) {
  year.textContent = new Date().getFullYear();
}

function closeMenu() {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute("aria-expanded", "false");
  navigation.classList.remove("is-open");
  document.body.classList.remove("menu-open");
}

if (menuButton && navigation) {
  menuButton.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    navigation.classList.toggle("is-open", !isOpen);
    document.body.classList.toggle("menu-open", !isOpen);
  });
}

menuLinks.forEach((link) => {
  link.addEventListener("click", closeMenu);
});

window.addEventListener("resize", () => {
  if (window.innerWidth > 980) {
    closeMenu();
  }
});

function updateFrequency() {
  if (!frequency || !frequencyOutput) return;
  frequencyOutput.textContent = frequency.value;
}

function calculateImpact(event) {
  event.preventDefault();
  const employees = Number(document.querySelector("#employees")?.value || 0);
  const days = Number(frequency?.value || 1);
  const reduction = Math.round(employees * days * 0.18);
  const gain = reduction * 385;

  if (sickDays) sickDays.textContent = String(reduction);
  if (productivity) productivity.textContent = `$${gain.toLocaleString()}`;
}

if (frequency) {
  frequency.addEventListener("input", updateFrequency);
  updateFrequency();
}

if (calculator) {
  calculator.addEventListener("submit", calculateImpact);
}

// ---------- Quote submission (native HTML remains a no-JS fallback) ----------
  document.querySelectorAll('form.estimate-card, form.seo-short-form').forEach(function (form) {
    if (!window.fetch || !window.FormData || !window.AbortController) return;
    var button = form.querySelector('button[type="submit"]');
    var originalText = button.textContent;
    var busy = false;
    var status = document.createElement('p');
    status.className = 'form-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    form.appendChild(status);

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (busy || !form.reportValidity()) return;
      var data = new FormData(form);
      var payload = {};
      data.forEach(function (value, key) { payload[key] = value; });
      // Redirect ourselves only after a confirmed API success, never on failure.
      delete payload.redirect;
      if (payload.botcheck) return;
      busy = true;
      button.disabled = true;
      button.textContent = 'Sending…';
      form.setAttribute('aria-busy', 'true');
      status.textContent = 'Sending your quote request…';
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 20000);

      fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      }).then(function (response) {
        if (!response.ok) throw new Error('Submission service unavailable');
        return response.json();
      }).then(function (result) {
        if (result.success !== true) throw new Error('Submission was not accepted');
        status.textContent = 'Your quote request was sent successfully.';
        window.location.assign('/thank-you.html');
      }).catch(function () {
        status.textContent = 'We could not confirm that your request was sent. Your details are still here. Please try again, or call (414) 367-7289.';
      }).finally(function () {
        clearTimeout(timer);
        busy = false;
        button.disabled = false;
        button.textContent = originalText;
        form.removeAttribute('aria-busy');
      });
    });
  });
