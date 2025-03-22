/**
 * Tests for note-form/index.js
 */
import "@testing-library/jest-dom";

// Mock all the dependencies
jest.mock("./bible-books", () => ({
  BibleBooksManager: jest.fn(),
}));

jest.mock("./tags-input", () => ({
  TagsManager: jest.fn(),
}));

jest.mock("./file-upload", () => ({
  FileUploadManager: jest.fn(),
}));

jest.mock("./note-type", () => ({
  NoteTypeManager: jest.fn(),
}));

jest.mock("./ajax-form", () => ({
  AjaxFormManager: jest.fn(),
}));

jest.mock("../form-enhancements", () => ({
  FormEnhancer: jest.fn(),
}));

describe("Note Form Index", () => {
  const originalAddEventListener = document.addEventListener;
  let domContentLoadedHandler;

  beforeEach(() => {
    // Mock document.addEventListener to capture DOMContentLoaded handler
    document.addEventListener = jest.fn((event, handler) => {
      if (event === "DOMContentLoaded") {
        domContentLoadedHandler = handler;
      }
    });

    // Mock required DOM elements
    document.body.innerHTML = `
      <div id="referenced-books"></div>
      <div id="book-suggestions-list"></div>
      <div id="book-suggestions"></div>
      <div id="selected-books-container"></div>
      <input id="referenced-books-json" type="hidden" />
      <input id="tags-input" />
      <input id="hidden-tags-input" type="hidden" />
      <div id="tags-container"></div>
      <input id="file-upload" type="file" />
      <div id="upload-area"></div>
      <div id="file-preview"></div>
      <div id="file-name"></div>
      <button id="remove-file"></button>
      <div id="existing-file"></div>
      <button id="replace-file"></button>
      <button id="delete-file"></button>
      <form id="new-type-form"></form>
      <input id="new-type-name" />
      <textarea id="new-type-description"></textarea>
      <div id="new-type-name-error"></div>
      <dialog id="new-type-modal"></dialog>
      <select id="id_note_type"></select>
      <form id="note-form"></form>
      <div id="form-messages"></div>
    `;

    // Create global window properties needed by the module
    global.window.bibleBooks = [{ id: 1, title: "Genesis" }];
    global.window.noteTypeCreateUrl = "/api/note-types/create/";
    global.window.noteCreateUrl = "/api/notes/create/";
    global.window.noteUpdateUrl = "/api/notes/update/";
    global.window.currentNoteId = "123";
    global.window.editors = [{ name: "mockEditor" }];

    // Import the module to test (this will trigger the event listener setup)
    require("./index.js");
  });

  afterEach(() => {
    // Restore original document.addEventListener
    document.addEventListener = originalAddEventListener;
    document.body.innerHTML = "";

    // Clear mocks
    jest.clearAllMocks();

    // Reset modules to ensure clean state for each test
    jest.resetModules();

    // Clean up global properties
    delete global.window.bibleBooks;
    delete global.window.noteTypeCreateUrl;
    delete global.window.noteCreateUrl;
    delete global.window.noteUpdateUrl;
    delete global.window.currentNoteId;
    delete global.window.editors;
  });

  test("should register DOMContentLoaded event listener", () => {
    expect(document.addEventListener).toHaveBeenCalledWith(
      "DOMContentLoaded",
      expect.any(Function),
    );
  });

  test("should initialize all components when DOM is loaded", () => {
    // Get mock constructors
    const { BibleBooksManager } = require("./bible-books");
    const { TagsManager } = require("./tags-input");
    const { FileUploadManager } = require("./file-upload");
    const { NoteTypeManager } = require("./note-type");
    const { AjaxFormManager } = require("./ajax-form");
    const { FormEnhancer } = require("../form-enhancements");

    // Trigger DOMContentLoaded handler
    domContentLoadedHandler();

    // Verify BibleBooksManager was initialized with correct options
    expect(BibleBooksManager).toHaveBeenCalledWith({
      inputId: "referenced-books",
      booksListId: "book-suggestions-list",
      suggestionsId: "book-suggestions",
      selectedContainerId: "selected-books-container",
      hiddenInputId: "referenced-books-json",
      bibleBooks: [{ id: 1, title: "Genesis" }],
    });

    // Verify TagsManager was initialized with correct options
    expect(TagsManager).toHaveBeenCalledWith({
      inputId: "tags-input",
      hiddenInputId: "hidden-tags-input",
      containerId: "tags-container",
    });

    // Verify FileUploadManager was initialized with correct options
    expect(FileUploadManager).toHaveBeenCalledWith({
      inputId: "file-upload",
      uploadAreaId: "upload-area",
      previewId: "file-preview",
      fileNameId: "file-name",
      removeFileBtnId: "remove-file",
      existingFileId: "existing-file",
      replaceFileBtnId: "replace-file",
      deleteFileBtnId: "delete-file",
    });

    // Verify NoteTypeManager was initialized with correct options
    expect(NoteTypeManager).toHaveBeenCalledWith({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: "/api/note-types/create/",
    });

    // Verify AjaxFormManager was initialized with correct options
    expect(AjaxFormManager).toHaveBeenCalledWith({
      formSelector: "#note-form",
      messageContainerId: "form-messages",
      editorInstances: [{ name: "mockEditor" }],
      createUrl: "/api/notes/create/",
      updateUrl: "/api/notes/update/",
      noteId: "123",
    });

    // Verify FormEnhancer was initialized with correct options
    expect(FormEnhancer).toHaveBeenCalledWith({
      formSelector: "#note-form",
      fabPosition: "bottom-right",
      fabLabel: "Save",
    });
  });

  test("should handle missing window properties gracefully", () => {
    // Create a scenario where window properties are missing
    delete global.window.bibleBooks;
    delete global.window.editors;

    // Trigger DOMContentLoaded handler
    domContentLoadedHandler();

    // Get mock constructors
    const { BibleBooksManager } = require("./bible-books");
    const { AjaxFormManager } = require("./ajax-form");

    // Verify they still get called with fallback values
    expect(BibleBooksManager).toHaveBeenCalledWith(
      expect.objectContaining({
        bibleBooks: [],
      }),
    );

    expect(AjaxFormManager).toHaveBeenCalledWith(
      expect.objectContaining({
        editorInstances: [],
      }),
    );
  });
});
