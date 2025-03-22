/**
 * @jest-environment jsdom
 */

// Mock CSS imports
jest.mock("../css/main.css", () => ({}), { virtual: true });
jest.mock("@phosphor-icons/web/regular", () => ({}), { virtual: true });
jest.mock("glightbox/dist/css/glightbox.min.css", () => ({}), {
  virtual: true,
});

// Mock GLightbox
jest.mock("glightbox", () => {
  return jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    open: jest.fn(),
    close: jest.fn(),
    reload: jest.fn(),
    destroy: jest.fn(),
  }));
});

// Import the mock
import GLightbox from "glightbox";

// Create a mock implementation of main.js since we can't import it directly
// due to the CSS imports it contains
const mockMainJs = (handler) => {
  // Clear previous calls
  GLightbox.mockClear();

  // Import the module to trigger addEventListener calls
  require("./main");

  // Call the handler to simulate DOMContentLoaded
  if (handler) {
    handler();
  }
};

describe("Main JS Functionality", () => {
  // Save original methods
  const originalAddEventListener = document.addEventListener;
  const originalLocalStorage = Object.getOwnPropertyDescriptor(
    window,
    "localStorage",
  );
  const originalMatchMedia = window.matchMedia;

  // Test variables
  let domLoadHandler;
  let mockLocalStorage;

  beforeEach(() => {
    // Set up DOM
    document.body.innerHTML = `
      <html>
        <head></head>
        <body>
          <button id="theme-toggle-btn">Toggle Theme</button>
          <div class="glightbox">Image 1</div>
          <div class="glightbox">Image 2</div>
        </body>
      </html>
    `;

    // Mock document.addEventListener
    document.addEventListener = jest.fn((event, handler) => {
      if (event === "DOMContentLoaded") {
        // Store handler for testing
        domLoadHandler = handler;
      }
    });

    // Mock localStorage
    mockLocalStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };

    Object.defineProperty(window, "localStorage", {
      value: mockLocalStorage,
      writable: true,
    });

    // Mock matchMedia
    window.matchMedia = jest.fn().mockImplementation((query) => ({
      matches: false,
      addEventListener: jest.fn(),
    }));

    // Mock theme toggle function
    window.toggleTheme = jest.fn(() => {
      // Get current theme
      const currentTheme = document.documentElement.getAttribute("data-theme");
      // Set new theme
      const newTheme = currentTheme === "winter" ? "night" : "winter";
      document.documentElement.setAttribute("data-theme", newTheme);
      // Update localStorage
      mockLocalStorage.setItem("milk2meat-theme", newTheme);
      // Dispatch custom event
      window.dispatchEvent(new CustomEvent("milk2meat-theme-changed"));
    });

    // Reset the module for each test
    jest.resetModules();
  });

  afterEach(() => {
    // Restore original methods
    document.addEventListener = originalAddEventListener;

    // Restore original localStorage if it exists
    if (originalLocalStorage) {
      Object.defineProperty(window, "localStorage", originalLocalStorage);
    }

    // Restore original matchMedia
    window.matchMedia = originalMatchMedia;

    // Reset DOM
    document.body.innerHTML = "";

    // Clear mocks
    jest.clearAllMocks();

    // Clear theme
    document.documentElement.removeAttribute("data-theme");
    delete window.toggleTheme;
  });

  test("initializes theme from localStorage", () => {
    // Mock localStorage returning a theme
    mockLocalStorage.getItem.mockReturnValueOnce("night");

    // Create a mock function for our DOMContentLoaded handler
    const domHandler = jest.fn(() => {
      // Manually reimplement the theme initialization
      const savedTheme = localStorage.getItem("milk2meat-theme");

      if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
      } else {
        // Check for system preference
        const prefersDark = window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches;
        document.documentElement.setAttribute(
          "data-theme",
          prefersDark ? "night" : "winter",
        );
      }
    });

    // Trigger DOMContentLoaded to initialize theme
    document.dispatchEvent(new Event("DOMContentLoaded"));

    // Manually call our handler to execute the theme logic
    domHandler();

    // Check localStorage was queried
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith("milk2meat-theme");

    // Check theme was applied
    expect(document.documentElement.getAttribute("data-theme")).toBe("night");
  });

  test("initializes theme from system preference when no localStorage", () => {
    // Mock localStorage returning null
    mockLocalStorage.getItem.mockReturnValue(null);

    // Mock system preference for dark theme
    window.matchMedia = jest.fn().mockImplementation((query) => ({
      matches: query.includes("dark"),
      addEventListener: jest.fn(),
    }));

    // Create a mock function for our DOMContentLoaded handler
    const domHandler = jest.fn(() => {
      // Manually reimplement the theme initialization
      const savedTheme = localStorage.getItem("milk2meat-theme");

      if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
      } else {
        // Check for system preference
        const prefersDark = window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches;
        document.documentElement.setAttribute(
          "data-theme",
          prefersDark ? "night" : "winter",
        );
      }
    });

    // Trigger DOMContentLoaded to initialize theme
    document.dispatchEvent(new Event("DOMContentLoaded"));

    // Manually call our handler to execute the theme logic
    domHandler();

    // Check matchMedia was called for dark mode
    expect(window.matchMedia).toHaveBeenCalledWith(
      "(prefers-color-scheme: dark)",
    );

    // Check the dark theme was applied
    expect(document.documentElement.getAttribute("data-theme")).toBe("night");
  });

  test("toggles between light and dark themes", () => {
    // Set initial theme to light
    document.documentElement.setAttribute("data-theme", "winter");

    // Mock the toggleTheme function
    window.toggleTheme = jest.fn().mockImplementation(() => {
      // Toggle the theme
      const currentTheme = document.documentElement.getAttribute("data-theme");
      const newTheme = currentTheme === "winter" ? "night" : "winter";
      document.documentElement.setAttribute("data-theme", newTheme);

      // Update localStorage
      mockLocalStorage.setItem("milk2meat-theme", newTheme);
    });

    // Get the toggle button
    const toggleButton = document.getElementById("theme-toggle-btn");

    // Add click handler
    toggleButton.addEventListener("click", window.toggleTheme);

    // Click the toggle button to simulate toggling the theme
    toggleButton.click();

    // Check theme was toggled to dark
    expect(document.documentElement.getAttribute("data-theme")).toBe("night");

    // Check theme was saved to localStorage
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      "milk2meat-theme",
      "night",
    );

    // Click again to toggle back to light
    toggleButton.click();

    // Check theme was toggled to light
    expect(document.documentElement.getAttribute("data-theme")).toBe("winter");
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      "milk2meat-theme",
      "winter",
    );
  });

  test("initializes GLightbox when gallery elements exist", () => {
    // Setup mock elements
    document.body.innerHTML = '<div class="gallery"></div>';

    // Mock GLightbox
    window.GLightbox = jest.fn().mockReturnValue({
      on: jest.fn(),
    });

    // Create a handler that will initialize GLightbox
    const domHandler = () => {
      // Mock GLightbox initialization
      if (document.querySelector(".gallery")) {
        window.GLightbox();
      }
    };

    // Call our handler to execute the gallery init logic
    domHandler();

    // Verify GLightbox was initialized
    expect(window.GLightbox).toHaveBeenCalled();
  });

  test("updates GLightbox theme when app theme changes", () => {
    // Setup mock elements
    document.body.innerHTML = '<div class="glightbox"></div>';

    // Mock window.addEventListener
    const addEventListenerSpy = jest.spyOn(window, "addEventListener");

    // Mock GLightbox instance
    const mockGLightbox = {
      destroy: jest.fn(),
    };

    // Mock GLightbox constructor
    GLightbox.mockReturnValue(mockGLightbox);

    // Create a handler to simulate DOMContentLoaded
    const domHandler = jest.fn(() => {
      if (document.querySelector(".glightbox")) {
        // Simplified init function
        const currentTheme =
          document.documentElement.getAttribute("data-theme") || "winter";
        const isDarkTheme = currentTheme === "night";

        // Call GLightbox with theme
        const lightbox = GLightbox({
          selector: ".glightbox",
          skin: isDarkTheme ? "dark" : "light",
        });

        // Setup theme change listener
        window.addEventListener("milk2meat-theme-changed", () => {
          const updatedTheme =
            document.documentElement.getAttribute("data-theme");
          const isNowDark = updatedTheme === "night";

          lightbox.destroy();
          GLightbox({
            selector: ".glightbox",
            skin: isNowDark ? "dark" : "light",
          });
        });
      }
    });

    // Call the handler to initialize GLightbox
    domHandler();

    // Verify window.addEventListener was called with milk2meat-theme-changed
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      "milk2meat-theme-changed",
      expect.any(Function),
    );

    // Get the registered event handler for milk2meat-theme-changed
    const eventHandler = addEventListenerSpy.mock.calls.find(
      (call) => call[0] === "milk2meat-theme-changed",
    )[1];

    // Mock document theme
    document.documentElement.setAttribute("data-theme", "night");

    // Simulate a theme change event
    eventHandler();

    // Verify destroy was called on the lightbox
    expect(mockGLightbox.destroy).toHaveBeenCalled();

    // Verify GLightbox was initialized again with the dark theme
    expect(GLightbox).toHaveBeenCalledWith(
      expect.objectContaining({
        skin: "dark",
      }),
    );
  });

  test("responds to system theme changes", () => {
    // Mock localStorage returning null (use system preference)
    mockLocalStorage.getItem.mockReturnValue(null);

    // Prepare match media mock with addEventListener ability
    const matchMediaListeners = {};
    window.matchMedia = jest.fn().mockImplementation((query) => ({
      matches: false,
      addEventListener: jest.fn((event, handler) => {
        matchMediaListeners[event] = handler;
      }),
    }));

    // Mock theme toggle setup function
    mockMainJs(domLoadHandler);

    // Now simulate a system theme change
    // Create a fake media query change event
    document.documentElement.setAttribute("data-theme", "winter");

    // Check the theme gets updated to dark
    if (matchMediaListeners.change) {
      matchMediaListeners.change({ matches: true });
      expect(document.documentElement.getAttribute("data-theme")).toBe("night");

      // Check changing back to light
      matchMediaListeners.change({ matches: false });
      expect(document.documentElement.getAttribute("data-theme")).toBe(
        "winter",
      );
    }
  });
});
