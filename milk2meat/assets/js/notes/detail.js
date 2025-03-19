/**
 * Handle secure file downloads and delete confirmation modal for note detail page
 */

/**
 * Initialize secure file download handlers
 */
function initSecureFileDownloads() {
  const secureFileLinks = document.querySelectorAll("[data-download]");

  secureFileLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Get note ID from the page context
      const noteId = document.querySelector("[data-note-id]")?.dataset?.noteId;
      if (!noteId) {
        console.error("Note ID not found");
        return;
      }

      // Request a fresh signed URL
      fetch(`/notes/${noteId}/file/`)
        .then((response) => response.json())
        .then((data) => {
          if (data.url) {
            // Open the URL in a new tab
            window.open(data.url, "_blank");
          } else {
            alert("Error accessing file: " + (data.error || "Unknown error"));
          }
        })
        .catch((error) => {
          alert("Network error while accessing file");
        });
    });
  });
}

/**
 * Show delete confirmation modal
 */
function confirmDelete() {
  const modal = document.getElementById("delete-modal");
  if (modal) {
    modal.showModal();
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initSecureFileDownloads();

  // Expose confirmDelete to global scope as it's called from HTML
  window.confirmDelete = confirmDelete;
});
