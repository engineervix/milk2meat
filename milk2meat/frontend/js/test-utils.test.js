/**
 * @jest-environment jsdom
 */

import {
  createMockFile,
  createMockResponse,
  mockFetch,
  mockSweetAlert,
  mockFormData,
  simulateKeyEvent,
  simulateMouseEvent,
  simulateFileDrop,
  setupTestDOM,
  mockEditor,
} from "./test-utils";

describe("Test Utilities", () => {
  describe("createMockFile", () => {
    test("creates a File object with the specified name and type", () => {
      const mockFile = createMockFile("test.pdf", "application/pdf");

      expect(mockFile).toBeInstanceOf(File);
      expect(mockFile.name).toBe("test.pdf");
      expect(mockFile.type).toBe("application/pdf");
    });

    test("uses default content when not specified", () => {
      const mockFile = createMockFile("test.pdf", "application/pdf");

      // Read the file content
      const reader = new FileReader();
      reader.readAsText(mockFile);

      return new Promise((resolve) => {
        reader.onload = () => {
          expect(reader.result).toBe("test content");
          resolve();
        };
      });
    });

    test("uses custom content when provided", () => {
      const mockFile = createMockFile(
        "test.pdf",
        "application/pdf",
        "custom content",
      );

      // Read the file content
      const reader = new FileReader();
      reader.readAsText(mockFile);

      return new Promise((resolve) => {
        reader.onload = () => {
          expect(reader.result).toBe("custom content");
          resolve();
        };
      });
    });
  });

  describe("createMockResponse", () => {
    test("creates a mock Response with JSON data", async () => {
      const data = { success: true, message: "OK" };
      const mockResponse = createMockResponse(data);

      expect(mockResponse.ok).toBe(true);
      expect(mockResponse.status).toBe(200);

      const jsonResult = await mockResponse.json();
      expect(jsonResult).toEqual(data);
    });

    test("creates a mock Response with string data", async () => {
      const data = "String response";
      const mockResponse = createMockResponse(data);

      const textResult = await mockResponse.text();
      expect(textResult).toBe(data);
    });

    test("creates a mock Response with custom status", () => {
      const data = { error: "Not found" };
      const mockResponse = createMockResponse(data, false, 404);

      expect(mockResponse.ok).toBe(false);
      expect(mockResponse.status).toBe(404);
    });
  });

  describe("mockFetch", () => {
    test("returns a mock fetch function that resolves with the specified data", async () => {
      const data = { success: true };
      const fetch = mockFetch(data);

      const response = await fetch("https://example.com/api");
      const result = await response.json();

      expect(fetch).toHaveBeenCalledWith("https://example.com/api");
      expect(result).toEqual(data);
    });

    test("returns a mock fetch with custom status", async () => {
      const data = { error: "Server error" };
      const fetch = mockFetch(data, false, 500);

      const response = await fetch();

      expect(response.ok).toBe(false);
      expect(response.status).toBe(500);
    });
  });

  describe("mockSweetAlert", () => {
    test("creates a mock Swal object with default confirmation", async () => {
      const swal = mockSweetAlert();

      const result = await swal.fire({
        title: "Confirm?",
        text: "Please confirm",
      });

      expect(swal.fire).toHaveBeenCalledWith({
        title: "Confirm?",
        text: "Please confirm",
      });
      expect(result.isConfirmed).toBe(true);
    });

    test("creates a mock Swal object with specified confirmation", async () => {
      const swal = mockSweetAlert(false);

      const result = await swal.fire();

      expect(result.isConfirmed).toBe(false);
    });
  });

  describe("mockFormData", () => {
    test("creates a mock FormData with working append and get methods", () => {
      const formData = mockFormData();

      formData.append("name", "Test Name");
      formData.append("email", "test@example.com");

      expect(formData.get("name")).toBe("Test Name");
      expect(formData.get("email")).toBe("test@example.com");
    });

    test("correctly implements the has method", () => {
      const formData = mockFormData();

      formData.append("exists", "value");

      expect(formData.has("exists")).toBe(true);
      expect(formData.has("does-not-exist")).toBe(false);
    });

    test("correctly implements the set method", () => {
      const formData = mockFormData();

      formData.append("key", "original");
      expect(formData.get("key")).toBe("original");

      formData.set("key", "updated");
      expect(formData.get("key")).toBe("updated");
    });

    test("correctly implements the delete method", () => {
      const formData = mockFormData();

      formData.append("key", "value");
      expect(formData.has("key")).toBe(true);

      formData.delete("key");
      expect(formData.has("key")).toBe(false);
    });

    test("correctly implements entries, keys, and values", () => {
      const formData = mockFormData();

      formData.append("name", "Test");
      formData.append("age", "30");

      // Test entries
      const entries = Array.from(formData.entries());
      expect(entries).toEqual([
        ["name", "Test"],
        ["age", "30"],
      ]);

      // Test keys
      const keys = Array.from(formData.keys());
      expect(keys).toEqual(["name", "age"]);

      // Test values
      const values = Array.from(formData.values());
      expect(values).toEqual(["Test", "30"]);
    });
  });

  describe("simulateKeyEvent", () => {
    test("creates a keyboard event with the specified key", () => {
      const event = simulateKeyEvent("Enter");

      expect(event instanceof KeyboardEvent).toBe(true);
      expect(event.key).toBe("Enter");
      expect(event.bubbles).toBe(true);
      expect(event.cancelable).toBe(true);
    });

    test("creates a keyboard event with additional options", () => {
      const event = simulateKeyEvent("a", { ctrlKey: true, metaKey: true });

      expect(event.key).toBe("a");
      expect(event.ctrlKey).toBe(true);
      expect(event.metaKey).toBe(true);
    });
  });

  describe("simulateMouseEvent", () => {
    test("dispatches a mouse event on the specified element", () => {
      // Create a test element
      const element = document.createElement("button");
      document.body.appendChild(element);

      // Add click event listener with jest spy
      const clickHandler = jest.fn();
      element.addEventListener("click", clickHandler);

      // Simulate mouse event
      simulateMouseEvent(element, "click");

      // Verify event was dispatched
      expect(clickHandler).toHaveBeenCalled();

      // Clean up
      document.body.removeChild(element);
    });
  });

  describe("simulateFileDrop", () => {
    test("simulates drag and drop operations on an element", () => {
      // Create a test element and mock files
      const dropTarget = document.createElement("div");
      document.body.appendChild(dropTarget);

      const mockFiles = [
        createMockFile("test1.pdf", "application/pdf"),
        createMockFile("test2.pdf", "application/pdf"),
      ];

      // Add drag event listeners with jest spies
      const dragoverHandler = jest.fn((e) => e.preventDefault());
      const dropHandler = jest.fn((e) => e.preventDefault());

      dropTarget.addEventListener("dragover", dragoverHandler);
      dropTarget.addEventListener("drop", dropHandler);

      // Simulate file drop
      simulateFileDrop(dropTarget, mockFiles);

      // Verify event handlers were called
      expect(dragoverHandler).toHaveBeenCalled();
      expect(dropHandler).toHaveBeenCalled();

      // Clean up
      document.body.removeChild(dropTarget);
    });
  });

  describe("setupTestDOM", () => {
    test("creates DOM structure from provided HTML and returns elements", () => {
      const formHtml = `
        <form id="test-form">
          <input name="test-input">
          <button type="submit">Submit</button>
        </form>
      `;

      const { form, submitButton } = setupTestDOM(formHtml);

      expect(form).toBeTruthy();
      expect(form.id).toBe("test-form");
      expect(submitButton).toBeTruthy();
      expect(submitButton.textContent).toBe("Submit");
    });
  });

  describe("mockEditor", () => {
    test("creates a mock editor instance with codemirror.save method", () => {
      const editor = mockEditor();

      expect(editor.codemirror).toBeDefined();
      expect(typeof editor.codemirror.save).toBe("function");

      // Should be a jest.fn()
      editor.codemirror.save();
      expect(editor.codemirror.save).toHaveBeenCalled();
    });
  });
});
