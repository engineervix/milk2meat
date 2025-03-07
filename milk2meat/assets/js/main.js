import "../css/main.css";
import "@phosphor-icons/web/regular";

// Dark mode functionality
document.addEventListener("DOMContentLoaded", () => {
  const darkModeToggle = document.getElementById("dark-mode-toggle");

  // Check for saved theme preference or use system preference
  const savedTheme =
    localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light");

  // Apply saved theme on page load
  if (savedTheme === "dark") {
    document.documentElement.classList.add("dark");
    if (darkModeToggle) darkModeToggle.checked = true;
  }

  // Toggle event
  if (darkModeToggle) {
    darkModeToggle.addEventListener("change", () => {
      if (darkModeToggle.checked) {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      } else {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      }
    });
  }
});
