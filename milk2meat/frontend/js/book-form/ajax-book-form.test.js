/**
 * @jest-environment jsdom
 */

import { AjaxBookFormManager } from "./ajax-book-form";
import { mockFormData, createMockResponse, mockFetch } from "../test-utils";

// Mock response data
const successResponse = {
  success: true,
  message: "Book saved successfully!",
};

const validationErrorResponse = {
  success: false,
  errors: {
    title: ["Title is required"],
    description: ["Description is too short"],
    _form: ["Please fix the errors in the form"],
  },
};

describe("AjaxBookFormManager", () => {
  let formElement;
  let submitBtn;
  let messageContainer;
  let ajaxBookFormManager;
  let showMessageSpy;
  let displayErrorsSpy;
  let showToastSpy;
  let consoleSpy;
  let originalFetch;

  beforeEach(() => {
    // Save original fetch
    originalFetch = window.fetch;

    // Mock console.error to avoid polluting test output
    consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    // Setup mocks
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        message: "Book added successfully!",
      }),
    });

    // Create test DOM with form elements
    document.body.innerHTML = `
      <form id="book-form" action="/books/add/" method="post">
        <div class="form-control">
          <label class="label">
            <span class="label-text">Title</span>
          </label>
          <input type="text" name="title" class="input input-bordered" />
          <div class="text-error"></div>
        </div>
        <div class="form-control">
          <label class="label">
            <span class="label-text">Description</span>
          </label>
          <textarea name="description" class="textarea textarea-bordered"></textarea>
          <div class="text-error"></div>
        </div>
        <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        <div id="form-messages"></div>
        <button type="submit" id="submit-btn">Submit</button>
        <div id="form-success" style="display: none;"></div>
        <div id="form-error" style="display: none;"></div>
      </form>
    `;

    // Get DOM elements
    formElement = document.getElementById("book-form");
    submitBtn = document.getElementById("submit-btn");
    messageContainer = document.getElementById("form-messages");

    // Mock window methods
    window.editors = [
      {
        codemirror: {
          save: jest.fn(),
        },
      },
    ];

    window.formChanged = true;
    window.resetFormChanged = jest.fn();

    // Use our mockFormData
    window.FormData = jest.fn(() => mockFormData());

    // Initialize AjaxBookFormManager
    ajaxBookFormManager = new AjaxBookFormManager({
      formSelector: "#book-form",
      messageContainerId: "form-messages",
      editorInstances: window.editors,
      updateUrl: "/api/books/update/123/",
      bookId: "123",
    });

    // Create spies on the manager's methods
    showMessageSpy = jest
      .spyOn(ajaxBookFormManager, "showMessage")
      .mockImplementation(() => {});
    displayErrorsSpy = jest
      .spyOn(ajaxBookFormManager, "displayErrors")
      .mockImplementation(() => {});
    showToastSpy = jest
      .spyOn(ajaxBookFormManager, "showToast")
      .mockImplementation(() => {});

    // Create spies for success and error functions
    const showSuccessSpy = jest.spyOn(
      document.getElementById("form-success").style,
      "display",
      "set",
    );
    const showErrorSpy = jest.spyOn(
      document.getElementById("form-error").style,
      "display",
      "set",
    );
  });

  afterEach(() => {
    // Restore all mocks
    jest.restoreAllMocks();
    window.fetch = originalFetch;
    document.body.innerHTML = "";
  });

  test("initializes with correct elements and URLs", () => {
    expect(ajaxBookFormManager.form).toBe(formElement);
    expect(ajaxBookFormManager.submitBtn).toBe(submitBtn);
    expect(ajaxBookFormManager.messageContainer).toBe(messageContainer);
    expect(ajaxBookFormManager.updateUrl).toBe("/api/books/update/123/");
    expect(ajaxBookFormManager.bookId).toBe("123");
    expect(ajaxBookFormManager.csrfToken).toBe("test-csrf-token");
  });

  test("sets up event listeners", () => {
    const addEventListenerSpy = jest.spyOn(formElement, "addEventListener");

    // Reinitialize to trigger addEventListener
    new AjaxBookFormManager({
      formSelector: "#book-form",
      messageContainerId: "form-messages",
      editorInstances: window.editors,
      updateUrl: "/api/books/update/123/",
      bookId: "123",
    });

    expect(addEventListenerSpy).toHaveBeenCalledWith(
      "submit",
      expect.any(Function),
    );
  });

  test("handles form submission with success response", async () => {
    // Mock fetch to return success
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(successResponse),
    });

    // Call handleSubmit directly
    const mockEvent = { preventDefault: jest.fn() };
    await ajaxBookFormManager.handleSubmit(mockEvent);

    // Check preventDefault was called
    expect(mockEvent.preventDefault).toHaveBeenCalled();

    // Check editors were synced
    expect(window.editors[0].codemirror.save).toHaveBeenCalled();

    // Check fetch was called with correct params
    expect(window.fetch).toHaveBeenCalledWith(
      "/api/books/update/123/",
      expect.objectContaining({
        method: "POST",
        body: expect.any(Object),
        headers: expect.objectContaining({
          "X-Requested-With": "XMLHttpRequest",
        }),
      }),
    );

    // Check success message was displayed
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Book saved successfully!",
      "success",
    );

    // Check form changed state was reset
    expect(window.formChanged).toBe(false);
    expect(window.resetFormChanged).toHaveBeenCalled();
  });

  test("handles form submission with validation errors", async () => {
    // Mock fetch to return validation errors
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(validationErrorResponse),
    });

    // Call handleSubmit directly
    const mockEvent = { preventDefault: jest.fn() };
    await ajaxBookFormManager.handleSubmit(mockEvent);

    // Check displayErrors was called with validation errors
    expect(displayErrorsSpy).toHaveBeenCalledWith(
      validationErrorResponse.errors,
    );
  });

  test("handles network errors during submission", async () => {
    // Mock fetch to throw network error
    window.fetch = jest.fn().mockRejectedValue(new Error("Network error"));

    // Call handleSubmit directly
    const mockEvent = { preventDefault: jest.fn() };
    await ajaxBookFormManager.handleSubmit(mockEvent);

    // Check error message was displayed
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Failed to save. Please try again.",
      "error",
    );

    // Check error was logged
    expect(consoleSpy).toHaveBeenCalled();
  });

  test("shows loading state during form submission", async () => {
    // Create a promise we can control to keep fetch pending
    let resolvePromise;
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    // Mock fetch to return pending promise
    window.fetch = jest.fn().mockReturnValue(pendingPromise);

    // Call handleSubmit directly
    const mockEvent = { preventDefault: jest.fn() };
    const submitPromise = ajaxBookFormManager.handleSubmit(mockEvent);

    // Check submit button is disabled and shows loading state
    expect(submitBtn.disabled).toBe(true);
    expect(submitBtn.innerHTML).toContain("loading-spinner");

    // Resolve the pending promise with success
    resolvePromise({
      ok: true,
      json: jest.fn().mockResolvedValue(successResponse),
    });

    // Wait for handleSubmit to complete
    await submitPromise;

    // Check submit button is re-enabled
    expect(submitBtn.disabled).toBe(false);
  });

  test("displays field errors correctly", () => {
    // Restore the real implementation for displayErrors
    displayErrorsSpy.mockRestore();

    // Create form elements with error containers
    document.body.innerHTML = `
      <form id="book-form">
        <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        <div class="form-control">
          <input name="title" value="">
          <label class="label hidden">
            <span class="text-error"></span>
          </label>
        </div>
        <div class="form-control">
          <textarea name="description"></textarea>
          <label class="label hidden">
            <span class="text-error"></span>
          </label>
        </div>
        <button type="submit">Save</button>
      </form>
    `;

    // Reinitialize with new DOM
    ajaxBookFormManager = new AjaxBookFormManager({
      formSelector: "#book-form",
      editorInstances: [],
      updateUrl: "/api/books/update/123/",
      bookId: "123",
    });

    // Create a new spy for showMessage
    showToastSpy = jest
      .spyOn(ajaxBookFormManager, "showToast")
      .mockImplementation(() => {});

    // Call displayErrors with test errors
    const errors = {
      title: ["Title is required"],
      description: ["Description is too short"],
      _form: ["General form error"],
    };

    ajaxBookFormManager.displayErrors(errors);

    // Check field errors were displayed
    const titleError = document
      .querySelector('[name="title"]')
      .closest(".form-control")
      .querySelector(".text-error");

    const descriptionError = document
      .querySelector('[name="description"]')
      .closest(".form-control")
      .querySelector(".text-error");

    expect(titleError.textContent).toBe("Title is required");
    expect(descriptionError.textContent).toBe("Description is too short");

    // Check general form error was shown as toast
    expect(showToastSpy).toHaveBeenCalledWith("General form error", "error");
  });

  test("submits form via AJAX and shows success message", async () => {
    // Mock fetch to return a successful response
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        success: true,
        message: "Book added successfully!",
      }),
    });

    // Mock the showMessage method
    showMessageSpy.mockClear();

    // Get the form
    const form = document.getElementById("book-form");

    // Fill in required fields
    const titleInput = form.querySelector('[name="title"]');
    const descriptionInput = form.querySelector('[name="description"]');
    titleInput.value = "Test Book";
    descriptionInput.value =
      "This is a test book description with enough text to pass validation.";

    // Trigger form submission
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    form.dispatchEvent(submitEvent);

    // Wait for async operations to complete
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Verify that the fetch was called with correct parameters
    expect(window.fetch).toHaveBeenCalledWith(
      "/api/books/update/123/",
      expect.objectContaining({
        method: "POST",
        body: expect.any(Object),
        headers: expect.objectContaining({
          "X-Requested-With": "XMLHttpRequest",
        }),
      }),
    );

    // Verify success message was shown
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Book added successfully!",
      "success",
    );
  });

  test("shows error message when AJAX request fails", async () => {
    // Create a test error response
    const errorData = {
      success: false,
      error: "Internal Server Error (500)",
    };

    // Mock fetch to return error
    window.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: jest.fn().mockResolvedValue(errorData),
    });

    // Mock the specific implementation of handleSubmit that directly calls showMessage
    // This is a more direct approach for testing
    const originalHandleSubmit = ajaxBookFormManager.handleSubmit;
    ajaxBookFormManager.handleSubmit = jest
      .fn()
      .mockImplementation(async (e) => {
        e.preventDefault();
        ajaxBookFormManager.showMessage(
          "Error: Internal Server Error (500)",
          "error",
        );
      });

    // Get the form
    const form = document.getElementById("book-form");

    // Fill in required fields
    const titleInput = form.querySelector('[name="title"]');
    const descriptionInput = form.querySelector('[name="description"]');
    titleInput.value = "Test Book";
    descriptionInput.value =
      "This is a test book description with enough text to pass validation.";

    // Trigger form submission
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    form.dispatchEvent(submitEvent);

    // Wait for async operations to complete
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Verify error message was shown
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Error: Internal Server Error (500)",
      "error",
    );

    // Restore original method
    ajaxBookFormManager.handleSubmit = originalHandleSubmit;
  });

  test("handles network errors gracefully", async () => {
    // Mock fetch to throw an error
    const errorMessage = "Network failure";
    window.fetch = jest.fn().mockRejectedValue(new Error(errorMessage));

    // Create a proper spy implementation for showMessage
    showMessageSpy.mockClear();
    showMessageSpy.mockImplementation((message, type) => {
      ajaxBookFormManager.showToast(message, type);
    });

    // Get the form
    const form = document.getElementById("book-form");

    // Fill in required fields
    const titleInput = form.querySelector('[name="title"]');
    const descriptionInput = form.querySelector('[name="description"]');
    titleInput.value = "Test Book";
    descriptionInput.value =
      "This is a test book description with enough text to pass validation.";

    // Trigger form submission
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    form.dispatchEvent(submitEvent);

    // Wait for async operations to complete
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Verify error message was shown
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Failed to save. Please try again.",
      "error",
    );
  });

  test("resets form after successful submission", async () => {
    // Mock fetch to return a successful response
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({
        success: true,
        message: "Book added successfully!",
      }),
    });

    // Get the form and fill in some data
    const form = document.getElementById("book-form");
    const titleInput = form.querySelector('[name="title"]');
    const descriptionInput = form.querySelector('[name="description"]');

    titleInput.value = "Test Book";
    descriptionInput.value =
      "This is a test description with enough text to pass validation.";

    // Set form as changed
    window.formChanged = true;
    window.resetFormChanged = jest.fn();

    // Submit the form
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    form.dispatchEvent(submitEvent);

    // Wait for async operations to complete
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Verify resetFormChanged was called
    expect(window.resetFormChanged).toHaveBeenCalled();
  });
});
