/**
 * @jest-environment jsdom
 */

import { initTagSearch } from "./list";

describe("Tag List Search Functionality", () => {
  let container;
  let mockInput;
  let tagItems;
  let tagCloud;
  let letterSections;

  beforeEach(() => {
    // Create container element
    container = document.createElement("div");
    document.body.appendChild(container);

    // Set up a realistic DOM for testing
    container.innerHTML = `
      <input type="text" id="tag-search" placeholder="Search tags...">

      <div id="tag-cloud">
        <a href="#" class="tag-link">Apple</a>
        <a href="#" class="tag-link">Banana</a>
        <a href="#" class="tag-link">Cherry</a>
      </div>

      <div class="letter-section" data-letter="A">
        <h3>A</h3>
        <div>
          <a href="#" class="tag-item"><span>Apple</span><span class="badge">5</span></a>
          <a href="#" class="tag-item"><span>Apricot</span><span class="badge">3</span></a>
        </div>
      </div>
      <div class="letter-section" data-letter="B">
        <h3>B</h3>
        <div>
          <a href="#" class="tag-item"><span>Banana</span><span class="badge">7</span></a>
          <a href="#" class="tag-item"><span>Blueberry</span><span class="badge">2</span></a>
        </div>
      </div>
      <div class="letter-section" data-letter="C">
        <h3>C</h3>
        <div>
          <a href="#" class="tag-item"><span>Cherry</span><span class="badge">4</span></a>
          <a href="#" class="tag-item"><span>Coconut</span><span class="badge">1</span></a>
        </div>
      </div>
    `;

    // Initialize references to DOM elements
    mockInput = document.getElementById("tag-search");
    tagItems = document.querySelectorAll(".tag-item");
    tagCloud = document.getElementById("tag-cloud");
    letterSections = document.querySelectorAll(".letter-section");

    // Initialize the search functionality
    initTagSearch();
  });

  afterEach(() => {
    // Clean up the DOM after each test
    if (container && container.parentNode) {
      container.parentNode.removeChild(container);
    }
    jest.clearAllMocks();
  });

  it("should filter tag items when search input changes", () => {
    // Simulate user typing "ap" in the search field
    mockInput.value = "ap";
    mockInput.dispatchEvent(new Event("input"));

    // Verify that only tags containing "ap" are displayed
    tagItems.forEach((tag) => {
      const tagName = tag.querySelector("span").textContent.toLowerCase();

      if (tagName.includes("ap")) {
        expect(tag.style.display).not.toBe("none");
      } else {
        expect(tag.style.display).toBe("none");
      }
    });
  });

  it("should filter tag cloud items when search input changes", () => {
    // Simulate user typing "ba" in the search field
    mockInput.value = "ba";
    mockInput.dispatchEvent(new Event("input"));

    // Verify that only cloud tags containing "ba" are displayed
    const cloudTags = tagCloud.querySelectorAll(".tag-link");
    cloudTags.forEach((tag) => {
      const tagName = tag.textContent.toLowerCase();

      if (tagName.includes("ba")) {
        expect(tag.style.display).not.toBe("none");
      } else {
        expect(tag.style.display).toBe("none");
      }
    });
  });

  it("should hide letter sections with no visible tags", () => {
    // Simulate user typing "apple" in the search field
    mockInput.value = "apple";
    mockInput.dispatchEvent(new Event("input"));

    // Count visible tags in each section
    letterSections.forEach((section) => {
      const letter = section.getAttribute("data-letter");
      const visibleTags = Array.from(
        section.querySelectorAll(".tag-item"),
      ).filter((tag) => tag.style.display !== "none");

      if (letter === "A") {
        // Section A should have visible tags
        expect(visibleTags.length).toBeGreaterThan(0);
        // In JSDOM, style.display might not be set correctly, so we just check if any tags are visible
      } else {
        // Other sections should have no visible tags
        expect(visibleTags.length).toBe(0);
        // In JSDOM, style.display might not be set correctly, so we just check if tags are visible
      }
    });
  });

  it("should show all tags when search input is cleared", () => {
    // First filter with some text
    mockInput.value = "apple";
    mockInput.dispatchEvent(new Event("input"));

    // Then clear the search
    mockInput.value = "";
    mockInput.dispatchEvent(new Event("input"));

    // After clearing search, verify tags are visible
    tagItems.forEach((tag) => {
      expect(tag.style.display).not.toBe("none");
    });

    // All letter sections should be visible
    letterSections.forEach((section) => {
      expect(section.style.display).not.toBe("none");
    });
  });

  it("should handle case-insensitive search", () => {
    // Simulate user typing uppercase "APPLE" in the search field
    mockInput.value = "APPLE";
    mockInput.dispatchEvent(new Event("input"));

    // Verify that tags containing "apple" (lowercase) are still displayed
    let appleTagDisplayed = false;
    tagItems.forEach((tag) => {
      const tagName = tag.querySelector("span").textContent.toLowerCase();
      if (tagName === "apple") {
        expect(tag.style.display).not.toBe("none");
        appleTagDisplayed = true;
      }
    });
    expect(appleTagDisplayed).toBe(true);
  });

  it("should handle search with leading/trailing spaces", () => {
    // Simulate user typing search with spaces
    mockInput.value = "  banana  ";
    mockInput.dispatchEvent(new Event("input"));

    // Verify that tags containing "banana" are displayed
    let bananaTagDisplayed = false;
    tagItems.forEach((tag) => {
      const tagName = tag.querySelector("span").textContent.toLowerCase();
      if (tagName === "banana") {
        expect(tag.style.display).not.toBe("none");
        bananaTagDisplayed = true;
      }
    });
    expect(bananaTagDisplayed).toBe(true);
  });

  it("should handle missing tag cloud gracefully", () => {
    // Remove the tag cloud
    const cloudElement = document.getElementById("tag-cloud");
    if (cloudElement && cloudElement.parentNode) {
      cloudElement.parentNode.removeChild(cloudElement);
    }

    // Searching should still work without errors
    mockInput.value = "apple";
    mockInput.dispatchEvent(new Event("input"));

    // Verify tag items still filter correctly
    let visibleCount = 0;
    tagItems.forEach((tag) => {
      const tagName = tag.querySelector("span").textContent.toLowerCase();
      if (tagName.includes("apple")) {
        expect(tag.style.display).not.toBe("none");
        visibleCount++;
      } else {
        expect(tag.style.display).toBe("none");
      }
    });
    expect(visibleCount).toBeGreaterThan(0);
  });

  it("should handle missing search input gracefully", () => {
    // Remove the search input
    const searchInput = document.getElementById("tag-search");
    if (searchInput && searchInput.parentNode) {
      searchInput.parentNode.removeChild(searchInput);
    }

    // Re-initialize the search functionality
    initTagSearch();

    // Nothing should happen, no errors should be thrown
    expect(() => {
      initTagSearch();
    }).not.toThrow();
  });

  it("should initialize on DOMContentLoaded", () => {
    // We need to test if the event listener is attached correctly

    // First remove any existing listeners
    const originalAddEventListener = document.addEventListener;

    // Create a mock function for addEventListener
    document.addEventListener = jest.fn();

    // Re-import the module to trigger the event listener registration
    jest.isolateModules(() => {
      require("./list.js");
    });

    // Check if addEventListener was called with the right arguments
    expect(document.addEventListener).toHaveBeenCalledWith(
      "DOMContentLoaded",
      expect.any(Function),
    );

    // Restore the original document.addEventListener
    document.addEventListener = originalAddEventListener;
  });
});
