/**
 * Manages the tags input functionality
 */
export class TagsManager {
  constructor(options) {
    this.tagsInput = document.getElementById(options.inputId);
    this.hiddenInput = document.getElementById(options.hiddenInputId);
    this.tagsContainer = document.getElementById(options.containerId);
    this.tags = [];

    // Initialize tags from hidden input if exists
    if (this.hiddenInput.value) {
      this.tags = this.hiddenInput.value.split(",");
      this.renderTags();
    }

    this.setupEventListeners();
  }

  setupEventListeners() {
    // Add tags when pressing Enter or comma
    this.tagsInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === ",") {
        e.preventDefault();
        this.addTag();
      }
    });

    // Also add tags when input loses focus
    this.tagsInput.addEventListener("blur", () => this.addTag());
  }

  addTag() {
    const value = this.tagsInput.value.trim();
    if (value && !value.includes(",")) {
      if (!this.tags.includes(value)) {
        this.tags.push(value);
        this.renderTags();
      }
      this.tagsInput.value = "";
    } else if (value && value.includes(",")) {
      // Handle multiple tags separated by commas
      const newTags = value
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag && !this.tags.includes(tag));

      this.tags.push(...newTags);
      this.renderTags();
      this.tagsInput.value = "";
    }
  }

  renderTags() {
    this.tagsContainer.innerHTML = "";
    this.tags.forEach((tag, index) => {
      const badge = document.createElement("div");
      badge.className = "badge badge-lg gap-1";
      badge.textContent = tag;

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "btn-xs btn-ghost rounded-full";
      removeBtn.textContent = "✕";
      removeBtn.addEventListener("click", () => {
        this.tags.splice(index, 1);
        this.renderTags();
      });

      badge.appendChild(removeBtn);
      this.tagsContainer.appendChild(badge);
    });

    // Update hidden input
    this.hiddenInput.value = this.tags.join(",");
  }
}
