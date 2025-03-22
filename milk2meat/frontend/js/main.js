import "../css/main.css";
import "@phosphor-icons/web/regular";
import GLightbox from "glightbox";
import "glightbox/dist/css/glightbox.min.css";
import Swal from "sweetalert2";

// Make SweetAlert2 available globally
window.Swal = Swal;

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
      setTheme(prefersDark ? "night" : "winter");
    }
  };

  // Toggle between themes
  const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "winter" ? "night" : "winter";
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
        setTheme(e.matches ? "night" : "winter");
      }
    });

  // Initialize GLightbox for images
  const initGLightbox = () => {
    // Get current theme to set appropriate GLightbox theme
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const isDarkTheme = currentTheme === "night";

    // Initialize lightbox for note attachments
    const lightbox = GLightbox({
      selector: ".glightbox",
      touchNavigation: true,
      loop: false,
      autoplayVideos: false,
      skin: isDarkTheme ? "dark" : "light",
      cssEfects: {
        fade: { in: "fadeIn", out: "fadeOut" },
      },
      onOpen: () => {
        // Pause any video/audio when lightbox opens
        document.querySelectorAll("video, audio").forEach((media) => {
          if (!media.paused) media.pause();
        });
      },
    });

    // Listen for theme changes to update GLightbox theme
    window.addEventListener("milk2meat-theme-changed", () => {
      const updatedTheme = document.documentElement.getAttribute("data-theme");
      const isNowDark = updatedTheme === "night";

      // Close and reinitialize with new theme
      lightbox.destroy();
      GLightbox({
        selector: ".glightbox",
        touchNavigation: true,
        loop: false,
        autoplayVideos: false,
        skin: isNowDark ? "dark" : "light",
      });
    });

    return lightbox;
  };

  // Initialize GLightbox if there are gallery elements on the page
  if (document.querySelector(".glightbox")) {
    initGLightbox();
  }

  // Add custom event for theme changes to update GLightbox
  const originalToggleTheme = toggleTheme;
  window.toggleTheme = () => {
    originalToggleTheme();
    // Dispatch custom event for theme change
    window.dispatchEvent(new CustomEvent("milk2meat-theme-changed"));
  };
});
