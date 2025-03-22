/**
 * Handle tag search and filtering functionality for tag list page
 */

/**
 * Initialize tag search functionality
 */
function initTagSearch() {
  const searchInput = document.getElementById("tag-search");
  const tagItems = document.querySelectorAll(".tag-item");
  const tagCloud = document.getElementById("tag-cloud");
  const letterSections = document.querySelectorAll(".letter-section");

  if (!searchInput) return;

  searchInput.addEventListener("input", function () {
    const searchValue = this.value.toLowerCase().trim();

    // Filter individual tag items
    tagItems.forEach((tag) => {
      const tagName = tag.querySelector("span").textContent.toLowerCase();
      tag.style.display = tagName.includes(searchValue) ? "" : "none";
    });

    // Filter tag cloud items
    if (tagCloud) {
      const cloudTags = tagCloud.querySelectorAll(".tag-link");
      cloudTags.forEach((tag) => {
        const tagName = tag.textContent.toLowerCase().trim();
        tag.style.display = tagName.includes(searchValue) ? "" : "none";
      });
    }

    // Show/hide letter sections based on whether they have visible items
    letterSections.forEach((section) => {
      const visibleTags = section.querySelectorAll('.tag-item[style=""]');
      section.style.display = visibleTags.length === 0 ? "none" : "";
    });
  });
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initTagSearch();
});
