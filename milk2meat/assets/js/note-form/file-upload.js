/**
 * Manages the file upload functionality
 */
export class FileUploadManager {
  constructor(options) {
    this.fileInput = document.getElementById(options.inputId);
    this.uploadArea = document.getElementById(options.uploadAreaId);
    this.filePreview = document.getElementById(options.previewId);
    this.fileName = document.getElementById(options.fileNameId);
    this.removeFileBtn = document.getElementById(options.removeFileBtnId);
    this.existingFile = document.getElementById(options.existingFileId);
    this.replaceFileBtn = document.getElementById(options.replaceFileBtnId);

    this.setupEventListeners();
  }

  setupEventListeners() {
    // Handle file selection
    this.fileInput.addEventListener("change", () => {
      if (this.fileInput.files && this.fileInput.files[0]) {
        this.showFilePreview(this.fileInput.files[0]);
      }
    });

    // Handle drag and drop
    this.uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.uploadArea.classList.add("border-primary");
    });

    this.uploadArea.addEventListener("dragleave", () => {
      this.uploadArea.classList.remove("border-primary");
    });

    this.uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      this.uploadArea.classList.remove("border-primary");

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.fileInput.files = e.dataTransfer.files;
        this.showFilePreview(e.dataTransfer.files[0]);
      }
    });

    // Remove file button
    if (this.removeFileBtn) {
      this.removeFileBtn.addEventListener("click", () => {
        this.fileInput.value = "";
        this.uploadArea.classList.remove("hidden");
        this.filePreview.classList.add("hidden");
      });
    }

    // Replace existing file button
    if (this.replaceFileBtn) {
      this.replaceFileBtn.addEventListener("click", () => {
        this.fileInput.click();
      });
    }
  }

  showFilePreview(file) {
    this.fileName.textContent = file.name;
    this.uploadArea.classList.add("hidden");
    this.filePreview.classList.remove("hidden");

    if (this.existingFile) {
      this.existingFile.classList.add("hidden");
    }
  }
}
