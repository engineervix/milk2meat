import { AjaxBookFormManager } from "./ajax-book-form";

document.addEventListener("DOMContentLoaded", () => {
  // Get editor instances for syncing before form submission
  const editors = window.editors || [];

  // Initialize AJAX Form Manager
  const ajaxForm = new AjaxBookFormManager({
    formSelector: "#book-form",
    messageContainerId: "form-messages",
    editorInstances: editors,
    updateUrl: window.bookUpdateUrl,
    bookId: window.currentBookId,
  });
});
