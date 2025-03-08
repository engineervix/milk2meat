// Import EasyMDE and its styles
import EasyMDE from "easymde";
import "easymde/dist/easymde.min.css";
import "../css/editor.css";

// Initialize EasyMDE when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Find all elements that should be converted to EasyMDE editors
  const editorElements = document.querySelectorAll("[data-editor]");

  // Track whether form has unsaved changes
  let formChanged = false;

  // Array to store editor instances
  const editors = [];

  // Create an editor instance for each element
  editorElements.forEach(function (element) {
    const editor = new EasyMDE({
      element: element,
      spellChecker: false,
      minHeight: "300px", // Add a reasonable min height for all editors
    });

    // Add change event listener to track unsaved changes
    editor.codemirror.on("change", function () {
      formChanged = true;
    });

    editors.push(editor);
  });

  // Timeline editor functionality
  const timelineEditor = document.getElementById("timeline-editor");
  if (timelineEditor) {
    initializeTimelineEditor();
  }

  // Set up beforeunload event to catch page navigation with unsaved changes
  if (document.querySelector("form")) {
    // Make formChanged accessible to other functions
    window.formChanged = formChanged;

    // Also track form input changes for non-editor fields
    document.querySelector("form").addEventListener("input", function (e) {
      if (!e.target.matches("[data-editor]")) {
        // Avoid double-tracking editor changes
        window.formChanged = true;
      }
    });

    // Add event listener for beforeunload to warn about unsaved changes
    // https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event
    window.addEventListener("beforeunload", function (e) {
      if (window.formChanged) {
        e.preventDefault();
      }
      return undefined;
    });

    // Listen for form submission to prevent the warning when form is properly submitted
    document.querySelector("form").addEventListener("submit", function () {
      window.formChanged = false;
    });

    // Handle cancel button click
    const cancelButton = document.getElementById("cancel-edit-btn");
    if (cancelButton) {
      cancelButton.addEventListener("click", function (e) {
        // If there are unsaved changes, ask for confirmation before navigating away
        if (window.formChanged) {
          if (
            !confirm(
              "You have unsaved changes. Are you sure you want to leave this page?",
            )
          ) {
            e.preventDefault();
          } else {
            window.formChanged = false; // Don't show the beforeunload dialog if user confirmed
          }
        }
      });
    }
  }
});

// Timeline editor functionality
function initializeTimelineEditor() {
  const timelineEvents = document.getElementById("timeline-events");
  const timelineData = document.getElementById("timeline-data");
  const addEventButton = document.getElementById("add-timeline-event");

  let timelineItems = [];

  // Load existing timeline data if available
  if (timelineData.value) {
    try {
      const parsedData = JSON.parse(timelineData.value);
      timelineItems = parsedData.events || [];
      renderTimelineEvents();
    } catch (e) {
      console.error("Error parsing timeline data:", e);
      timelineItems = [];
    }
  }

  // Add new event handler
  addEventButton.addEventListener("click", function () {
    timelineItems.push({
      date: "",
      description: "",
    });
    renderTimelineEvents();
    updateTimelineData();
  });

  // Render timeline events
  function renderTimelineEvents() {
    timelineEvents.innerHTML = "";

    if (timelineItems.length === 0) {
      const emptyMessage = document.createElement("div");
      emptyMessage.className = "p-4 text-center text-base-content/60";
      emptyMessage.textContent =
        'No timeline events yet. Click "Add Event" to create one.';
      timelineEvents.appendChild(emptyMessage);
      return;
    }

    timelineItems.forEach((item, index) => {
      const eventElement = document.createElement("div");
      eventElement.className = "timeline-event mb-4 p-4 rounded-lg bg-base-200";
      eventElement.dataset.index = index;

      eventElement.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Date</span>
            </label>
            <input type="text" class="input input-bordered timeline-date"
                   value="${item.date}" placeholder="e.g., 1010-971 B.C.">
          </div>
          <div class="form-control md:col-span-2">
            <label class="label">
              <span class="label-text">Description</span>
            </label>
            <input type="text" class="input input-bordered timeline-description"
                   value="${item.description}" placeholder="e.g., Reign of David">
          </div>
        </div>
        <div class="timeline-event-actions mt-2 flex justify-end">
          <button type="button" class="btn btn-sm btn-outline btn-error delete-event">Remove</button>
        </div>
      `;

      // Add event listeners
      const dateInput = eventElement.querySelector(".timeline-date");
      const descriptionInput = eventElement.querySelector(
        ".timeline-description",
      );
      const deleteButton = eventElement.querySelector(".delete-event");

      dateInput.addEventListener("input", function () {
        timelineItems[index].date = this.value;
        updateTimelineData();
      });

      descriptionInput.addEventListener("input", function () {
        timelineItems[index].description = this.value;
        updateTimelineData();
      });

      deleteButton.addEventListener("click", function () {
        timelineItems.splice(index, 1);
        renderTimelineEvents();
        updateTimelineData();
      });

      timelineEvents.appendChild(eventElement);
    });
  }

  // Update hidden input with timeline data
  function updateTimelineData() {
    timelineData.value = JSON.stringify({
      events: timelineItems,
    });
  }
}
