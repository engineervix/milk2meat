import { AjaxBookFormManager } from "./ajax-book-form";
import { FormEnhancer } from "../form-enhancements";

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

  // Initialize Form Enhancer for keyboard shortcuts and floating save button
  const formEnhancer = new FormEnhancer({
    formSelector: "#book-form",
    fabPosition: "bottom-right",
    fabLabel: "Save",
  });
});
