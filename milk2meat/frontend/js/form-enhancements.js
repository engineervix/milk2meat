/**
 * Form Enhancements Module
 *
 * Adds usability improvements to forms:
 * 1. Keyboard shortcuts (Ctrl+S / Cmd+S) for saving forms
 * 2. Floating action button for easy access to save functionality
 */

class FormEnhancer {
  constructor({
    formSelector,
    submitButtonSelector = 'button[type="submit"]',
    cancelButtonSelector = "#cancel-edit-btn",
    fabPosition = "bottom-right", // Possible values: "bottom-right", "bottom-center", "bottom-left"
    fabLabel = "Save",
    fabIcon = '<i class="ph ph-floppy-disk text-xl"></i>',
    enableKeyboardShortcuts = true,
    enableFloatingButton = true,
  }) {
    this.formSelector = formSelector;
    this.submitButtonSelector = submitButtonSelector;
    this.cancelButtonSelector = cancelButtonSelector;
    this.fabPosition = fabPosition;
    this.fabLabel = fabLabel;
    this.fabIcon = fabIcon;
    this.enableKeyboardShortcuts = enableKeyboardShortcuts;
    this.enableFloatingButton = enableFloatingButton;

    this.form = document.querySelector(this.formSelector);
    this.submitButton = this.form
      ? this.form.querySelector(this.submitButtonSelector)
      : null;
    this.cancelButton = document.querySelector(this.cancelButtonSelector);

    this.init();
  }

  init() {
    if (!this.form || !this.submitButton) {
      console.error("Form or submit button not found");
      return;
    }

    if (this.enableKeyboardShortcuts) {
      this.setupKeyboardShortcuts();
    }

    if (this.enableFloatingButton) {
      this.createFloatingActionButton();
    }
  }

  setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
      // Check for Ctrl+S or Cmd+S (Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault(); // Prevent browser save dialog
        this.saveForm();
      }
    });
  }

  createFloatingActionButton() {
    // Create the FAB element
    const fab = document.createElement("button");
    fab.className = `fab fab-${this.fabPosition} btn btn-primary btn-circle fixed shadow-lg z-50 flex items-center justify-center`;
    fab.setAttribute("title", `${this.fabLabel} (Ctrl+S / Cmd+S)`);
    fab.innerHTML = this.fabIcon;

    // Set position based on fabPosition
    switch (this.fabPosition) {
      case "bottom-right":
        fab.style.cssText = "bottom: 2rem; right: 2rem;";
        break;
      case "bottom-center":
        fab.style.cssText =
          "bottom: 2rem; left: 50%; transform: translateX(-50%);";
        break;
      case "bottom-left":
        fab.style.cssText = "bottom: 2rem; left: 2rem;";
        break;
      default:
        fab.style.cssText = "bottom: 2rem; right: 2rem;";
    }

    // Add click event listener to submit the form
    fab.addEventListener("click", (e) => {
      e.preventDefault();
      this.saveForm();
    });

    // Add the FAB to the document
    document.body.appendChild(fab);

    // Add styles for the FAB to handle hover state and transitions
    const style = document.createElement("style");
    style.textContent = `
      .fab {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      .fab:hover {
        transform: scale(1.1);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      }
      .fab-bottom-center:hover {
        transform: translateX(-50%) scale(1.1);
      }
    `;
    document.head.appendChild(style);

    // Show label on hover with tooltip
    // DaisyUI already has tooltip functionality through data attributes
    fab.setAttribute("data-tip", this.fabLabel);
    fab.classList.add("tooltip", "tooltip-left");
  }

  saveForm() {
    if (this.form && this.submitButton) {
      // If we have EasyMDE instances, sync them before submission
      if (window.editors && window.editors.length > 0) {
        window.editors.forEach((editor) => {
          editor.codemirror.save();
        });
      }

      // Click the submit button to trigger the form submission
      this.submitButton.click();
    }
  }
}

export { FormEnhancer };
