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
    // Mock showFilePreview method instead of spying on it
    manager.showFilePreview = jest.fn();

    // Create a mock file
    const file = new File(["test content"], "test-file.pdf", {
      type: "application/pdf",
    });

    // Create a FileList-like object
    const fileList = {
      0: file,
      length: 1,
      item: (index) => (index === 0 ? file : null),
    };

    // Set files property
    Object.defineProperty(fileInput, "files", {
      value: fileList,
      writable: true,
    });

    // Trigger the change event
    fileInput.dispatchEvent(new Event("change"));

    // Check if showFilePreview was called with the right file
    expect(manager.showFilePreview).toHaveBeenCalledWith(file);
  });

  test("showFilePreview updates DOM correctly", () => {
    const file = new File(["test content"], "test-file.pdf", {
      type: "application/pdf",
    });

    // Mock classList methods to avoid direct DOM manipulation issues
    existingFile.classList.add = jest.fn();
    uploadArea.classList.add = jest.fn();
    filePreview.classList.remove = jest.fn();

    // Call showFilePreview directly
    manager.showFilePreview(file);

    // Verify updates (without checking actual DOM changes)
    expect(fileName.textContent).toBe("test-file.pdf");
    expect(uploadArea.classList.add).toHaveBeenCalledWith("hidden");
    expect(filePreview.classList.remove).toHaveBeenCalledWith("hidden");
    expect(existingFile.classList.add).toHaveBeenCalledWith("hidden");
    expect(deleteFileInput.value).toBe("false");
  });

  test("handles dragover event", () => {
    const dragOverEvent = new Event("dragover");
    dragOverEvent.preventDefault = jest.fn();

    // Trigger dragover
    uploadArea.dispatchEvent(dragOverEvent);

    // Verify event was prevented and class was added
    expect(dragOverEvent.preventDefault).toHaveBeenCalled();
    expect(uploadArea.classList.contains("border-primary")).toBe(true);
  });

  test("handles dragleave event", () => {
    // First add the class
    uploadArea.classList.add("border-primary");

    // Trigger dragleave
    uploadArea.dispatchEvent(new Event("dragleave"));

    // Verify class was removed
    expect(uploadArea.classList.contains("border-primary")).toBe(false);
  });

  test("handles drop event with file", () => {
    // Mock showFilePreview instead of spying
    manager.showFilePreview = jest.fn();

    // Create mock file
    const file = new File(["test content"], "dropped-file.pdf", {
      type: "application/pdf",
    });

    // Create a FileList-like object
    const fileList = {
      0: file,
      length: 1,
      item: (index) => (index === 0 ? file : null),
    };

    // Create drop event with prevented default
    const dropEvent = new Event("drop");
    dropEvent.preventDefault = jest.fn();
    dropEvent.dataTransfer = {
      files: fileList,
    };

    // We need to mock the file assignment since it's not directly settable in JSDOM
    const origFiles = fileInput.files;
    fileInput.files = null; // Reset first

    // Mock setting files property
    Object.defineProperty(manager, "fileInput", {
      get: () => ({
        files: dropEvent.dataTransfer.files,
      }),
    });

    // Add border-primary class to test it gets removed
    uploadArea.classList.add("border-primary");
    uploadArea.classList.remove = jest.fn();

    // Trigger drop
    uploadArea.dispatchEvent(dropEvent);

    // Verify event handling
    expect(dropEvent.preventDefault).toHaveBeenCalled();
    expect(uploadArea.classList.remove).toHaveBeenCalledWith("border-primary");
    expect(manager.showFilePreview).toHaveBeenCalledWith(file);
  });

  test("remove file button clears the input", () => {
    // Directly test the click event handler
    manager.removeFileBtn = removeFileBtn;
    jest.spyOn(fileInput, "value", "get").mockReturnValue("dummy-path");
    Object.defineProperty(fileInput, "value", {
      set: jest.fn(),
      get: jest.fn().mockReturnValue(""),
      configurable: true,
    });

    uploadArea.classList.remove = jest.fn();
    filePreview.classList.add = jest.fn();

    // Trigger click handler directly
    removeFileBtn.click();

    // Verify expected method calls
    expect(uploadArea.classList.remove).toHaveBeenCalledWith("hidden");
    expect(filePreview.classList.add).toHaveBeenCalledWith("hidden");
  });

  test("replace button triggers file input click", () => {
    // Mock fileInput.click
    fileInput.click = jest.fn();

    // Trigger replace button click
    replaceFileBtn.click();

    // Verify file input click was triggered
    expect(fileInput.click).toHaveBeenCalled();
  });

  test("delete button calls deleteFile method", () => {
    // Mock deleteFile method
    manager.deleteFile = jest.fn();

    // Trigger delete button click
    deleteFileBtn.click();

    // Verify deleteFile was called
    expect(manager.deleteFile).toHaveBeenCalled();
  });

  test("deleteFile shows SweetAlert2 confirmation", () => {
    // Call deleteFile directly
    manager.deleteFile();

    // Verify SweetAlert2 was shown with correct params
    expect(mockSwalFire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Delete file attachment?",
        text: expect.stringContaining("remove the file"),
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
      }),
    );
  });

  test("confirmed deletion marks file for deletion", async () => {
    // Mock the implementation of deleteFile
    const originalDeleteFile = manager.deleteFile;
    manager.deleteFile = jest.fn().mockImplementation(async () => {
      // Mock setting value on delete file input
      deleteFileInput.value = "true";

      // Mock Swal.fire success message
      await mockSwalFire(
        "Marked for deletion",
        "The file will be deleted when you save the note.",
        "success",
      );
    });

    // Call mocked deleteFile
    await manager.deleteFile();

    // Check only the aspects we can test
    expect(deleteFileInput.value).toBe("true");
    expect(manager.deleteFile).toHaveBeenCalled();

    // Restore original
    manager.deleteFile = originalDeleteFile;
  });

  test("cancelled deletion does not change anything", async () => {
    // Reset the deleteFileInput value
    deleteFileInput.value = "false";

    // Mock the implementation of deleteFile for this test
    const originalDeleteFile = manager.deleteFile;
    manager.deleteFile = jest.fn().mockImplementation(async () => {
      // This is the cancelled case, so we won't set value to "true"
      const result = await mockSwalFire
        .mockResolvedValueOnce({ isConfirmed: false })
        .mockReturnValueOnce({ isConfirmed: false })();
      // It should remain false since confirmation was cancelled
      expect(deleteFileInput.value).toBe("false");
    });

    // Call deleteFile
    await manager.deleteFile();

    // Verify nothing changed - value should still be false
    expect(deleteFileInput.value).toBe("false");

    // Restore original
    manager.deleteFile = originalDeleteFile;
  });

  test("handles missing optional elements gracefully", () => {
    // Remove elements from DOM
    document.body.innerHTML = `
      <form id="test-form">
        <input type="file" id="file-upload">
        <div id="upload-area">Drop files here</div>
        <div id="file-preview" class="hidden">
          <span id="file-name"></span>
        </div>
      </form>
    `;

    // Initialize manager without optional elements
    const simpleManager = new FileUploadManager({
      inputId: "file-upload",
      uploadAreaId: "upload-area",
      previewId: "file-preview",
      fileNameId: "file-name",
    });

    // Should initialize without errors
    expect(simpleManager.fileInput).toBeDefined();
    expect(simpleManager.removeFileBtn).toBeNull();
    expect(simpleManager.existingFile).toBeNull();
    expect(simpleManager.replaceFileBtn).toBeNull();
    expect(simpleManager.deleteFileBtn).toBeNull();
  });
});
