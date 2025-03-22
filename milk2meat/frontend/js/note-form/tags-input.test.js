/**
 * @jest-environment jsdom
 */

import { TagsManager } from "./tags-input";

describe("TagsManager", () => {
  // DOM elements used by TagsManager
  let tagsInput;
  let hiddenInput;
  let tagsContainer;
  let tagsManager;

  beforeEach(() => {
    // Set up the DOM elements
    document.body.innerHTML = `
      <input id="tags-input" type="text" />
      <input id="tags-hidden" type="hidden" />
      <div id="tags-container"></div>
    `;

    tagsInput = document.getElementById("tags-input");
    hiddenInput = document.getElementById("tags-hidden");
    tagsContainer = document.getElementById("tags-container");

    // Create a new TagsManager instance
    tagsManager = new TagsManager({
      inputId: "tags-input",
      hiddenInputId: "tags-hidden",
      containerId: "tags-container",
    });
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  describe("initialization", () => {
    test("initializes with empty tags array by default", () => {
      expect(tagsManager.tags).toEqual([]);
      expect(tagsContainer.innerHTML).toBe("");
    });

    test("loads existing tags from hidden input", () => {
      // Setup hidden input with pre-existing tags
      hiddenInput.value = "javascript,testing,jest";

      // Create a new manager to trigger initialization
      tagsManager = new TagsManager({
        inputId: "tags-input",
        hiddenInputId: "tags-hidden",
        containerId: "tags-container",
      });

      // Check tags array and rendered elements
      expect(tagsManager.tags).toEqual(["javascript", "testing", "jest"]);
      expect(tagsContainer.children.length).toBe(3);
      expect(tagsContainer.children[0].textContent).toMatch(/javascript/);
    });
  });

  describe("addTag", () => {
    test("adds a tag when Enter key is pressed", () => {
      // Simulate typing in the input
      tagsInput.value = "javascript";

      // Simulate Enter key press
      const event = new KeyboardEvent("keydown", { key: "Enter" });
      tagsInput.dispatchEvent(event);

      // Check if tag was added
      expect(tagsManager.tags).toEqual(["javascript"]);
      expect(tagsContainer.children.length).toBe(1);
      expect(hiddenInput.value).toBe("javascript");
      expect(tagsInput.value).toBe("");
    });

    test("adds a tag when comma key is pressed", () => {
      // Simulate typing in the input
      tagsInput.value = "testing";

      // Simulate comma key press
      const event = new KeyboardEvent("keydown", { key: "," });
      tagsInput.dispatchEvent(event);

      // Check if tag was added
      expect(tagsManager.tags).toEqual(["testing"]);
      expect(tagsContainer.children.length).toBe(1);
      expect(hiddenInput.value).toBe("testing");
    });

    test("adds a tag when input loses focus", () => {
      // Simulate typing in the input
      tagsInput.value = "jest";

      // Simulate blur event
      tagsInput.dispatchEvent(new Event("blur"));

      // Check if tag was added
      expect(tagsManager.tags).toEqual(["jest"]);
      expect(tagsContainer.children.length).toBe(1);
      expect(hiddenInput.value).toBe("jest");
    });

    test("handles multiple comma-separated tags", () => {
      // Simulate typing multiple tags
      tagsInput.value = "unit,integration,e2e";

      // Simulate blur event
      tagsInput.dispatchEvent(new Event("blur"));

      // Check if all tags were added
      expect(tagsManager.tags).toEqual(["unit", "integration", "e2e"]);
      expect(tagsContainer.children.length).toBe(3);
      expect(hiddenInput.value).toBe("unit,integration,e2e");
    });

    test("doesn't add duplicate tags", () => {
      // Add first tag
      tagsInput.value = "javascript";
      tagsInput.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter" }));

      // Try to add same tag again
      tagsInput.value = "javascript";
      tagsInput.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter" }));

      // Check if tag was added only once
      expect(tagsManager.tags).toEqual(["javascript"]);
      expect(tagsContainer.children.length).toBe(1);
    });

    test("doesn't add empty tags", () => {
      // Try to add empty tag
      tagsInput.value = "   ";
      tagsInput.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter" }));

      // Check no tags were added
      expect(tagsManager.tags).toEqual([]);
      expect(tagsContainer.children.length).toBe(0);
    });
  });

  describe("removeTag", () => {
    test("removes a tag when its remove button is clicked", () => {
      // Add some tags first
      tagsManager.tags = ["tag1", "tag2", "tag3"];
      tagsManager.renderTags();

      // Initial state check
      expect(tagsContainer.children.length).toBe(3);

      // Find and click the remove button for the second tag
      const removeBtn = tagsContainer.children[1].querySelector("button");
      removeBtn.dispatchEvent(new Event("click"));

      // Check if tag was removed
      expect(tagsManager.tags).toEqual(["tag1", "tag3"]);
      expect(tagsContainer.children.length).toBe(2);
      expect(hiddenInput.value).toBe("tag1,tag3");
    });
  });
});
