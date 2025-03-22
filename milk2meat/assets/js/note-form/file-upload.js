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
    this.deleteFileBtn = document.getElementById(options.deleteFileBtnId);

    // Add hidden input for tracking file deletion
    this.setupDeleteFileInput();
    this.setupEventListeners();
  }

  setupDeleteFileInput() {
    // Create a hidden input to track file deletion
    this.deleteFileInput = document.createElement("input");
    this.deleteFileInput.type = "hidden";
    this.deleteFileInput.name = "delete_upload";
    this.deleteFileInput.value = "false";

    // Add it to the form
    const form = this.fileInput.closest("form");
    if (form) {
      form.appendChild(this.deleteFileInput);
    }
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

    // Delete existing file button
    if (this.deleteFileBtn) {
      this.deleteFileBtn.addEventListener("click", () => {
        this.deleteFile();
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

    // Reset delete flag when uploading a new file
    this.deleteFileInput.value = "false";
  }

  deleteFile() {
    // Use SweetAlert2 for confirmation (global Swal object from main.js)
    Swal.fire({
      title: "Delete file attachment?",
      text: "This will remove the file from this note. This cannot be undone!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#3085d6",
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel",
    }).then((result) => {
      if (result.isConfirmed) {
        // Set the delete flag
        this.deleteFileInput.value = "true";

        // Hide existing file and show upload area
        if (this.existingFile) {
          this.existingFile.classList.add("hidden");
        }
        this.uploadArea.classList.remove("hidden");

        // Clear the file input in case there was a replacement file selected
        this.fileInput.value = "";
        this.filePreview.classList.add("hidden");

        // Show success message
        Swal.fire(
          "Marked for deletion",
          "The file will be deleted when you save the note.",
          "success",
        );
      }
    });
  }
}
