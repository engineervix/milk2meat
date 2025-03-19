/**
 * Manages the Bible books autocomplete functionality
 */
export class BibleBooksManager {
  constructor(options) {
    this.input = document.getElementById(options.inputId);
    this.booksList = document.getElementById(options.booksListId);
    this.suggestions = document.getElementById(options.suggestionsId);
    this.selectedContainer = document.getElementById(
      options.selectedContainerId,
    );
    this.hiddenInput = document.getElementById(options.hiddenInputId);
    this.bibleBooks = options.bibleBooks || [];
    this.selectedBooks = [];

    // Initialize selected books from hidden input if exists
    if (this.hiddenInput.value) {
      try {
        this.selectedBooks = JSON.parse(this.hiddenInput.value);
        this.renderSelectedBooks();
      } catch (e) {
        console.error("Error parsing books JSON:", e);
      }
    }

    this.setupEventListeners();
  }

  setupEventListeners() {
    // Filter books as user types
    this.input.addEventListener("input", () => this.handleInput());

    // Hide suggestions when clicking outside
    document.addEventListener("click", (e) => {
      if (!this.suggestions.contains(e.target) && e.target !== this.input) {
        this.suggestions.classList.add("hidden");
      }
    });
  }

  handleInput() {
    const value = this.input.value.toLowerCase();
    if (value.length < 1) {
      this.suggestions.classList.add("hidden");
      return;
    }

    // Filter books by input value
    const matches = this.bibleBooks.filter(
      (book) =>
        book.title.toLowerCase().includes(value) &&
        !this.selectedBooks.some((selected) => selected.id === book.id),
    );

    this.renderSuggestions(matches);
  }

  renderSuggestions(matches) {
    this.booksList.innerHTML = "";
    if (matches.length > 0) {
      matches.forEach((book) => {
        const li = document.createElement("li");
        li.className = "px-4 py-2 hover:bg-base-200 cursor-pointer";
        li.textContent = book.title;
        li.dataset.id = book.id;

        li.addEventListener("click", () => {
          this.selectedBooks.push({
            id: book.id,
            title: book.title,
          });
          this.renderSelectedBooks();
          this.input.value = "";
          this.suggestions.classList.add("hidden");
        });

        this.booksList.appendChild(li);
      });
      this.suggestions.classList.remove("hidden");
    } else {
      this.suggestions.classList.add("hidden");
    }
  }

  renderSelectedBooks() {
    this.selectedContainer.innerHTML = "";
    this.selectedBooks.forEach((book, index) => {
      const badge = document.createElement("div");
      badge.className = "badge badge-lg gap-1";
      badge.textContent = book.title;

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "btn-xs btn-ghost rounded-full";
      removeBtn.textContent = "✕";
      removeBtn.addEventListener("click", () => {
        this.selectedBooks.splice(index, 1);
        this.renderSelectedBooks();
      });

      badge.appendChild(removeBtn);
      this.selectedContainer.appendChild(badge);
    });

    // Update hidden input
    this.hiddenInput.value = JSON.stringify(this.selectedBooks);
  }
}
