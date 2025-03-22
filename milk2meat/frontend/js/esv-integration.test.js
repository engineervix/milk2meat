/**
 * @jest-environment jsdom
 */

describe("ESV Integration", () => {
  // Save original window properties
  const originalDispatchEvent = window.dispatchEvent;
  const originalAddEventListener = window.addEventListener;

  beforeEach(() => {
    // Reset the DOM
    document.documentElement.innerHTML = "<html></html>";

    // Mock window methods
    window.dispatchEvent = jest.fn();
    window.addEventListener = jest.fn();

    // Reset the ESV options before each test
    window.ESV_CROSSREF_OPTIONS = undefined;

    // Reset the module cache to ensure a fresh load each time
    jest.resetModules();
  });

  afterEach(() => {
    // Restore original window methods
    window.dispatchEvent = originalDispatchEvent;
    window.addEventListener = originalAddEventListener;

    // Clean up event listeners
    jest.restoreAllMocks();
  });

  test("sets ESV options on DOM load with light theme", () => {
    // Set the theme to light (default)
    document.documentElement.setAttribute("data-theme", "light");

    // Set up DOMContentLoaded handler first
    const eventMap = {};
    document.addEventListener = jest.fn((event, handler) => {
      eventMap[event] = handler;
    });

    // Import the module to execute the code
    require("./esv-integration");

    // Manually trigger the DOMContentLoaded handler
    eventMap.DOMContentLoaded();

    // Check that ESV options are set correctly for light theme
    expect(window.ESV_CROSSREF_OPTIONS).toBeDefined();
    expect(window.ESV_CROSSREF_OPTIONS.header_background_color).toBe("F0F0F0");
    expect(window.ESV_CROSSREF_OPTIONS.body_background_color).toBe("F0F0F0");
    expect(window.ESV_CROSSREF_OPTIONS.body_font_color).toBe("000000");
  });

  test("sets ESV options on DOM load with dark theme", () => {
    // Set the theme to dark
    document.documentElement.setAttribute("data-theme", "night");

    // Set up DOMContentLoaded handler first
    const eventMap = {};
    document.addEventListener = jest.fn((event, handler) => {
      eventMap[event] = handler;
    });

    // Import the module to execute the code
    require("./esv-integration");

    // Manually trigger the DOMContentLoaded handler
    eventMap.DOMContentLoaded();

    // Check that ESV options are set correctly for dark theme
    expect(window.ESV_CROSSREF_OPTIONS).toBeDefined();
    expect(window.ESV_CROSSREF_OPTIONS.header_background_color).toBe("333333");
    expect(window.ESV_CROSSREF_OPTIONS.body_background_color).toBe("222222");
    expect(window.ESV_CROSSREF_OPTIONS.body_font_color).toBe("FFFFFF");
  });

  test("updates ESV options when theme changes", () => {
    // Set the theme to light
    document.documentElement.setAttribute("data-theme", "light");

    // Set up event handlers
    const windowEventMap = {};
    window.addEventListener = jest.fn((event, handler) => {
      windowEventMap[event] = handler;
    });

    const documentEventMap = {};
    document.addEventListener = jest.fn((event, handler) => {
      documentEventMap[event] = handler;
    });

    // Load the module (which sets up event listeners)
    require("./esv-integration");

    // Trigger DOMContentLoaded to initialize
    documentEventMap.DOMContentLoaded();

    // Verify theme change listener was set up
    expect(windowEventMap["milk2meat-theme-changed"]).toBeDefined();

    // Change to dark theme
    document.documentElement.setAttribute("data-theme", "night");

    // Manually call the theme change listener
    windowEventMap["milk2meat-theme-changed"]();

    // Verify ESV options were updated for dark theme
    expect(window.ESV_CROSSREF_OPTIONS.body_background_color).toBe("222222");

    // Verify the re-linking was triggered
    expect(window.dispatchEvent).toHaveBeenCalled();
    expect(window.dispatchEvent.mock.calls[0][0].type).toBe(
      "esv-crossref.trigger-linkify",
    );
  });
});
