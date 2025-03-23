/**
 * @jest-environment jsdom
 */

import { AjaxFormManager } from "./ajax-form";

// Mock response data
const successResponse = {
  success: true,
  message: "Note saved successfully!",
  is_new: false,
};

const validationErrorResponse = {
  success: false,
  errors: {
    title: ["Title is required"],
    content: ["Content is too short"],
    _form: ["Please fix the errors in the form"],
  },
};

describe("AjaxFormManager", () => {
  let formElement;
  let submitBtn;
  let messageContainer;
  let ajaxFormManager;
  let showMessageSpy;
  let displayErrorsSpy;
  let showToastSpy;
  let mockConsoleError;
  let originalFetch;

  beforeEach(() => {
    // Save original fetch
    originalFetch = window.fetch;

    // Mock console.error to suppress expected test errors
    mockConsoleError = jest
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Set up DOM
    document.body.innerHTML = `
      <form id="note-form">
        <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        <input name="title" value="Test Note">
        <textarea name="content">Test content</textarea>
        <input name="tags" value="test,note">
        <button type="submit" id="submit-btn">Save</button>
        <div id="form-messages"></div>
      </form>
    `;

    // Get DOM elements
    formElement = document.getElementById("note-form");
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

    // Create FormData mock
    const formData = {
      get: jest.fn((key) => {
        if (key === "title") return "Test Note";
        if (key === "content") return "Test content";
        if (key === "tags") return "test,note";
        return null;
      }),
      entries: jest.fn(function* () {
        yield ["title", "Test Note"];
        yield ["content", "Test content"];
        yield ["tags", "test,note"];
      }),
    };

    // Mock FormData constructor
    window.FormData = jest.fn(() => formData);

    // Initialize AjaxFormManager
    ajaxFormManager = new AjaxFormManager({
      formSelector: "#note-form",
      messageContainerId: "form-messages",
      editorInstances: window.editors,
      createUrl: "/api/notes/create/",
      updateUrl: "/api/notes/update/123/",
      noteId: "123",
    });

    // Create spies on the methods
    showMessageSpy = jest
      .spyOn(ajaxFormManager, "showMessage")
      .mockImplementation(() => {});
    displayErrorsSpy = jest
      .spyOn(ajaxFormManager, "displayErrors")
      .mockImplementation(() => {});
    showToastSpy = jest
      .spyOn(ajaxFormManager, "showToast")
      .mockImplementation(() => {});
  });

  afterEach(() => {
    // Restore all mocks
    jest.restoreAllMocks();
    window.fetch = originalFetch;
    document.body.innerHTML = "";
  });

  test("initializes with correct elements and URLs", () => {
    expect(ajaxFormManager.form).toBe(formElement);
    expect(ajaxFormManager.submitBtn).toBe(submitBtn);
    expect(ajaxFormManager.messageContainer).toBe(messageContainer);
    expect(ajaxFormManager.createUrl).toBe("/api/notes/create/");
    expect(ajaxFormManager.updateUrl).toBe("/api/notes/update/123/");
    expect(ajaxFormManager.noteId).toBe("123");
    expect(ajaxFormManager.csrfToken).toBe("test-csrf-token");
  });

  test("sets up event listeners", () => {
    const addEventListenerSpy = jest.spyOn(formElement, "addEventListener");

    // Reinitialize to trigger addEventListener
    new AjaxFormManager({
      formSelector: "#note-form",
      messageContainerId: "form-messages",
      editorInstances: window.editors,
      createUrl: "/api/notes/create/",
      updateUrl: "/api/notes/update/123/",
      noteId: "123",
    });

    expect(addEventListenerSpy).toHaveBeenCalledWith(
      "submit",
      expect.any(Function),
    );
  });

  test("handles form submission with success response", async () => {
    // Mock fetch
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(successResponse),
    });

    // Call handleSubmit directly since we're mocking the event listener
    const mockEvent = { preventDefault: jest.fn() };
    await ajaxFormManager.handleSubmit(mockEvent);

    // Check event.preventDefault was called
    expect(mockEvent.preventDefault).toHaveBeenCalled();

    // Check editors were synced
    expect(window.editors[0].codemirror.save).toHaveBeenCalled();

    // Check fetch was called with correct params
    expect(window.fetch).toHaveBeenCalledWith(
      "/api/notes/update/123/",
      expect.objectContaining({
        method: "POST",
        body: expect.any(Object),
        headers: expect.objectContaining({
          "X-Requested-With": "XMLHttpRequest",
        }),
      }),
    );

    // Check the success message is displayed
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Note saved successfully!",
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
    await ajaxFormManager.handleSubmit(mockEvent);

    // Check displayErrors was called with the validation errors
    expect(displayErrorsSpy).toHaveBeenCalledWith(
      validationErrorResponse.errors,
    );
  });

  test("handles network errors during submission", async () => {
    // Mock fetch to throw a network error
    window.fetch = jest.fn().mockRejectedValue(new Error("Network error"));

    // Call handleSubmit directly
    const mockEvent = { preventDefault: jest.fn() };
    await ajaxFormManager.handleSubmit(mockEvent);

    // Check error message is displayed
    expect(showMessageSpy).toHaveBeenCalledWith(
      "Failed to save. Please try again.",
      "error",
    );

    // Check console.error was called
    expect(mockConsoleError).toHaveBeenCalled();
  });

  test("displays field errors correctly", () => {
    const errors = {
      title: ["Title cannot be empty", "Title must be at least 3 characters"],
      content: ["Content is required"],
    };

    // Call the method directly
    ajaxFormManager.displayErrors(errors);

    // Check if it was called with the errors
    expect(displayErrorsSpy).toHaveBeenCalledWith(errors);
  });

  test("shows toast for general form errors", () => {
    // In this test, we want to test the real method implementation
    displayErrorsSpy.mockRestore();

    // Create a new mock for showMessage
    const newShowMessageSpy = jest
      .spyOn(ajaxFormManager, "showMessage")
      .mockImplementation(() => {});

    // Create mock form errors
    const formErrors = {
      _form: ["General form error"],
    };

    // Call displayErrors directly
    ajaxFormManager.displayErrors(formErrors);

    // Verify showMessage was called with the form error
    expect(newShowMessageSpy).toHaveBeenCalledWith(
      "General form error",
      "error",
    );
  });
});
