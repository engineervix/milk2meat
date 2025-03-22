/**
 * Tests for BibleBooksManager in bible-books.js
 */
import { BibleBooksManager } from "./bible-books";
import "@testing-library/jest-dom";

describe("BibleBooksManager", () => {
  // Mock DOM elements and data before each test
  let bibleManager;
  let mockInput;
  let mockBooksList;
  let mockSuggestions;
  let mockSelectedContainer;
  let mockHiddenInput;
  let mockBibleBooks;

  beforeEach(() => {
    // Create mock DOM elements
    document.body.innerHTML = `
      <input id="referenced-books" type="text" />
      <div id="book-suggestions" class="hidden">
        <ul id="book-suggestions-list"></ul>
      </div>
      <div id="selected-books-container"></div>
      <input id="referenced-books-json" type="hidden" />
    `;

    // Mock DOM elements
    mockInput = document.getElementById("referenced-books");
    mockBooksList = document.getElementById("book-suggestions-list");
    mockSuggestions = document.getElementById("book-suggestions");
    mockSelectedContainer = document.getElementById("selected-books-container");
    mockHiddenInput = document.getElementById("referenced-books-json");

    // Sample Bible books data
    mockBibleBooks = [
      { id: 1, title: "Genesis" },
      { id: 2, title: "Exodus" },
      { id: 3, title: "Leviticus" },
      { id: 4, title: "Numbers" },
      { id: 5, title: "Deuteronomy" },
    ];

    // Initialize manager
    bibleManager = new BibleBooksManager({
      inputId: "referenced-books",
      booksListId: "book-suggestions-list",
      suggestionsId: "book-suggestions",
      selectedContainerId: "selected-books-container",
      hiddenInputId: "referenced-books-json",
      bibleBooks: mockBibleBooks,
    });
  });

  afterEach(() => {
    document.body.innerHTML = "";
    jest.clearAllMocks();
  });

  test("should initialize correctly", () => {
    expect(bibleManager.input).toBe(mockInput);
    expect(bibleManager.booksList).toBe(mockBooksList);
    expect(bibleManager.suggestions).toBe(mockSuggestions);
    expect(bibleManager.selectedContainer).toBe(mockSelectedContainer);
    expect(bibleManager.hiddenInput).toBe(mockHiddenInput);
    expect(bibleManager.bibleBooks).toEqual(mockBibleBooks);
    expect(bibleManager.selectedBooks).toEqual([]);
  });

  test("should initialize with pre-selected books from hidden input", () => {
    // Set hidden input value and reinitialize
    mockHiddenInput.value = JSON.stringify([{ id: 1, title: "Genesis" }]);

    const newManager = new BibleBooksManager({
      inputId: "referenced-books",
      booksListId: "book-suggestions-list",
      suggestionsId: "book-suggestions",
      selectedContainerId: "selected-books-container",
      hiddenInputId: "referenced-books-json",
      bibleBooks: mockBibleBooks,
    });

    expect(newManager.selectedBooks).toEqual([{ id: 1, title: "Genesis" }]);
    expect(mockSelectedContainer.children.length).toBe(1);
  });

  test("should handle invalid JSON in hidden input", () => {
    // Mock console.error
    console.error = jest.fn();

    // Set invalid JSON in hidden input
    mockHiddenInput.value = "invalid-json";

    const newManager = new BibleBooksManager({
      inputId: "referenced-books",
      booksListId: "book-suggestions-list",
      suggestionsId: "book-suggestions",
      selectedContainerId: "selected-books-container",
      hiddenInputId: "referenced-books-json",
      bibleBooks: mockBibleBooks,
    });

    expect(console.error).toHaveBeenCalled();
    expect(newManager.selectedBooks).toEqual([]);
  });

  test("should filter books as user types", () => {
    // Simulate user input
    mockInput.value = "gen";
    bibleManager.handleInput();

    // Check that suggestions are shown with filtered results
    expect(mockSuggestions.classList.contains("hidden")).toBe(false);
    expect(mockBooksList.children.length).toBe(1);
    expect(mockBooksList.children[0].textContent).toBe("Genesis");
  });

  test("should hide suggestions if input is empty", () => {
    // Set input empty
    mockInput.value = "";
    bibleManager.handleInput();

    // Check that suggestions are hidden
    expect(mockSuggestions.classList.contains("hidden")).toBe(true);
    expect(mockBooksList.children.length).toBe(0);
  });

  test("should hide suggestions if no matches found", () => {
    // Set input to something that won't match
    mockInput.value = "xyz";
    bibleManager.handleInput();

    // Check that suggestions are hidden
    expect(mockSuggestions.classList.contains("hidden")).toBe(true);
    expect(mockBooksList.children.length).toBe(0);
  });

  test("should not show already selected books in suggestions", () => {
    // Add a book to selected books
    bibleManager.selectedBooks = [{ id: 1, title: "Genesis" }];

    // Search for "gen" which should match Genesis
    mockInput.value = "gen";
    bibleManager.handleInput();

    // Should not show Genesis since it's already selected
    expect(mockBooksList.children.length).toBe(0);
    expect(mockSuggestions.classList.contains("hidden")).toBe(true);
  });

  test("should add book to selection when clicked", () => {
    // Set up suggestion list
    mockInput.value = "gen";
    bibleManager.handleInput();

    // Simulate click on suggestion
    mockBooksList.children[0].click();

    // Should add to selected books
    expect(bibleManager.selectedBooks.length).toBe(1);
    expect(bibleManager.selectedBooks[0].title).toBe("Genesis");
    expect(mockSelectedContainer.children.length).toBe(1);
    expect(mockInput.value).toBe("");
    expect(mockSuggestions.classList.contains("hidden")).toBe(true);
  });

  test("should remove book when remove button is clicked", () => {
    // Add a book first
    bibleManager.selectedBooks = [{ id: 1, title: "Genesis" }];
    bibleManager.renderSelectedBooks();

    // There should be one book displayed
    expect(mockSelectedContainer.children.length).toBe(1);

    // Click remove button
    const removeBtn = mockSelectedContainer.querySelector("button");
    removeBtn.click();

    // Book should be removed
    expect(bibleManager.selectedBooks.length).toBe(0);
    expect(mockSelectedContainer.children.length).toBe(0);
  });

  test("should update hidden input when books selection changes", () => {
    // Add a book
    bibleManager.selectedBooks = [{ id: 1, title: "Genesis" }];
    bibleManager.renderSelectedBooks();

    // Hidden input should be updated
    expect(mockHiddenInput.value).toBe(
      JSON.stringify([{ id: 1, title: "Genesis" }]),
    );

    // Add another book
    bibleManager.selectedBooks.push({ id: 2, title: "Exodus" });
    bibleManager.renderSelectedBooks();

    // Hidden input should be updated again
    expect(mockHiddenInput.value).toBe(
      JSON.stringify([
        { id: 1, title: "Genesis" },
        { id: 2, title: "Exodus" },
      ]),
    );
  });

  test("should hide suggestions when clicking outside", () => {
    // Show suggestions
    mockSuggestions.classList.remove("hidden");

    // Simulate click outside
    document.dispatchEvent(new MouseEvent("click"));

    // Suggestions should be hidden
    expect(mockSuggestions.classList.contains("hidden")).toBe(true);
  });

  test("should not hide suggestions when clicking on input", () => {
    // Show suggestions
    mockSuggestions.classList.remove("hidden");

    // Simulate click on input
    mockInput.dispatchEvent(new MouseEvent("click", { bubbles: true }));

    // Suggestions should still be visible
    expect(mockSuggestions.classList.contains("hidden")).toBe(false);
  });
});
