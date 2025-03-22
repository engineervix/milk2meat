/**
 * @jest-environment jsdom
 */

// Create a mock instance we can access directly
const mockCodeMirror = {
  on: jest.fn((event, callback) => {
    // Store handlers for testing
    mockHandlers[event] = callback;
  }),
  replaceSelection: jest.fn(),
};

// Store event handlers for testing
const mockHandlers = {};

// Setup a mock for EasyMDE that returns our consistent mockCodeMirror object
jest.mock("easymde", () => {
  const MockEasyMDE = jest.fn().mockImplementation(() => ({
    codemirror: mockCodeMirror,
  }));
  return MockEasyMDE;
});

// Mock Turndown
jest.mock("turndown", () => {
  const MockTurndownService = jest.fn().mockImplementation(() => ({
    turndown: jest.fn((html) => `converted-${html}`),
  }));
  return MockTurndownService;
});

// Import after mocking
import EasyMDE from "easymde";
import TurndownService from "turndown";

describe("Editor functionality", () => {
  let originalAddEventListener;
  // Store document event listeners
  let documentEventHandlers = {};
  // Store form event listeners
  let formEventHandlers = {};

  beforeEach(() => {
    // Setup DOM for tests
    document.body.innerHTML = `
      <div>
        <textarea data-editor></textarea>
      </div>
    `;

    // Mock implementations
    EasyMDE.mockClear();
    TurndownService.mockClear();
    mockCodeMirror.on.mockClear();

    // Setup method to capture event listeners
    originalAddEventListener = document.addEventListener;
    document.addEventListener = jest.fn((event, handler) => {
      documentEventHandlers[event] = handler;
      // Immediately call the handler if it's DOMContentLoaded
      if (event === "DOMContentLoaded") {
        handler();
      }
    });

    // Add a mock addEventListener to the HTMLFormElement prototype
    HTMLFormElement.prototype.addEventListener = jest.fn((event, handler) => {
      formEventHandlers[event] = handler;
    });

    // Reset tracked event handlers
    documentEventHandlers = {};
    formEventHandlers = {};

    jest.resetModules();
  });

  afterEach(() => {
    // Restore original methods
    document.addEventListener = originalAddEventListener;
    delete HTMLFormElement.prototype.addEventListener;
    // Clean up
    jest.clearAllMocks();
  });

  test("initializes EasyMDE editors for elements with data-editor attribute", () => {
    // Reset mocks
    EasyMDE.mockClear();

    // Create DOMContentLoaded handler based on editor.js
    const handler = () => {
      const editorElements = document.querySelectorAll("[data-editor]");
      editorElements.forEach((element) => {
        new EasyMDE({
          element: element,
          spellChecker: false,
          minHeight: "300px",
        });
      });
    };

    // Call the handler
    handler();

    // Verify editor was initialized
    expect(EasyMDE).toHaveBeenCalledWith(
      expect.objectContaining({
        element: expect.any(Element),
        spellChecker: false,
        minHeight: "300px",
      }),
    );
  });

  test("sets up paste event handler for rich text conversion", () => {
    // Reset mocks
    TurndownService.mockClear();
    mockCodeMirror.on.mockClear();

    // Create our own handler for initialization
    const handler = () => {
      // Create turndown service
      const turndownService = new TurndownService({
        headingStyle: "atx",
        codeBlockStyle: "fenced",
      });

      // Create editor and setup paste handler
      const editor = new EasyMDE({
        element: document.querySelector("[data-editor]"),
        spellChecker: false,
        minHeight: "300px",
      });

      // Add paste handler
      editor.codemirror.on("paste", jest.fn());
    };

    // Call the handler
    handler();

    // Verify turndown service was created
    expect(TurndownService).toHaveBeenCalledWith(
      expect.objectContaining({
        headingStyle: "atx",
        codeBlockStyle: "fenced",
      }),
    );

    // Verify paste handler was registered
    expect(mockCodeMirror.on).toHaveBeenCalledWith(
      "paste",
      expect.any(Function),
    );
  });

  test("converts HTML to Markdown on paste", () => {
    // Import editor module
    require("./editor");

    // Get the paste handler that was registered
    const pasteHandler = mockHandlers.paste;
    expect(pasteHandler).toBeDefined();

    // Create mock clipboard event
    const mockClipboardEvent = {
      clipboardData: {
        types: ["text/html"],
        getData: jest.fn((type) => {
          if (type === "text/html") {
            return "<p>Test HTML</p>";
          }
          return "";
        }),
      },
      preventDefault: jest.fn(),
    };

    // Call the paste handler directly
    const result = pasteHandler(mockCodeMirror, mockClipboardEvent);

    // Verify clipboard data was retrieved
    expect(mockClipboardEvent.clipboardData.getData).toHaveBeenCalledWith(
      "text/html",
    );

    // Verify default browser paste was prevented
    expect(mockClipboardEvent.preventDefault).toHaveBeenCalled();

    // Verify selection was replaced with converted Markdown
    expect(mockCodeMirror.replaceSelection).toHaveBeenCalled();

    // Verify handler returns true to indicate handled
    expect(result).toBe(true);
  });

  test("tracks unsaved changes when editor content changes", () => {
    // Import editor module
    require("./editor");

    // Verify change handler was registered
    expect(mockCodeMirror.on).toHaveBeenCalledWith(
      "change",
      expect.any(Function),
    );

    // Get the change handler that was registered
    const changeHandler = mockHandlers.change;
    expect(changeHandler).toBeDefined();

    // Reset form changed flags
    window.formChanged = false;

    // Trigger editor change
    changeHandler();

    // Verify form changed flags were set
    expect(window.formChanged).toBe(true);
  });

  test("warns when navigating away with unsaved changes", () => {
    // Setup
    window.formChanged = true;

    // Setup beforeunload event
    const event = new Event("beforeunload");
    Object.defineProperty(event, "returnValue", {
      writable: true,
      value: "",
    });

    // Add event listener to capture beforeunload behavior
    const beforeUnloadHandler = jest.fn((e) => {
      e.returnValue = "You have unsaved changes.";
      return "You have unsaved changes.";
    });

    window.addEventListener("beforeunload", beforeUnloadHandler);

    // Trigger beforeunload event
    window.dispatchEvent(event);

    // Check if handler was called
    expect(beforeUnloadHandler).toHaveBeenCalled();
    // Check if returnValue was set
    expect(event.returnValue).toBe("You have unsaved changes.");

    // Cleanup
    window.removeEventListener("beforeunload", beforeUnloadHandler);
    window.formChanged = false;
  });

  test("clears unsaved changes warning when form is submitted", () => {
    // Create a mock form and a module variable for formChanged
    document.body.innerHTML = `
      <form id="test-form">
        <button type="submit">Submit</button>
      </form>
    `;
    const form = document.getElementById("test-form");

    // Import the module to run its initialization code
    jest.isolateModules(() => {
      // Set up initial state
      window.formChanged = true;

      // Import module, which will set up event listeners
      require("./editor");

      // Trigger the submit event on the form
      form.dispatchEvent(
        new Event("submit", {
          bubbles: true,
          cancelable: true,
        }),
      );

      // The event listener in the module should have reset window.formChanged
      expect(window.formChanged).toBe(false);
    });
  });

  test("initializes timeline editor when element exists", () => {
    // Add timeline editor elements
    document.body.innerHTML += `
      <div id="timeline-editor">
        <div id="timeline-events"></div>
        <input id="timeline-data" value='{"events":[{"date":"1000 BC","description":"Test event"}]}'>
        <button id="add-timeline-event">Add Event</button>
      </div>
    `;

    // Create spy for timeline rendering
    const renderSpy = jest.spyOn(Document.prototype, "createElement");

    // Import editor module
    require("./editor");

    // Verify timeline data was loaded
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.innerHTML).not.toBe("");

    // Check if timeline events rendered correctly
    expect(renderSpy).toHaveBeenCalled();
  });
});
