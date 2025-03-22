/**
 * Handle filtering and tag management for note list page
 */

/**
 * Apply filter to the current URL
 * @param {string} filterType - Type of filter (type, book, tag)
 * @param {string} value - Filter value
 */
function applyFilter(filterType, value) {
  // Get current URL and parameters
  const url = new URL(window.location.href);
  const params = new URLSearchParams(url.search);

  // Remove page parameter when changing filters
  params.delete("page");

  // Set, update, or remove the filter parameter
  if (value) {
    params.set(filterType, value);
  } else {
    params.delete(filterType);
  }

  // Redirect to new URL with updated parameters
  window.location.href = `${url.pathname}?${params.toString()}`;
}

/**
 * Initialize tag checkbox handlers
 */
function initTagCheckboxes() {
  const tagCheckboxes = document.querySelectorAll(".tag-checkbox");

  tagCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      // Uncheck other checkboxes
      tagCheckboxes.forEach((cb) => {
        if (cb !== checkbox) {
          cb.checked = false;
        }
      });

      // Apply tag filter
      if (checkbox.checked) {
        applyFilter("tag", checkbox.dataset.tagName);
      } else {
        applyFilter("tag", "");
      }
    });
  });
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initTagCheckboxes();

  // Expose applyFilter to global scope as it's called from HTML
  window.applyFilter = applyFilter;
});
