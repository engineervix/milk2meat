/**
 * @jest-environment jsdom
 */

import { AjaxBookFormManager } from "./ajax-book-form";
import { FormEnhancer } from "../form-enhancements";

// Mock the imported dependencies
jest.mock("./ajax-book-form");
jest.mock("../form-enhancements");

describe("Book Form Index", () => {
  beforeEach(() => {
    // Reset mocks and clear DOM
    jest.resetAllMocks();
    document.body.innerHTML = `
      <form id="book-form">
        <input type="text" name="title" />
        <button type="submit">Save</button>
        <div id="form-messages"></div>
      </form>
    `;

    // Set up window properties used in the index.js file
    window.editors = [{ codemirror: { save: jest.fn() } }];
    window.bookUpdateUrl = "/api/books/update/123/";
    window.currentBookId = "123";
  });

  afterEach(() => {
    // Clean up
    document.body.innerHTML = "";
    jest.clearAllMocks();
    delete window.editors;
    delete window.bookUpdateUrl;
    delete window.currentBookId;
  });

  test("initializes components when DOM is loaded", () => {
    // Require the module - this just loads it but doesn't execute the DOMContentLoaded callback
    const indexModule = require("./index");

    // Manually trigger DOMContentLoaded event
    const domContentLoadedEvent = new Event("DOMContentLoaded");
    document.dispatchEvent(domContentLoadedEvent);

    // Verify AjaxBookFormManager was initialized correctly
    expect(AjaxBookFormManager).toHaveBeenCalledWith({
      formSelector: "#book-form",
      messageContainerId: "form-messages",
      editorInstances: window.editors,
      updateUrl: window.bookUpdateUrl,
      bookId: window.currentBookId,
    });

    // Verify FormEnhancer was initialized correctly
    expect(FormEnhancer).toHaveBeenCalledWith({
      formSelector: "#book-form",
      fabPosition: "bottom-right",
      fabLabel: "Save",
    });
  });

  test("handles case when window.editors is not defined", () => {
    // Remove window.editors to test fallback
    delete window.editors;

    // Require module again with editors undefined
    jest.resetModules();
    require("./index");

    // Trigger the DOM load event
    document.dispatchEvent(new Event("DOMContentLoaded"));

    // Verify AjaxBookFormManager was called with empty editors array
    expect(AjaxBookFormManager).toHaveBeenCalledWith(
      expect.objectContaining({
        editorInstances: [],
      }),
    );
  });
});
