import { BibleBooksManager } from "./bible-books";
import { TagsManager } from "./tags-input";
import { FileUploadManager } from "./file-upload";
import { NoteTypeManager } from "./note-type";
import { AjaxFormManager } from "./ajax-form";
import { FormEnhancer } from "../form-enhancements";

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Bible Books Manager
  const bibleBooks = new BibleBooksManager({
    inputId: "referenced-books",
    booksListId: "book-suggestions-list",
    suggestionsId: "book-suggestions",
    selectedContainerId: "selected-books-container",
    hiddenInputId: "referenced-books-json",
    bibleBooks: window.bibleBooks || [], // This will be populated from the template
  });

  // Initialize Tags Manager
  const tags = new TagsManager({
    inputId: "tags-input",
    hiddenInputId: "hidden-tags-input",
    containerId: "tags-container",
  });

  // Initialize File Upload Manager
  const fileUpload = new FileUploadManager({
    inputId: "file-upload",
    uploadAreaId: "upload-area",
    previewId: "file-preview",
    fileNameId: "file-name",
    removeFileBtnId: "remove-file",
    existingFileId: "existing-file",
    replaceFileBtnId: "replace-file",
    deleteFileBtnId: "delete-file",
  });

  // Initialize Note Type Manager
  const noteType = new NoteTypeManager({
    formId: "new-type-form",
    nameInputId: "new-type-name",
    descInputId: "new-type-description",
    nameErrorId: "new-type-name-error",
    modalId: "new-type-modal",
    selectId: "id_note_type",
    createUrl: window.noteTypeCreateUrl, // This will be populated from the template
  });

  // Get editor instances for syncing before form submission
  const editors = window.editors || [];

  // Initialize AJAX Form Manager
  const ajaxForm = new AjaxFormManager({
    formSelector: "#note-form",
    messageContainerId: "form-messages",
    editorInstances: editors,
    createUrl: window.noteCreateUrl,
    updateUrl: window.noteUpdateUrl,
    noteId: window.currentNoteId,
  });

  // Initialize Form Enhancer for keyboard shortcuts and floating save button
  const formEnhancer = new FormEnhancer({
    formSelector: "#note-form",
    fabPosition: "bottom-right",
    fabLabel: "Save",
  });
});
