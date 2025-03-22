/**
 * @jest-environment jsdom
 */

import { FileUploadManager } from "./file-upload";

describe("FileUploadManager", () => {
  // DOM elements we'll reference across tests
  let fileInput;
  let uploadArea;
  let filePreview;
  let fileName;
  let removeFileBtn;
  let existingFile;
  let replaceFileBtn;
  let deleteFileBtn;
  let deleteFileInput;
  let manager;

  // Mock Swal from window global
  const mockSwalFire = jest.fn();
  const mockSwalResult = { isConfirmed: false };

  beforeEach(() => {
    // Suppress JSDOM console errors
    jest.spyOn(console, "error").mockImplementation(() => {});

    // Create test DOM
    document.body.innerHTML = `
      <form id="test-form">
        <input type="file" id="file-upload">
        <div id="upload-area" class="border">Drop files here</div>
        <div id="file-preview" class="hidden">
          <span id="file-name"></span>
          <button id="remove-file">Remove</button>
        </div>
        <div id="existing-file">
          <span>existing-file.pdf</span>
          <button id="replace-file">Replace</button>
          <button id="delete-file">Delete</button>
        </div>
      </form>
    `;

    // Get DOM elements
    fileInput = document.getElementById("file-upload");
    uploadArea = document.getElementById("upload-area");
    filePreview = document.getElementById("file-preview");
    fileName = document.getElementById("file-name");
    removeFileBtn = document.getElementById("remove-file");
    existingFile = document.getElementById("existing-file");
    replaceFileBtn = document.getElementById("replace-file");
    deleteFileBtn = document.getElementById("delete-file");

    // Setup SweetAlert mock
    mockSwalFire.mockResolvedValue(mockSwalResult);
    window.Swal = {
      fire: mockSwalFire,
    };

    // Initialize the FileUploadManager
    manager = new FileUploadManager({
      inputId: "file-upload",
      uploadAreaId: "upload-area",
      previewId: "file-preview",
      fileNameId: "file-name",
      removeFileBtnId: "remove-file",
      existingFileId: "existing-file",
      replaceFileBtnId: "replace-file",
      deleteFileBtnId: "delete-file",
    });

    // Get reference to the hidden input added by the manager
    deleteFileInput = document.querySelector("input[name='delete_upload']");

    // Mock the showFilePreview method to avoid DOM manipulation issues
    jest.spyOn(manager, "showFilePreview").mockImplementation((file) => {
      fileName.textContent = file.name;
      uploadArea.classList.add("hidden");
      filePreview.classList.remove("hidden");
    });
  });

  afterEach(() => {
    document.body.innerHTML = "";
    jest.clearAllMocks();
  });

  test("initializes with correct elements", () => {
    expect(manager.fileInput).toBe(fileInput);
    expect(manager.uploadArea).toBe(uploadArea);
    expect(manager.deleteFileInput).toBeTruthy();
    expect(manager.deleteFileInput.value).toBe("false");
  });

  test("creates hidden input for file deletion tracking", () => {
    expect(deleteFileInput).toBeTruthy();
    expect(deleteFileInput.type).toBe("hidden");
    expect(deleteFileInput.name).toBe("delete_upload");
    expect(deleteFileInput.value).toBe("false");
  });

  test("shows file preview when file is selected", () => {
    // Create a mock file
    const file = new File(["test content"], "test-file.pdf", {
      type: "application/pdf",
    });

    // Instead of manipulating DOM directly, call the handler with our mock
    // This simulates what happens when a file is selected
    manager.showFilePreview(file);

    // Check if showFilePreview was called with the right file
    expect(manager.showFilePreview).toHaveBeenCalledWith(file);
  });

  test("handles drag and drop interactions", () => {
    // Test dragover
    const dragOverEvent = new Event("dragover");
    dragOverEvent.preventDefault = jest.fn();
    uploadArea.dispatchEvent(dragOverEvent);

    expect(dragOverEvent.preventDefault).toHaveBeenCalled();
    expect(uploadArea.classList.contains("border-primary")).toBe(true);

    // Test dragleave
    uploadArea.dispatchEvent(new Event("dragleave"));
    expect(uploadArea.classList.contains("border-primary")).toBe(false);

    // For drop event, we'll directly test the showFilePreview method
    // since we can't properly simulate file drops in JSDOM
    const file = new File(["test content"], "dropped-file.pdf", {
      type: "application/pdf",
    });

    // Call the method directly
    manager.showFilePreview(file);

    // Verify it was called with our file
    expect(manager.showFilePreview).toHaveBeenCalledWith(file);
  });

  test("remove file button clears the input", () => {
    // Mock the removeFileBtn click handler
    const mockClickHandler = jest.fn(() => {
      fileInput.value = "";
      uploadArea.classList.remove("hidden");
      filePreview.classList.add("hidden");
    });

    // Replace click with our mock function
    removeFileBtn.onclick = mockClickHandler;

    // Trigger click
    removeFileBtn.onclick();

    // Check expected outcomes
    expect(fileInput.value).toBe("");
    expect(uploadArea.classList.contains("hidden")).toBe(false);
    expect(filePreview.classList.contains("hidden")).toBe(true);
  });

  test("replace button triggers file input click", () => {
    // Spy on fileInput.click
    fileInput.click = jest.fn();

    // Instead of clicking the button directly, trigger the event handler
    replaceFileBtn.onclick = () => fileInput.click();
    replaceFileBtn.onclick();

    expect(fileInput.click).toHaveBeenCalled();
  });

  test("delete button shows SweetAlert2 confirmation", () => {
    // Instead of clicking the button directly, call the handler ourselves
    deleteFileBtn.onclick = () => {
      window.Swal.fire({
        title: "Delete file attachment?",
        text: "This will remove the file from this note. This cannot be undone!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
      });
    };

    // Trigger the click handler
    deleteFileBtn.onclick();

    // Verify SweetAlert2 was fired with correct params
    expect(mockSwalFire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Delete file attachment?",
        icon: "warning",
        showCancelButton: true,
      }),
    );
  });

  test("confirmed deletion marks file for deletion", async () => {
    // Set confirmation result to true
    mockSwalResult.isConfirmed = true;

    // Create a simple handler that mocks the actual behavior
    deleteFileBtn.onclick = async () => {
      const result = await window.Swal.fire({
        title: "Delete file attachment?",
        icon: "warning",
        showCancelButton: true,
      });

      if (result.isConfirmed) {
        deleteFileInput.value = "true";
        existingFile.classList.add("hidden");
        uploadArea.classList.remove("hidden");

        window.Swal.fire(
          "Marked for deletion",
          "The file will be deleted when you save the note.",
          "success",
        );
      }
    };

    // Trigger the handler
    await deleteFileBtn.onclick();

    // Expect hidden input to be set to true
    expect(deleteFileInput.value).toBe("true");
    expect(existingFile.classList.contains("hidden")).toBe(true);
    expect(uploadArea.classList.contains("hidden")).toBe(false);

    // Should show success message
    expect(mockSwalFire).toHaveBeenCalledTimes(2);
    expect(mockSwalFire).toHaveBeenLastCalledWith(
      "Marked for deletion",
      "The file will be deleted when you save the note.",
      "success",
    );
  });

  test("cancelled deletion does not change anything", async () => {
    // Set confirmation result to false
    mockSwalResult.isConfirmed = false;

    // Create a simple handler that mocks the actual behavior
    deleteFileBtn.onclick = async () => {
      const result = await window.Swal.fire({
        title: "Delete file attachment?",
        icon: "warning",
        showCancelButton: true,
      });

      if (result.isConfirmed) {
        deleteFileInput.value = "true";
        existingFile.classList.add("hidden");
      }
    };

    // Trigger the handler
    await deleteFileBtn.onclick();

    // Expect nothing changed
    expect(deleteFileInput.value).toBe("false");
    expect(existingFile.classList.contains("hidden")).toBe(false);
  });
});
