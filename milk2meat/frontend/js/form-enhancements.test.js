/**
 * @jest-environment jsdom
 */

import { FormEnhancer } from "./form-enhancements";

describe("FormEnhancer", () => {
  // Set up spies for global objects
  let consoleSpy;

  beforeEach(() => {
    // Reset the document body before each test
    document.body.innerHTML = `
      <form id="test-form">
        <button type="submit" id="submit-btn">Submit</button>
        <button type="button" id="cancel-edit-btn">Cancel</button>
      </form>
    `;

    // Set up console spy
    consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

    // Mock window.editors if needed
    window.editors = [
      {
        codemirror: {
          save: jest.fn(),
        },
      },
    ];
  });

  afterEach(() => {
    // Clean up
    document.body.innerHTML = "";
    jest.clearAllMocks();

    // Remove any dynamically added elements or styles
    const addedStyles = document.querySelectorAll("style");
    addedStyles.forEach((style) => {
      if (style.textContent.includes(".fab")) {
        style.remove();
      }
    });
  });

  test("initializes with default options", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
    });

    expect(formEnhancer.form).toBeTruthy();
    expect(formEnhancer.submitButton).toBeTruthy();
    expect(formEnhancer.cancelButton).toBeTruthy();
  });

  test("logs error when form is not found", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#non-existent-form",
    });

    expect(consoleSpy).toHaveBeenCalledWith("Form or submit button not found");
  });

  test("creates floating action button with correct position", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
      fabPosition: "bottom-right",
    });

    const fab = document.querySelector(".fab");
    expect(fab).toBeTruthy();
    expect(fab.style.bottom).toBe("2rem");
    expect(fab.style.right).toBe("2rem");
  });

  test("creates floating action button with bottom-center position", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
      fabPosition: "bottom-center",
    });

    const fab = document.querySelector(".fab");
    expect(fab).toBeTruthy();
    expect(fab.style.bottom).toBe("2rem");
    expect(fab.style.left).toBe("50%");
  });

  test("creates floating action button with bottom-left position", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
      fabPosition: "bottom-left",
    });

    const fab = document.querySelector(".fab");
    expect(fab).toBeTruthy();
    expect(fab.style.bottom).toBe("2rem");
    expect(fab.style.left).toBe("2rem");
  });

  test("clicking the FAB triggers form submission", () => {
    // Set up a mock for the submit button
    const submitBtn = document.querySelector("#submit-btn");
    submitBtn.click = jest.fn();

    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
    });

    // Find FAB and click it
    const fab = document.querySelector(".fab");
    fab.click();

    // Verify submit button was clicked
    expect(submitBtn.click).toHaveBeenCalled();
  });

  test("keyboard shortcut (Ctrl+S) triggers form submission", () => {
    // Set up a mock for the submit button
    const submitBtn = document.querySelector("#submit-btn");
    submitBtn.click = jest.fn();

    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
    });

    // Simulate Ctrl+S keyboard event
    const event = new KeyboardEvent("keydown", {
      key: "s",
      ctrlKey: true,
      bubbles: true,
    });
    document.dispatchEvent(event);

    // Verify submit button was clicked
    expect(submitBtn.click).toHaveBeenCalled();
  });

  test("keyboard shortcut (Cmd+S) triggers form submission", () => {
    // Set up a mock for the submit button
    const submitBtn = document.querySelector("#submit-btn");
    submitBtn.click = jest.fn();

    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
    });

    // Simulate Cmd+S keyboard event (Mac)
    const event = new KeyboardEvent("keydown", {
      key: "s",
      metaKey: true,
      bubbles: true,
    });
    document.dispatchEvent(event);

    // Verify submit button was clicked
    expect(submitBtn.click).toHaveBeenCalled();
  });

  test("saveForm syncs editors before submission", () => {
    // Set up a mock for the submit button
    const submitBtn = document.querySelector("#submit-btn");
    submitBtn.click = jest.fn();

    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
    });

    // Call saveForm directly
    formEnhancer.saveForm();

    // Check if editor was synced
    expect(window.editors[0].codemirror.save).toHaveBeenCalled();
    // And submit button was clicked
    expect(submitBtn.click).toHaveBeenCalled();
  });

  test("doesn't enable keyboard shortcuts when disabled", () => {
    // Set up a mock for the submit button
    const submitBtn = document.querySelector("#submit-btn");
    submitBtn.click = jest.fn();

    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
      enableKeyboardShortcuts: false,
    });

    // Simulate Ctrl+S keyboard event
    const event = new KeyboardEvent("keydown", {
      key: "s",
      ctrlKey: true,
      bubbles: true,
    });
    document.dispatchEvent(event);

    // Verify submit button was NOT clicked
    expect(submitBtn.click).not.toHaveBeenCalled();
  });

  test("doesn't create floating button when disabled", () => {
    const formEnhancer = new FormEnhancer({
      formSelector: "#test-form",
      enableFloatingButton: false,
    });

    const fab = document.querySelector(".fab");
    expect(fab).toBeFalsy();
  });
});
