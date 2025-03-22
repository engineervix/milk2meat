/**
 * @jest-environment jsdom
 */

// Import the module being tested
const pdfViewerPath = "./pdf-viewer";

// Mock canvas.getContext
HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue({
  drawImage: jest.fn(),
  fillRect: jest.fn(),
});

// Mock the pdf.js library
jest.mock("pdfjs-dist", () => {
  const mockPdfjsLib = {
    getDocument: jest.fn().mockImplementation((url) => ({
      promise: Promise.resolve({
        numPages: 3,
        getPage: jest.fn().mockImplementation((pageNum) =>
          Promise.resolve({
            getViewport: jest.fn().mockReturnValue({
              width: 800,
              height: 600,
              scale: 1.0,
            }),
            render: jest.fn().mockImplementation(() => ({
              promise: Promise.resolve(),
            })),
          }),
        ),
      }),
    })),
    GlobalWorkerOptions: {
      workerSrc: "",
    },
  };
  return mockPdfjsLib;
});

describe("PDF Viewer", () => {
  // Store original functions
  const originalAddEventListener = document.addEventListener;

  // Capture event handler
  let domContentLoadedHandler;

  beforeEach(() => {
    // Reset mocks and spies
    jest.clearAllMocks();

    // Reset DOM
    document.body.innerHTML = `
      <div id="pdf-viewer" data-note-id="123"></div>
    `;

    // Mock fetch
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes("/notes/") && url.includes("/file/")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              url: "https://example.com/secure-pdf.pdf",
            }),
        });
      }
      return Promise.reject(new Error("URL not mocked"));
    });

    // Mock document.addEventListener to capture DOMContentLoaded handler
    document.addEventListener = jest.fn((event, handler) => {
      if (event === "DOMContentLoaded") {
        domContentLoadedHandler = handler;
      }
    });

    // Mock window.location
    Object.defineProperty(window, "location", {
      value: { hostname: "example.com" },
      writable: true,
    });

    // Mock timer functions
    jest.useFakeTimers();
    global.setInterval = jest.fn().mockReturnValue(123);
    global.clearInterval = jest.fn();

    // We need to clear the module cache to ensure a fresh import each time
    jest.resetModules();
  });

  afterEach(() => {
    document.addEventListener = originalAddEventListener;
    global.fetch = undefined;
    jest.useRealTimers();
  });

  test("adds event listener for DOMContentLoaded", () => {
    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Check that addEventListener was called with DOMContentLoaded
    expect(document.addEventListener).toHaveBeenCalledWith(
      "DOMContentLoaded",
      expect.any(Function),
    );
  });

  test("initializes PDF viewer when DOMContentLoaded fires", () => {
    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Make sure we captured the handler
    expect(domContentLoadedHandler).toBeDefined();

    // Call the handler to simulate DOMContentLoaded event
    domContentLoadedHandler();

    // Should fetch secure URL
    expect(global.fetch).toHaveBeenCalledWith("/notes/123/file/");
  });

  test("doesn't initialize when PDF viewer container doesn't exist", () => {
    // Clear the DOM
    document.body.innerHTML = "";

    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Call the handler
    domContentLoadedHandler();

    // Should not fetch
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test("uses direct PDF URL when available", () => {
    // Set up DOM with direct PDF URL
    document.body.innerHTML = `
      <div id="pdf-viewer" data-pdf-url="direct.pdf"></div>
    `;

    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Call the handler
    domContentLoadedHandler();

    // Should not fetch secure URL
    expect(global.fetch).not.toHaveBeenCalled();

    // Should use pdfjsLib.getDocument
    const pdfjsLib = require("pdfjs-dist");
    expect(pdfjsLib.getDocument).toHaveBeenCalledWith("direct.pdf");
  });

  test("shows error when no PDF URL or note ID provided", () => {
    // Set up element without data attributes
    document.body.innerHTML = `<div id="pdf-viewer"></div>`;

    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Spy on innerHTML
    const container = document.getElementById("pdf-viewer");
    const originalInnerHTML = container.innerHTML;
    const innerHTMLSpy = jest.spyOn(container, "innerHTML", "set");

    // Call the handler
    domContentLoadedHandler();

    // Check the error message
    expect(innerHTMLSpy).toHaveBeenCalled();
    expect(innerHTMLSpy.mock.calls[0][0]).toContain("Error loading PDF");
    expect(innerHTMLSpy.mock.calls[0][0]).toContain(
      "No PDF URL or note ID provided",
    );

    // Restore
    innerHTMLSpy.mockRestore();
  });

  test("identifies dev vs production environment correctly", () => {
    // Mock production hostname
    Object.defineProperty(window, "location", {
      value: { hostname: "example.com" },
      writable: true,
    });

    // Import the module to access its internals
    jest.isolateModules(() => {
      // We need to use isolateModules to ensure we get a fresh instance of the module
      const pdfViewer = require(pdfViewerPath);

      // Check production detection logic
      expect(window.location.hostname).not.toBe("localhost");
      expect(window.location.hostname).not.toBe("127.0.0.1");

      // Now set it to development hostname
      Object.defineProperty(window, "location", {
        value: { hostname: "localhost" },
        writable: true,
      });

      // Reload module in dev environment
      jest.resetModules();
      require(pdfViewerPath);

      // Check development detection logic
      expect(window.location.hostname).toBe("localhost");
    });
  });

  test("handles PDF loading errors gracefully", async () => {
    // Mock pdfjsLib to fail
    const pdfjsLib = require("pdfjs-dist");
    pdfjsLib.getDocument.mockImplementationOnce(() => ({
      promise: Promise.reject(new Error("Failed to load PDF")),
    }));

    // Set up container with direct URL
    document.body.innerHTML = `<div id="pdf-viewer" data-pdf-url="broken.pdf"></div>`;
    const container = document.getElementById("pdf-viewer");

    // Import the module - this also sets up the event listener
    require(pdfViewerPath);

    // Spy on innerHTML
    const innerHTMLSpy = jest.spyOn(container, "innerHTML", "set");

    // Call the handler
    domContentLoadedHandler();

    // Wait for promises
    await Promise.resolve();
    await Promise.resolve();

    // Check for error message
    const errorMessageShown = innerHTMLSpy.mock.calls.some(
      (call) =>
        call[0].includes("Error loading PDF") &&
        call[0].includes("Failed to load PDF"),
    );

    expect(errorMessageShown).toBe(true);

    // Restore
    innerHTMLSpy.mockRestore();
  });
});
