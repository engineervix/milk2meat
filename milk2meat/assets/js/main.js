import "../css/main.css";
import "@phosphor-icons/web/regular";

// Theme management
document.addEventListener("DOMContentLoaded", () => {
  // Theme toggle functionality
  const themeToggleBtn = document.getElementById("theme-toggle-btn");

  // Function to set theme and update localStorage
  const setTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("milk2meat-theme", theme);
  };

  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem("milk2meat-theme");

    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Check for system preference
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches;
      setTheme(prefersDark ? "dark" : "emerald");
    }
  };

  // Toggle between themes
  const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "emerald" ? "dark" : "emerald";
    setTheme(newTheme);
  };

  // Initialize theme on page load
  initializeTheme();

  // Add event listener to theme toggle button
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", toggleTheme);
  }

  // Listen for system theme changes
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (e) => {
      if (!localStorage.getItem("milk2meat-theme")) {
        setTheme(e.matches ? "dark" : "emerald");
      }
    });
});
