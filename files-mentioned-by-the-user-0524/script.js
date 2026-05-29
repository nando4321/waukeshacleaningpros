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
