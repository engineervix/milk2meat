// Import EasyMDE and its styles
import EasyMDE from "easymde";
import "easymde/dist/easymde.min.css";
import "../css/editor.css";

// Initialize EasyMDE when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Find all elements that should be converted to EasyMDE editors
  const editorElements = document.querySelectorAll("[data-editor]");

  // Create an editor instance for each element
  editorElements.forEach(function (element) {
    const editor = new EasyMDE({
      element: element,
      spellChecker: false,
    });
  });

  // Timeline editor functionality
  const timelineEditor = document.getElementById("timeline-editor");
  if (timelineEditor) {
    initializeTimelineEditor();
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

// Export functions for reuse
export { initializeTimelineEditor };
