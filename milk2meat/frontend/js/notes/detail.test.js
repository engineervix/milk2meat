/**
 * Tests for notes detail functionality
 * @jest-environment jsdom
 */

import "@testing-library/jest-dom";

// Mock fetch API
global.fetch = jest.fn();

// Setup mock fetch success response
const mockFetchSuccess = () => {
  global.fetch.mockImplementation(() =>
    Promise.resolve({
      json: () => Promise.resolve({ url: "https://example.com/secure-url" }),
    }),
  );
};

// Setup mock fetch error response
const mockFetchError = () => {
  global.fetch.mockImplementation(() =>
    Promise.resolve({
      json: () => Promise.resolve({ error: "Access denied" }),
    }),
  );
};

// Mock window.open
global.open = jest.fn();

// Mock window.alert
global.alert = jest.fn();

// Capture the confirmDelete function
let confirmDelete;

// Override the global DOMContentLoaded handler to capture functions
const originalAddEventListener = document.addEventListener;
document.addEventListener = jest.fn((event, handler) => {
  if (event === "DOMContentLoaded") {
    // Store the handler but don't execute it yet
    document._domContentLoadedHandler = handler;
  }
  return originalAddEventListener.apply(document, [event, handler]);
});

describe("Notes Detail Module", () => {
  beforeEach(() => {
    // Reset mocks
    global.fetch.mockClear();
    global.open.mockClear();
    global.alert.mockClear();

    // Reset window.confirmDelete
    delete window.confirmDelete;

    // Reset DOM
    document.body.innerHTML = `
      <div data-note-id="123">
        <a href="#" data-download>Download File</a>
        <button onclick="confirmDelete()">Delete</button>
        <dialog id="delete-modal">
          <div class="modal-content">
            <h3>Delete Confirmation</h3>
            <div class="modal-actions">
              <button>Cancel</button>
              <button>Delete</button>
            </div>
          </div>
        </dialog>
      </div>
    `;

    // Import module after DOM setup to catch event listeners
    jest.resetModules();
    const detailModule = require("../notes/detail");

    // Execute the DOMContentLoaded handler to initialize everything
    if (document._domContentLoadedHandler) {
      document._domContentLoadedHandler();
    }

    // Get the confirmDelete function
    if (detailModule && typeof detailModule.confirmDelete === "function") {
      confirmDelete = detailModule.confirmDelete;
    } else {
      confirmDelete = window.confirmDelete;
    }
  });

  describe("Secure File Download", () => {
    test("should fetch secure URL and open in new tab", async () => {
      mockFetchSuccess();

      // Trigger download click
      const downloadLink = document.querySelector("[data-download]");
      downloadLink.click();

      // Check fetch was called with correct URL
      expect(global.fetch).toHaveBeenCalledWith("/notes/123/file/");

      // Wait for promise to resolve
      await new Promise(process.nextTick);

      // Check window.open was called with secure URL
      expect(global.open).toHaveBeenCalledWith(
        "https://example.com/secure-url",
        "_blank",
      );

      // Alert should not be called
      expect(global.alert).not.toHaveBeenCalled();
    });

    test("should show error alert when fetch returns error", async () => {
      mockFetchError();

      // Trigger download click
      const downloadLink = document.querySelector("[data-download]");
      downloadLink.click();

      // Check fetch was called
      expect(global.fetch).toHaveBeenCalled();

      // Wait for promise to resolve
      await new Promise(process.nextTick);

      // Check alert was shown with error
      expect(global.alert).toHaveBeenCalledWith(
        "Error accessing file: Access denied",
      );

      // Window.open should not be called
      expect(global.open).not.toHaveBeenCalled();
    });

    test("should handle case when note ID is not found", () => {
      // Remove note ID from DOM
      document.querySelector("[data-note-id]").removeAttribute("data-note-id");

      // Trigger download click
      const downloadLink = document.querySelector("[data-download]");
      downloadLink.click();

      // Fetch should not be called
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test("should handle network error", async () => {
      // Make fetch reject
      global.fetch.mockImplementation(() => Promise.reject("Network error"));

      // Trigger download click
      const downloadLink = document.querySelector("[data-download]");
      downloadLink.click();

      // Wait for promise to reject
      await new Promise(process.nextTick);

      // Should show error alert
      expect(global.alert).toHaveBeenCalledWith(
        "Network error while accessing file",
      );
    });
  });

  describe("Delete Confirmation", () => {
    test("should show delete confirmation modal", () => {
      // Spy on dialog showModal method
      const modal = document.getElementById("delete-modal");
      modal.showModal = jest.fn();

      // Call confirmDelete directly
      confirmDelete();

      // Check if modal was shown
      expect(modal.showModal).toHaveBeenCalled();
    });

    test("should handle missing modal gracefully", () => {
      // Remove modal from DOM
      document.getElementById("delete-modal").remove();

      // This should not throw an error
      expect(() => {
        confirmDelete();
      }).not.toThrow();
    });
  });
});
