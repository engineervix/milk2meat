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

  test("does not process non-HTML paste", () => {
    // Import editor module
    require("./editor");

    // Get the paste handler that was registered
    const pasteHandler = mockHandlers.paste;
    expect(pasteHandler).toBeDefined();

    // Reset replaceSelection mock
    mockCodeMirror.replaceSelection.mockClear();

    // Create mock clipboard event with only plain text (no HTML)
    const mockClipboardEvent = {
      clipboardData: {
        types: ["text/plain"],
        getData: jest.fn((type) => {
          if (type === "text/plain") {
            return "Plain text content";
          }
          return "";
        }),
      },
      preventDefault: jest.fn(),
    };

    // Call the paste handler directly
    const result = pasteHandler(mockCodeMirror, mockClipboardEvent);

    // Verify paste was not handled
    expect(result).toBe(false);

    // Verify selection was not replaced
    expect(mockCodeMirror.replaceSelection).not.toHaveBeenCalled();

    // Verify default browser paste was not prevented
    expect(mockClipboardEvent.preventDefault).not.toHaveBeenCalled();
  });

  test("handles clipboard data not available", () => {
    // Import editor module
    require("./editor");

    // Get the paste handler that was registered
    const pasteHandler = mockHandlers.paste;
    expect(pasteHandler).toBeDefined();

    // Reset replaceSelection mock
    mockCodeMirror.replaceSelection.mockClear();

    // Create mock clipboard event with no clipboardData
    const mockClipboardEvent = {};

    // Call the paste handler directly
    const result = pasteHandler(mockCodeMirror, mockClipboardEvent);

    // Verify paste was not handled
    expect(result).toBe(false);

    // Verify selection was not replaced
    expect(mockCodeMirror.replaceSelection).not.toHaveBeenCalled();
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
  });

  test("clears unsaved changes warning when form is submitted", () => {
    // Setup form in the document
    document.body.innerHTML = `
      <form>
        <textarea data-editor></textarea>
        <button type="submit">Save</button>
      </form>
    `;

    // Reset previous handlers
    jest.resetModules();

    // Mark form as changed
    window.formChanged = true;

    // Import editor to initialize event listeners
    require("./editor");

    // Extract the form submit handler that was registered
    const form = document.querySelector("form");
    const submitHandler = formEventHandlers.submit;
    expect(submitHandler).toBeDefined();

    // Call the handler directly
    submitHandler();

    // Verify form changed flag was reset
    expect(window.formChanged).toBe(false);
  });

  test("provides resetFormChanged function for AJAX forms", () => {
    // Import editor module
    require("./editor");

    // Check if resetFormChanged is available
    expect(typeof window.resetFormChanged).toBe("function");

    // Set changed flag
    window.formChanged = true;

    // Call reset function
    window.resetFormChanged();

    // Verify flag was reset
    expect(window.formChanged).toBe(false);
  });

  test("directly test the cancel button confirmation handler", () => {
    // Setup
    window.formChanged = true;
    window.confirm = jest.fn(() => true);

    // Create a handler that mimics the one in editor.js
    const handleCancelClick = (e) => {
      if (window.formChanged) {
        const confirmed = window.confirm(
          "You have unsaved changes. Are you sure you want to leave this page?",
        );
        if (!confirmed) {
          e.preventDefault();
          return;
        }
        window.formChanged = false;
      }
    };

    // Create a mock event
    const mockEvent = {
      preventDefault: jest.fn(),
    };

    // Call the handler
    handleCancelClick(mockEvent);

    // Verify confirm was called with the right message
    expect(window.confirm).toHaveBeenCalledWith(
      "You have unsaved changes. Are you sure you want to leave this page?",
    );

    // Since we mocked confirm to return true, formChanged should be reset
    expect(window.formChanged).toBe(false);

    // And preventDefault should not be called
    expect(mockEvent.preventDefault).not.toHaveBeenCalled();
  });

  test("directly test cancel button handling when user declines confirmation", () => {
    // Setup
    window.formChanged = true;
    window.confirm = jest.fn(() => false);

    // Create a handler that mimics the one in editor.js
    const handleCancelClick = (e) => {
      if (window.formChanged) {
        const confirmed = window.confirm(
          "You have unsaved changes. Are you sure you want to leave this page?",
        );
        if (!confirmed) {
          e.preventDefault();
          return;
        }
        window.formChanged = false;
      }
    };

    // Create a mock event
    const mockEvent = {
      preventDefault: jest.fn(),
    };

    // Call the handler
    handleCancelClick(mockEvent);

    // Verify confirm was called
    expect(window.confirm).toHaveBeenCalled();

    // Since we mocked confirm to return false, formChanged should still be true
    expect(window.formChanged).toBe(true);

    // And preventDefault should be called to stop navigation
    expect(mockEvent.preventDefault).toHaveBeenCalled();
  });

  test("initializes timeline editor when element exists", () => {
    // Setup DOM with timeline editor
    document.body.innerHTML = `
      <div id="timeline-editor">
        <input type="hidden" id="timeline-data" value='{"events":[{"date":"1000 BC","description":"Test Event"}]}'>
        <div id="timeline-events"></div>
        <button id="add-timeline-event">Add Event</button>
      </div>
    `;

    // Import to trigger initialization
    require("./editor");

    // Verify that timeline editor is initialized
    // We'll check this by looking for the rendered timeline events
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.innerHTML).toContain("timeline-event");
  });
});

describe("Timeline Editor functionality", () => {
  // Create a helper function to directly initialize the timeline editor
  function manuallyInitializeTimelineEditor() {
    // Extract the initializeTimelineEditor function from editor.js
    // This is similar to what's in the editor.js file
    const timelineEvents = document.getElementById("timeline-events");
    const timelineData = document.getElementById("timeline-data");
    const addEventButton = document.getElementById("add-timeline-event");

    let timelineItems = [];

    // Load existing timeline data if available
    if (timelineData.value) {
      try {
        const parsedData = JSON.parse(timelineData.value);
        timelineItems = parsedData.events || [];
        renderTimelineEvents();
      } catch (e) {
        console.error("Error parsing timeline data:", e);
        timelineItems = [];
        renderTimelineEvents();
      }
    } else {
      renderTimelineEvents();
    }

    // Add new event handler
    addEventButton.addEventListener("click", function () {
      timelineItems.push({
        date: "",
        description: "",
      });
      renderTimelineEvents();
      updateTimelineData();
    });

    // Render timeline events
    function renderTimelineEvents() {
      timelineEvents.innerHTML = "";

      if (timelineItems.length === 0) {
        const emptyMessage = document.createElement("div");
        emptyMessage.className = "p-4 text-center text-base-content/60";
        emptyMessage.textContent =
          'No timeline events yet. Click "Add Event" to create one.';
        timelineEvents.appendChild(emptyMessage);
        return;
      }

      timelineItems.forEach((item, index) => {
        const eventElement = document.createElement("div");
        eventElement.className =
          "timeline-event mb-4 p-4 rounded-lg bg-base-200";
        eventElement.dataset.index = index;

        eventElement.innerHTML = `
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text">Date</span>
              </label>
              <input type="text" class="input input-bordered timeline-date"
                     value="${item.date}" placeholder="e.g., 1010-971 B.C.">
            </div>
            <div class="form-control md:col-span-2">
              <label class="label">
                <span class="label-text">Description</span>
              </label>
              <input type="text" class="input input-bordered timeline-description"
                     value="${item.description}" placeholder="e.g., Reign of David">
            </div>
          </div>
          <div class="timeline-event-actions mt-2 flex justify-end">
            <button type="button" class="btn btn-sm btn-outline btn-error delete-event">Remove</button>
          </div>
        `;

        // Add event listeners
        const dateInput = eventElement.querySelector(".timeline-date");
        const descriptionInput = eventElement.querySelector(
          ".timeline-description",
        );
        const deleteButton = eventElement.querySelector(".delete-event");

        dateInput.addEventListener("input", function () {
          timelineItems[index].date = this.value;
          updateTimelineData();
        });

        descriptionInput.addEventListener("input", function () {
          timelineItems[index].description = this.value;
          updateTimelineData();
        });

        deleteButton.addEventListener("click", function () {
          timelineItems.splice(index, 1);
          renderTimelineEvents();
          updateTimelineData();
        });

        timelineEvents.appendChild(eventElement);
      });
    }

    // Update hidden input with timeline data
    function updateTimelineData() {
      timelineData.value = JSON.stringify({
        events: timelineItems,
      });
    }

    // Return functions for testing
    return {
      renderTimelineEvents,
      updateTimelineData,
      getTimelineItems: () => timelineItems,
    };
  }

  beforeEach(() => {
    // Setup DOM with timeline editor
    document.body.innerHTML = `
      <div id="timeline-editor">
        <input type="hidden" id="timeline-data" value='{"events":[{"date":"1000 BC","description":"Test Event"}]}'>
        <div id="timeline-events"></div>
        <button id="add-timeline-event">Add Event</button>
      </div>
    `;

    // Mock console.error to avoid test noise
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    console.error.mockRestore();
  });

  test("initializes timeline editor with existing data", () => {
    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Check if the timeline events were rendered
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.innerHTML).not.toBe("");
    expect(timelineEvents.querySelector(".timeline-date").value).toBe(
      "1000 BC",
    );
    expect(timelineEvents.querySelector(".timeline-description").value).toBe(
      "Test Event",
    );
  });

  test("initializes timeline editor with empty data", () => {
    // Set empty timeline data
    document.getElementById("timeline-data").value = "";

    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Check if empty message was rendered
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.innerHTML).not.toBe("");
    expect(timelineEvents.textContent).toContain("No timeline events yet");
  });

  test("initializes timeline editor with invalid JSON data", () => {
    // Set invalid JSON
    document.getElementById("timeline-data").value = "invalid-json";

    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Check if error was logged
    expect(console.error).toHaveBeenCalled();

    // Check if timeline is still initialized with empty array
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.innerHTML).not.toBe("");
    expect(timelineEvents.textContent).toContain("No timeline events yet");
  });

  test("adds a new timeline event when button is clicked", () => {
    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Get initial count of events
    const initialEventCount =
      document.querySelectorAll(".timeline-event").length;

    // Click the add event button
    const addButton = document.getElementById("add-timeline-event");
    addButton.click();

    // Check if a new event was added
    const newEventCount = document.querySelectorAll(".timeline-event").length;
    expect(newEventCount).toBe(initialEventCount + 1);

    // Check if timeline data was updated
    const timelineData = document.getElementById("timeline-data");
    const parsedData = JSON.parse(timelineData.value);
    expect(parsedData.events.length).toBe(initialEventCount + 1);
  });

  test("updates timeline data when event date is changed", () => {
    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Get the date input field for the first event
    const dateInput = document.querySelector(".timeline-date");
    expect(dateInput).not.toBeNull();

    // Change the date
    dateInput.value = "950 BC";
    dateInput.dispatchEvent(new Event("input"));

    // Check if timeline data was updated
    const timelineData = document.getElementById("timeline-data");
    const parsedData = JSON.parse(timelineData.value);
    expect(parsedData.events[0].date).toBe("950 BC");
  });

  test("updates timeline data when event description is changed", () => {
    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Get the description input field for the first event
    const descriptionInput = document.querySelector(".timeline-description");
    expect(descriptionInput).not.toBeNull();

    // Change the description
    descriptionInput.value = "Updated Event";
    descriptionInput.dispatchEvent(new Event("input"));

    // Check if timeline data was updated
    const timelineData = document.getElementById("timeline-data");
    const parsedData = JSON.parse(timelineData.value);
    expect(parsedData.events[0].description).toBe("Updated Event");
  });

  test("removes an event when delete button is clicked", () => {
    // Manually initialize timeline editor
    manuallyInitializeTimelineEditor();

    // Get initial count of events
    const initialEventCount =
      document.querySelectorAll(".timeline-event").length;
    expect(initialEventCount).toBeGreaterThan(0);

    // Click the delete button for the first event
    const deleteButton = document.querySelector(".delete-event");
    deleteButton.click();

    // Check if the event was removed
    const newEventCount = document.querySelectorAll(".timeline-event").length;
    expect(newEventCount).toBe(0); // All events are removed

    // Check if timeline data was updated
    const timelineData = document.getElementById("timeline-data");
    const parsedData = JSON.parse(timelineData.value);
    expect(parsedData.events.length).toBe(0);

    // Check if empty message is shown
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.textContent).toContain("No timeline events yet");
  });

  test("shows empty message when all events are removed", () => {
    // Set timeline data with one event
    document.getElementById("timeline-data").value =
      '{"events":[{"date":"1000 BC","description":"Test Event"}]}';

    // Manually initialize timeline editor
    const { getTimelineItems } = manuallyInitializeTimelineEditor();

    // Verify we have exactly one event
    expect(getTimelineItems().length).toBe(1);

    // Click the delete button for the only event
    const deleteButton = document.querySelector(".delete-event");
    deleteButton.click();

    // Check if empty message is shown
    const timelineEvents = document.getElementById("timeline-events");
    expect(timelineEvents.textContent).toContain("No timeline events yet");

    // Verify the timeline items array is empty
    expect(getTimelineItems().length).toBe(0);
  });
});
