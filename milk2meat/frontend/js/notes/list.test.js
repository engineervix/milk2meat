/**
 * Tests for notes list functionality
 * @jest-environment jsdom
 */

import "@testing-library/jest-dom";

// Mock URL and Location API
const mockURLSearchParams = {
  toString: jest.fn(() => "mock-params"),
  delete: jest.fn(),
  set: jest.fn(),
};

const mockURL = {
  pathname: "/notes/",
  search: "",
  searchParams: mockURLSearchParams,
};

// Mock global functions before importing module
global.URL = jest.fn(() => mockURL);
global.URLSearchParams = jest.fn(() => mockURLSearchParams);

// Store original location
const originalLocation = window.location;

// Mock and restore window.location
beforeAll(() => {
  delete window.location;
  window.location = { href: "http://localhost/notes/" };
});

afterAll(() => {
  window.location = originalLocation;
});

// Mock the applyFilter function - we need to test it directly
let applyFilter;

// Override the global DOMContentLoaded handler to capture the applyFilter function
const originalAddEventListener = document.addEventListener;
document.addEventListener = jest.fn((event, handler) => {
  if (event === "DOMContentLoaded") {
    // Store the handler but don't execute it yet
    document._domContentLoadedHandler = handler;
  }
  return originalAddEventListener.apply(document, [event, handler]);
});

// Import module after setting up mocks
const listModule = require("../notes/list");

// Grab the applyFilter function directly from the module
if (listModule && typeof listModule.applyFilter === "function") {
  applyFilter = listModule.applyFilter;
} else {
  // Extract applyFilter from the script (fallback approach)
  const executeScript = () => {
    document._domContentLoadedHandler();
    applyFilter = window.applyFilter;
  };

  executeScript();
}

describe("Notes List Module", () => {
  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = `
      <div>
        <select id="note-type-filter"></select>
        <select id="book-filter"></select>
        <div class="dropdown">
          <div class="dropdown-content">
            <div class="form-control">
              <label class="cursor-pointer label">
                <input type="checkbox" class="tag-checkbox" data-tag-name="prayer" />
              </label>
            </div>
            <div class="form-control">
              <label class="cursor-pointer label">
                <input type="checkbox" class="tag-checkbox" data-tag-name="study" />
              </label>
            </div>
          </div>
        </div>
      </div>
    `;

    // Reset mocks
    mockURLSearchParams.delete.mockClear();
    mockURLSearchParams.set.mockClear();
    mockURLSearchParams.toString.mockClear();
    global.URL.mockClear();

    // Reset window.location.href
    window.location.href = "http://localhost/notes/";

    // Execute the DOMContentLoaded handler to initialize everything
    if (document._domContentLoadedHandler) {
      document._domContentLoadedHandler();
    }
  });

  describe("applyFilter function", () => {
    test("should set filter parameter and update URL", () => {
      // Call the function directly instead of through window
      applyFilter("type", "sermon");

      // Check URL constructor call with current location
      expect(global.URL).toHaveBeenCalledWith("http://localhost/notes/");

      // Verify parameter modifications
      expect(mockURLSearchParams.delete).toHaveBeenCalledWith("page");
      expect(mockURLSearchParams.set).toHaveBeenCalledWith("type", "sermon");

      // Verify URL was updated with the correct format
      expect(window.location.href).toBe("/notes/?mock-params");
    });

    test("should remove filter parameter when value is empty", () => {
      applyFilter("book", "");

      expect(mockURLSearchParams.delete).toHaveBeenCalledWith("page");
      expect(mockURLSearchParams.delete).toHaveBeenCalledWith("book");
    });
  });

  describe("Tag checkbox functionality", () => {
    test("should initialize tag checkboxes on page load", () => {
      const checkboxes = document.querySelectorAll(".tag-checkbox");
      expect(checkboxes.length).toBe(2);

      // Simulate checking the first checkbox
      const firstCheckbox = checkboxes[0];
      firstCheckbox.checked = true;
      firstCheckbox.dispatchEvent(new Event("change"));

      // First checkbox should stay checked
      expect(firstCheckbox.checked).toBe(true);
      // Second checkbox should be unchecked
      expect(checkboxes[1].checked).toBe(false);

      // Should have applied the tag filter
      expect(mockURLSearchParams.set).toHaveBeenCalledWith("tag", "prayer");
    });

    test("should uncheck previous checkbox when selecting a new one", () => {
      const checkboxes = document.querySelectorAll(".tag-checkbox");

      // Check first checkbox
      checkboxes[0].checked = true;
      checkboxes[0].dispatchEvent(new Event("change"));

      // Then check second checkbox
      checkboxes[1].checked = true;
      checkboxes[1].dispatchEvent(new Event("change"));

      // First should now be unchecked
      expect(checkboxes[0].checked).toBe(false);
      expect(checkboxes[1].checked).toBe(true);

      // Should have applied new tag filter
      expect(mockURLSearchParams.set).toHaveBeenCalledWith("tag", "study");
    });

    test("should clear tag filter when unchecking a checkbox", () => {
      const checkbox = document.querySelector(".tag-checkbox");

      // First check it
      checkbox.checked = true;
      checkbox.dispatchEvent(new Event("change"));

      // Then uncheck it
      checkbox.checked = false;
      checkbox.dispatchEvent(new Event("change"));

      // Should have cleared the tag filter
      expect(mockURLSearchParams.delete).toHaveBeenCalledWith("tag");
    });
  });
});
