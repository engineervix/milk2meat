/**
 * Manages the note type form functionality
 */
export class NoteTypeManager {
  constructor(options) {
    this.form = document.getElementById(options.formId);
    this.nameInput = document.getElementById(options.nameInputId);
    this.descInput = document.getElementById(options.descInputId);
    this.nameError = document.getElementById(options.nameErrorId);
    this.modal = document.getElementById(options.modalId);
    this.noteTypeSelect = document.getElementById(options.selectId);
    this.csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    this.createUrl = options.createUrl;

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
  }

  async handleSubmit(e) {
    e.preventDefault();

    // Reset error state
    this.nameError.classList.add("hidden");

    // Get form data
    const formData = new FormData();
    formData.append("name", this.nameInput.value.trim());
    formData.append("description", this.descInput.value.trim());
    formData.append("csrfmiddlewaretoken", this.csrfToken);

    try {
      const response = await fetch(this.createUrl, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Add new option to select
        const option = document.createElement("option");
        option.value = data.id;
        option.textContent = data.name;
        option.selected = true;
        this.noteTypeSelect.appendChild(option);

        // Close modal and reset form
        this.modal.close();
        this.form.reset();
      } else {
        // Show error message
        if (data.errors && data.errors.name) {
          this.nameError.textContent = data.errors.name[0];
          this.nameError.classList.remove("hidden");
        }
      }
    } catch (error) {
      console.error("Error creating note type:", error);
    }
  }
}
