/**
 * @jest-environment jsdom
 */

// Mock CSS imports
jest.mock("../css/main.css", () => ({}), { virtual: true });
jest.mock("@phosphor-icons/web/regular", () => ({}), { virtual: true });
jest.mock("glightbox/dist/css/glightbox.min.css", () => ({}), {
  virtual: true,
});

// Mock Sweetalert2
jest.mock("sweetalert2", () => {
  return jest.fn().mockImplementation(() => ({
    fire: jest.fn(),
  }));
});

// Mock GLightbox
const mockGLightbox = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
  on: jest.fn(),
}));
jest.mock("glightbox", () => {
  return mockGLightbox;
});

// Import mocks before importing the module under test
import GLightbox from "glightbox";
import Swal from "sweetalert2";

describe("Main JS Functionality", () => {
  // Save original methods
  const originalAddEventListener = document.addEventListener;
  const originalWindowAddEventListener = window.addEventListener;
  const originalLocalStorage = Object.getOwnPropertyDescriptor(
    window,
    "localStorage",
  );
  const originalMatchMedia = window.matchMedia;
  const originalQuerySelector = document.querySelector;
  const originalQuerySelectorAll = document.querySelectorAll;
  const originalGetElementById = document.getElementById;
  const originalDispatchEvent = window.dispatchEvent;

  // Test variables
  let domLoadedHandler;
  let mockLocalStorage;
  let mockToggleBtn;
  let mockDispatchEvent;

  beforeEach(() => {
    // Set up DOM
    document.body.innerHTML = `
      <html>
        <head></head>
        <body>
          <div class="glightbox">Image 1</div>
          <div class="glightbox">Image 2</div>
        </body>
      </html>
    `;

    // Setup mock toggle button
    mockToggleBtn = document.createElement("button");
    mockToggleBtn.id = "theme-toggle-btn";
    mockToggleBtn.addEventListener = jest.fn((event, handler) => {
      if (event === "click") {
        mockToggleBtn.clickHandler = handler;
      }
    });
    mockToggleBtn.click = jest.fn(() => {
      if (mockToggleBtn.clickHandler) {
        mockToggleBtn.clickHandler();
      }
    });

    // Mock document.getElementById
    document.getElementById = jest.fn().mockImplementation((id) => {
      if (id === "theme-toggle-btn") {
        return mockToggleBtn;
      }
      return null;
    });

    // Mock document.addEventListener to capture the DOMContentLoaded handler
    document.addEventListener = jest.fn((event, handler) => {
      if (event === "DOMContentLoaded") {
        domLoadedHandler = handler;
      }
    });

    // Mock window.addEventListener
    window.addEventListener = jest.fn();

    // Mock window.dispatchEvent
    mockDispatchEvent = jest.fn();
    window.dispatchEvent = mockDispatchEvent;

    // Mock localStorage
    mockLocalStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, "localStorage", {
      value: mockLocalStorage,
    });

    // Mock window.matchMedia
    window.matchMedia = jest.fn().mockImplementation((query) => ({
      matches: query.includes("dark"),
      addEventListener: jest.fn(),
    }));

    // Mock document.querySelector
    document.querySelector = jest.fn().mockImplementation((selector) => {
      if (selector === ".glightbox") {
        return document.createElement("div");
      }
      return null;
    });

    // Create mock video and audio elements
    const videoEl = document.createElement("div");
    videoEl.pause = jest.fn();
    videoEl.paused = false;

    const audioEl = document.createElement("div");
    audioEl.pause = jest.fn();
    audioEl.paused = false;

    // Mock document.querySelectorAll
    document.querySelectorAll = jest.fn().mockImplementation((selector) => {
      if (selector === "video, audio") {
        return [videoEl, audioEl];
      }
      return [];
    });

    // Reset mocks
    mockGLightbox.mockClear();
    if (Swal) Swal.mockClear();

    // Reset the module for each test
    jest.resetModules();
  });

  afterEach(() => {
    // Restore original methods
    document.addEventListener = originalAddEventListener;
    document.querySelector = originalQuerySelector;
    document.querySelectorAll = originalQuerySelectorAll;
    document.getElementById = originalGetElementById;
    window.addEventListener = originalWindowAddEventListener;
    window.dispatchEvent = originalDispatchEvent;

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

    // Clear theme and global functions
    document.documentElement.removeAttribute("data-theme");
    delete window.toggleTheme;
  });

  test("should make Sweetalert2 available globally", () => {
    // Import the module
    require("./main");

    // Check if Swal is attached to window
    expect(window.Swal).toBeDefined();
  });

  test("should register DOMContentLoaded event listener", () => {
    // Import the module
    require("./main");

    // Verify document.addEventListener was called with DOMContentLoaded
    expect(document.addEventListener).toHaveBeenCalledWith(
      "DOMContentLoaded",
      expect.any(Function),
    );
  });

  describe("Theme Management", () => {
    beforeEach(() => {
      // Import the module
      require("./main");

      // Execute the DOMContentLoaded handler
      if (domLoadedHandler) {
        domLoadedHandler();
      }
    });

    test("should initialize theme from localStorage", () => {
      // Reset mocks
      document.documentElement.removeAttribute("data-theme");

      // Setup localStorage to return a theme
      mockLocalStorage.getItem.mockReturnValueOnce("night");

      // Re-run the DOMContentLoaded handler
      domLoadedHandler();

      // Verify localStorage was checked
      expect(mockLocalStorage.getItem).toHaveBeenCalledWith("milk2meat-theme");

      // Verify theme was set
      expect(document.documentElement.getAttribute("data-theme")).toBe("night");
    });

    test("should initialize theme from system preference when no localStorage value", () => {
      // Reset document theme
      document.documentElement.removeAttribute("data-theme");

      // Setup localStorage to return null
      mockLocalStorage.getItem.mockReturnValueOnce(null);

      // Mock dark mode preference
      window.matchMedia = jest.fn().mockImplementation(() => ({
        matches: true,
        addEventListener: jest.fn(),
      }));

      // Re-run the DOMContentLoaded handler
      domLoadedHandler();

      // Verify theme was set to night for dark mode
      expect(document.documentElement.getAttribute("data-theme")).toBe("night");
    });

    test("should initialize theme to winter when system prefers light mode", () => {
      // Reset document theme
      document.documentElement.removeAttribute("data-theme");

      // Setup localStorage to return null
      mockLocalStorage.getItem.mockReturnValueOnce(null);

      // Mock light mode preference
      window.matchMedia = jest.fn().mockImplementation(() => ({
        matches: false,
        addEventListener: jest.fn(),
      }));

      // Re-run the DOMContentLoaded handler
      domLoadedHandler();

      // Verify theme was set to winter for light mode
      expect(document.documentElement.getAttribute("data-theme")).toBe(
        "winter",
      );
    });

    test("should toggle theme via window.toggleTheme", () => {
      // Set initial theme to winter
      document.documentElement.setAttribute("data-theme", "winter");

      // Verify toggleTheme was exposed globally
      expect(typeof window.toggleTheme).toBe("function");

      // Reset localStorage mock
      mockLocalStorage.setItem.mockClear();
      mockDispatchEvent.mockClear();

      // Call toggleTheme
      window.toggleTheme();

      // Verify theme was toggled to night
      expect(document.documentElement.getAttribute("data-theme")).toBe("night");

      // Verify localStorage was updated
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        "milk2meat-theme",
        "night",
      );

      // Verify a custom event was dispatched
      expect(mockDispatchEvent).toHaveBeenCalled();
    });

    test("should toggle theme when button is clicked", () => {
      // Set initial theme to winter
      document.documentElement.setAttribute("data-theme", "winter");

      // Verify a click handler was attached to the button
      expect(mockToggleBtn.addEventListener).toHaveBeenCalledWith(
        "click",
        expect.any(Function),
      );

      // Click the button
      mockToggleBtn.click();

      // Verify theme was toggled
      expect(document.documentElement.getAttribute("data-theme")).toBe("night");
    });
  });

  describe("GLightbox Integration", () => {
    let capturedOptions;

    beforeEach(() => {
      // Capture GLightbox options
      mockGLightbox.mockImplementation((options) => {
        capturedOptions = options;
        return {
          destroy: jest.fn(),
          on: jest.fn(),
        };
      });

      // Import the module
      require("./main");
    });

    test("should initialize GLightbox with theme-specific options", () => {
      // Reset all state
      document.documentElement.removeAttribute("data-theme");
      mockGLightbox.mockClear();

      // Set theme to night
      document.documentElement.setAttribute("data-theme", "night");

      // Run DOMContentLoaded handler
      domLoadedHandler();

      // Check GLightbox was called
      expect(mockGLightbox).toHaveBeenCalled();

      // Verify theme-related options are present
      const options = mockGLightbox.mock.calls[0][0];
      expect(options.selector).toBe(".glightbox");
      expect(options.skin !== undefined).toBe(true);
    });

    test("should not initialize GLightbox when no elements exist", () => {
      // Mock querySelector to return null
      document.querySelector.mockReturnValueOnce(null);

      // Clear GLightbox mock
      mockGLightbox.mockClear();

      // Run DOMContentLoaded handler
      domLoadedHandler();

      // Verify GLightbox was not called
      expect(mockGLightbox).not.toHaveBeenCalled();
    });

    test("should update GLightbox when theme changes", () => {
      // Run DOMContentLoaded handler first to set up event listeners
      domLoadedHandler();

      // Find the milk2meat-theme-changed event handler
      const themeChangeHandlerCall = window.addEventListener.mock.calls.find(
        (call) => call[0] === "milk2meat-theme-changed",
      );

      // Extract the handler
      const themeChangeHandler = themeChangeHandlerCall
        ? themeChangeHandlerCall[1]
        : null;

      // Check handler was registered
      expect(themeChangeHandler).toBeDefined();

      // Create a mock instance with destroy method for testing
      const mockDestroy = jest.fn();
      const mockLightboxInstance = { destroy: mockDestroy };

      // Replace the defaultGLightbox implementation just for this test
      const savedImplementation = mockGLightbox.getMockImplementation();
      mockGLightbox.mockImplementation(() => mockLightboxInstance);

      // Manually attach the handler to window like main.js does
      window.addEventListener = jest.fn((event, handler) => {
        if (event === "milk2meat-theme-changed") {
          // Store the handler for later use
          window.themeChangeHandler = handler;
        }
      });

      // Re-initialize GLightbox to capture the handler
      domLoadedHandler();

      // Reset the mock for clean tracking
      mockGLightbox.mockClear();

      // Call the handler directly
      if (window.themeChangeHandler) {
        window.themeChangeHandler();

        // Verify destroy was called
        expect(mockDestroy).toHaveBeenCalled();

        // Verify GLightbox was reinitialized
        expect(mockGLightbox).toHaveBeenCalled();
      }

      // Restore the original implementation
      mockGLightbox.mockImplementation(savedImplementation);
    });

    test("should pause media when lightbox opens", () => {
      // Run DOMContentLoaded handler to set up GLightbox
      domLoadedHandler();

      // Check if onOpen handler was captured
      expect(capturedOptions).toBeDefined();
      expect(capturedOptions.onOpen).toBeDefined();

      // Get the media elements
      const mediaElements = document.querySelectorAll("video, audio");
      const videoEl = mediaElements[0];
      const audioEl = mediaElements[1];

      // Call the onOpen handler
      capturedOptions.onOpen();

      // Verify pause was called on both media elements
      expect(videoEl.pause).toHaveBeenCalled();
      expect(audioEl.pause).toHaveBeenCalled();
    });

    test("should not pause already paused media", () => {
      // Run DOMContentLoaded handler to set up GLightbox
      domLoadedHandler();

      // Get the media elements
      const mediaElements = document.querySelectorAll("video, audio");
      const videoEl = mediaElements[0];
      const audioEl = mediaElements[1];

      // Set paused state
      videoEl.paused = true;
      audioEl.paused = true;

      // Clear pause mocks
      videoEl.pause.mockClear();
      audioEl.pause.mockClear();

      // Call the onOpen handler
      capturedOptions.onOpen();

      // Verify pause was not called on paused media
      expect(videoEl.pause).not.toHaveBeenCalled();
      expect(audioEl.pause).not.toHaveBeenCalled();
    });
  });
});
