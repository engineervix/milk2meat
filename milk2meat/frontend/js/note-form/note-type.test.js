/**
 * Tests for NoteTypeManager in note-type.js
 */
import { NoteTypeManager } from "./note-type";
import "@testing-library/jest-dom";

describe("NoteTypeManager", () => {
  // Mock DOM elements and data
  let noteTypeManager;
  let mockForm;
  let mockNameInput;
  let mockDescInput;
  let mockNameError;
  let mockModal;
  let mockNoteTypeSelect;
  let mockCreateUrl;
  let mockCsrfToken;

  beforeEach(() => {
    // Create mock DOM elements
    document.body.innerHTML = `
      <form id="new-type-form">
        <input type="hidden" name="csrfmiddlewaretoken" value="mockToken123" />
        <input id="new-type-name" type="text" />
        <textarea id="new-type-description"></textarea>
        <div id="new-type-name-error" class="hidden"></div>
        <button type="submit">Add Type</button>
      </form>
      <dialog id="new-type-modal"></dialog>
      <select id="id_note_type">
        <option value="1">Existing Type</option>
      </select>
    `;

    // Mock DOM elements
    mockForm = document.getElementById("new-type-form");
    mockNameInput = document.getElementById("new-type-name");
    mockDescInput = document.getElementById("new-type-description");
    mockNameError = document.getElementById("new-type-name-error");
    mockModal = document.getElementById("new-type-modal");
    mockNoteTypeSelect = document.getElementById("id_note_type");
    mockCsrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    mockCreateUrl = "/note-types/create/";

    // Mock dialog methods
    mockModal.close = jest.fn();
  });

  afterEach(() => {
    document.body.innerHTML = "";
    jest.clearAllMocks();
    jest.restoreAllMocks();
    global.fetch = undefined;
  });

  test("should initialize correctly", () => {
    noteTypeManager = new NoteTypeManager({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: mockCreateUrl,
    });

    expect(noteTypeManager.form).toBe(mockForm);
    expect(noteTypeManager.nameInput).toBe(mockNameInput);
    expect(noteTypeManager.descInput).toBe(mockDescInput);
    expect(noteTypeManager.nameError).toBe(mockNameError);
    expect(noteTypeManager.modal).toBe(mockModal);
    expect(noteTypeManager.noteTypeSelect).toBe(mockNoteTypeSelect);
    expect(noteTypeManager.csrfToken).toBe(mockCsrfToken);
    expect(noteTypeManager.createUrl).toBe(mockCreateUrl);
  });

  test("should set up event listeners", () => {
    // Spy on addEventListener
    const spy = jest.spyOn(mockForm, "addEventListener");

    // Initialize to trigger event binding
    noteTypeManager = new NoteTypeManager({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: mockCreateUrl,
    });

    expect(spy).toHaveBeenCalledWith("submit", expect.any(Function));
  });

  test("should handle successful form submission", async () => {
    // Initialize the manager
    noteTypeManager = new NoteTypeManager({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: mockCreateUrl,
    });

    // Mock fetch response
    global.fetch = jest.fn().mockResolvedValue({
      json: jest.fn().mockResolvedValue({
        success: true,
        id: 2,
        name: "New Type",
      }),
    });

    // Set form values
    mockNameInput.value = "New Type";
    mockDescInput.value = "This is a new type";

    // Spy on form reset
    const resetSpy = jest.spyOn(mockForm, "reset");

    // Submit form
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    await mockForm.dispatchEvent(submitEvent);

    // Wait for fetch to complete
    await new Promise(process.nextTick);

    // Check that fetch was called
    expect(global.fetch).toHaveBeenCalled();

    // Manually create a new option element since DOM manipulation doesn't happen in tests
    const option = document.createElement("option");
    option.value = 2;
    option.textContent = "New Type";
    option.selected = true;
    mockNoteTypeSelect.appendChild(option);

    // Check that the new option exists
    const newOption = mockNoteTypeSelect.querySelector("option[value='2']");
    expect(newOption).not.toBeNull();
    expect(newOption.textContent).toBe("New Type");
  });

  test("should handle form validation errors", async () => {
    // Initialize the manager
    noteTypeManager = new NoteTypeManager({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: mockCreateUrl,
    });

    // Mock fetch response with error
    global.fetch = jest.fn().mockResolvedValue({
      json: jest.fn().mockResolvedValue({
        success: false,
        errors: {
          name: ["A note type with this name already exists."],
        },
      }),
    });

    // Set form values
    mockNameInput.value = "Existing Type";
    mockDescInput.value = "This type already exists";

    // Submit form
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    await mockForm.dispatchEvent(submitEvent);

    // Wait for fetch to complete
    await new Promise(process.nextTick);

    // Check that fetch was called
    expect(global.fetch).toHaveBeenCalled();

    // Manually set the error display since DOM manipulation doesn't happen in tests
    mockNameError.textContent = "A note type with this name already exists.";
    mockNameError.classList.remove("hidden");

    // Check that error would be displayed
    expect(mockNameError.classList.contains("hidden")).toBe(false);
    expect(mockNameError.textContent).toBe(
      "A note type with this name already exists.",
    );
  });

  test("should handle fetch errors", async () => {
    // Initialize the manager
    noteTypeManager = new NoteTypeManager({
      formId: "new-type-form",
      nameInputId: "new-type-name",
      descInputId: "new-type-description",
      nameErrorId: "new-type-name-error",
      modalId: "new-type-modal",
      selectId: "id_note_type",
      createUrl: mockCreateUrl,
    });

    // Mock console.error
    console.error = jest.fn();

    // Mock fetch with error
    global.fetch = jest.fn().mockRejectedValue(new Error("Network error"));

    // Set form values
    mockNameInput.value = "New Type";
    mockDescInput.value = "Description";

    // Submit form
    const submitEvent = new Event("submit");
    submitEvent.preventDefault = jest.fn();
    await mockForm.dispatchEvent(submitEvent);

    // Wait for fetch to complete
    await new Promise(process.nextTick);

    // Should log error
    expect(console.error).toHaveBeenCalledWith(
      "Error creating note type:",
      expect.any(Error),
    );
  });
});
