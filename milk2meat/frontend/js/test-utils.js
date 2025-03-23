/**
 * Shared test utilities for frontend tests
 */

/**
 * Creates a mock file with a given name and type
 * @param {string} name - The file name
 * @param {string} type - The MIME type
 * @param {string} content - The file content
 * @returns {File} - A mock File object
 */
export function createMockFile(name, type, content = "test content") {
  return new File([content], name, { type });
}

/**
 * Creates a mock fetch response
 * @param {object|string} data - The response data
 * @param {boolean} ok - Whether the response was successful
 * @param {number} status - The HTTP status code
 * @returns {object} - A mock Response object
 */
export function createMockResponse(data, ok = true, status = 200) {
  return {
    ok,
    status,
    json: jest.fn().mockResolvedValue(data),
    text: jest
      .fn()
      .mockResolvedValue(
        typeof data === "string" ? data : JSON.stringify(data),
      ),
  };
}

/**
 * Sets up a mock for the window.fetch function
 * @param {object|string} responseData - The data to return
 * @param {boolean} ok - Whether the response should be successful
 * @param {number} status - The HTTP status code
 * @returns {Function} - The mock fetch function
 */
export function mockFetch(responseData, ok = true, status = 200) {
  const mockResponse = createMockResponse(responseData, ok, status);
  return jest.fn().mockResolvedValue(mockResponse);
}

/**
 * Creates a mock for SweetAlert2
 * @param {boolean} isConfirmed - Whether the user confirmed the alert
 * @returns {object} - A mock Swal object
 */
export function mockSweetAlert(isConfirmed = true) {
  const mockSwalFire = jest.fn().mockResolvedValue({ isConfirmed });
  return {
    fire: mockSwalFire,
  };
}

/**
 * Creates a mock FormData instance
 * @returns {object} - A mock FormData object
 */
export function mockFormData() {
  const formDataEntries = {};

  return {
    append: jest.fn((key, value) => {
      formDataEntries[key] = value;
    }),
    get: jest.fn((key) => formDataEntries[key]),
    getAll: jest.fn((key) => [formDataEntries[key]]),
    has: jest.fn((key) =>
      Object.prototype.hasOwnProperty.call(formDataEntries, key),
    ),
    set: jest.fn((key, value) => {
      formDataEntries[key] = value;
    }),
    delete: jest.fn((key) => {
      delete formDataEntries[key];
    }),
    entries: jest.fn(() => Object.entries(formDataEntries)[Symbol.iterator]()),
    values: jest.fn(() => Object.values(formDataEntries)[Symbol.iterator]()),
    keys: jest.fn(() => Object.keys(formDataEntries)[Symbol.iterator]()),
    _entries: formDataEntries, // For test inspection
  };
}

/**
 * Simulates a keyboard event
 * @param {string} key - The key being pressed
 * @param {object} options - Additional options (ctrlKey, metaKey, etc)
 * @returns {KeyboardEvent} - A KeyboardEvent object
 */
export function simulateKeyEvent(key, options = {}) {
  return new KeyboardEvent("keydown", {
    key,
    bubbles: true,
    cancelable: true,
    ...options,
  });
}

/**
 * Simulates a mouse event
 * @param {HTMLElement} element - The element to trigger the event on
 * @param {string} eventType - The type of event (click, mousedown, etc)
 */
export function simulateMouseEvent(element, eventType) {
  const event = new MouseEvent(eventType, {
    bubbles: true,
    cancelable: true,
    view: window,
  });
  element.dispatchEvent(event);
}

/**
 * Simulates a drag and drop operation
 * @param {HTMLElement} dropTarget - The element to drop onto
 * @param {File[]} files - The files to drop
 */
export function simulateFileDrop(dropTarget, files) {
  // Simulate dragover
  const dragOverEvent = new Event("dragover", { bubbles: true });
  dragOverEvent.preventDefault = jest.fn();
  dropTarget.dispatchEvent(dragOverEvent);

  // Simulate drop
  const dropEvent = new Event("drop", { bubbles: true });
  dropEvent.preventDefault = jest.fn();
  dropEvent.dataTransfer = { files };

  dropTarget.dispatchEvent(dropEvent);
}

/**
 * Helper to setup common test DOM structures
 * @param {string} formHtml - The HTML for the form
 * @returns {object} - An object with references to common elements
 */
export function setupTestDOM(formHtml) {
  document.body.innerHTML = formHtml;

  return {
    form: document.querySelector("form"),
    submitButton: document.querySelector("[type='submit']"),
  };
}

/**
 * Mocks a simple editor instance (EasyMDE)
 * @returns {object} - A mock editor object
 */
export function mockEditor() {
  return {
    codemirror: {
      save: jest.fn(),
    },
  };
}
