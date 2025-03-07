import "../css/main.css";
import "@phosphor-icons/web/regular";

// Dark mode functionality
document.addEventListener("DOMContentLoaded", () => {
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  const htmlElement = document.documentElement;

  // Check for saved theme preference or use system preference
  const savedTheme =
    localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light");

  // Apply saved theme on page load
  if (savedTheme === "dark") {
    htmlElement.classList.add("dark");
    if (darkModeToggle) darkModeToggle.checked = true;
  }

  // Toggle event
  if (darkModeToggle) {
    darkModeToggle.addEventListener("change", () => {
      if (darkModeToggle.checked) {
        htmlElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      } else {
        htmlElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      }
    });
  }

  // Handle system preference changes
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (e) => {
      if (!localStorage.getItem("theme")) {
        if (e.matches) {
          htmlElement.classList.add("dark");
          if (darkModeToggle) darkModeToggle.checked = true;
        } else {
          htmlElement.classList.remove("dark");
          if (darkModeToggle) darkModeToggle.checked = false;
        }
      }
    });
});
