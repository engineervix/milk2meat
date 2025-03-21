/**
 * Handles AJAX form submission for notes
 */
export class AjaxFormManager {
  constructor(options) {
    this.form = document.querySelector(options.formSelector || "form");
    this.submitBtn = this.form.querySelector('[type="submit"]');
    this.editorInstances = options.editorInstances || [];
    this.messageContainer = document.getElementById(options.messageContainerId);
    this.csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    this.createUrl = options.createUrl;
    this.updateUrl = options.updateUrl;
    this.noteId = options.noteId;

    // Track form submission state
    this.isSubmitting = false;

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
  }

  async handleSubmit(e) {
    // Prevent traditional form submission
    e.preventDefault();

    // Prevent double submission
    if (this.isSubmitting) return;

    this.isSubmitting = true;

    // Show loading state
    const originalBtnText = this.submitBtn.innerHTML;
    this.submitBtn.disabled = true;
    this.submitBtn.innerHTML = `
      <span class="loading loading-spinner loading-xs"></span>
      Saving...
    `;

    try {
      // Sync editor content to textarea fields if EasyMDE is used
      if (this.editorInstances.length > 0) {
        this.editorInstances.forEach((editor) => {
          editor.codemirror.save();
        });
      }

      // Create FormData from the form
      const formData = new FormData(this.form);

      // Use the appropriate URL (update URL is already set correctly by the template)
      const url = this.noteId ? this.updateUrl : this.createUrl;

      // Submit the form
      const response = await fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
      });

      const data = await response.json();

      if (data.success) {
        // Show success message
        this.showMessage(data.message, "success");

        // For newly created notes, update the form to edit mode
        if (data.is_new) {
          // Update note ID
          this.noteId = data.note.id;

          // Update page URL (for browser history and refresh)
          window.history.pushState({}, "", data.note.edit_url);

          // Update document title
          document.title = document.title.replace(
            "New Note",
            `Edit ${data.note.title}`,
          );

          // Update heading if present
          const heading = document.querySelector(".promo-heading");
          if (heading) {
            heading.textContent = "Edit Note";
          }

          // Update the update URL for future saves
          this.updateUrl = data.note.edit_url
            .replace("/edit/", "/update/")
            .replace("/core/", "/api/");
        }

        // Reset the form changed state since we just saved
        if (window.formChanged !== undefined) {
          window.formChanged = false;
        }
      } else {
        // Display validation errors
        this.displayErrors(
          data.errors || { _form: [data.error || "An unknown error occurred"] },
        );
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      this.showMessage("Failed to save. Please try again.", "error");
    } finally {
      // Restore button state
      this.submitBtn.disabled = false;
      this.submitBtn.innerHTML = originalBtnText;
      this.isSubmitting = false;
    }
  }

  /**
   * Displays a message to the user
   */
  showMessage(message, type = "success") {
    if (!this.messageContainer) {
      // If no container specified, use toast notification
      this.showToast(message, type);
      return;
    }

    // Clear existing messages
    this.messageContainer.innerHTML = "";

    // Create alert
    const alertClass = type === "success" ? "alert-success" : "alert-error";
    this.messageContainer.innerHTML = `
      <div class="alert ${alertClass} shadow-lg mb-4">
        <div>
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${type === "success" ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" : "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"}" />
          </svg>
          <span>${message}</span>
        </div>
      </div>
    `;

    // Auto-hide message after a delay
    setTimeout(() => {
      const alert = this.messageContainer.querySelector(".alert");
      if (alert) {
        alert.style.opacity = "0";
        alert.style.transition = "opacity 0.5s";
        setTimeout(() => {
          this.messageContainer.innerHTML = "";
        }, 500);
      }
    }, 5000);
  }

  /**
   * Shows a toast notification
   */
  showToast(message, type = "success") {
    // Create toast element
    const toast = document.createElement("div");
    toast.className = `toast toast-end ${type === "success" ? "toast-success" : "toast-error"}`;
    toast.innerHTML = `
      <div class="alert">
        <span>${message}</span>
      </div>
    `;

    // Add to document
    document.body.appendChild(toast);

    // Remove after delay
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.5s";
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 500);
    }, 5000);
  }

  /**
   * Displays validation errors on the form
   */
  displayErrors(errors) {
    // Clear any existing error messages
    this.form.querySelectorAll(".text-error").forEach((el) => {
      el.textContent = "";
      el.closest(".label")?.classList.add("hidden");
    });

    // Display new error messages
    for (const field in errors) {
      const errorMessage = Array.isArray(errors[field])
        ? errors[field].join(", ")
        : errors[field];

      if (field === "_form") {
        // General form error
        this.showMessage(errorMessage, "error");
        continue;
      }

      // Find the error container for this field
      let errorEl;

      // Handle special case for hidden inputs
      if (field === "tags_input") {
        errorEl = document
          .querySelector("#tags-container")
          .nextElementSibling?.querySelector(".text-error");
      } else if (field === "referenced_books_json") {
        errorEl = document
          .querySelector("#selected-books-container")
          .nextElementSibling?.querySelector(".text-error");
      } else {
        // Try to find the standard error container
        const inputEl = this.form.querySelector(`[name="${field}"]`);
        if (inputEl) {
          errorEl = inputEl.nextElementSibling?.querySelector(".text-error");
          if (!errorEl) {
            // Try to find label error
            errorEl = inputEl
              .closest(".form-control")
              ?.querySelector(".label .text-error");
          }
        }
      }

      // Display the error if we found an element
      if (errorEl) {
        errorEl.textContent = errorMessage;
        errorEl.closest(".label")?.classList.remove("hidden");
      } else {
        // Fall back to generic message
        this.showMessage(`${field}: ${errorMessage}`, "error");
      }
    }
  }
}
