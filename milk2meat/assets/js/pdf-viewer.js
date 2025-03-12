import * as pdfjsLib from "pdfjs-dist";

// Set the worker source - using the path where webpack will output the worker
pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/js/pdf.worker.min.js";

// Export the library for global use if needed
window.pdfjsLib = pdfjsLib;

// PDF viewer functionality
document.addEventListener("DOMContentLoaded", function () {
  const pdfViewerContainer = document.getElementById("pdf-viewer");

  // Only initialize if we have a PDF viewer container
  if (!pdfViewerContainer) return;

  // Get the note ID for secure access
  const noteId = pdfViewerContainer.dataset.noteId;

  if (noteId) {
    // For secure URLs, we need to fetch a fresh URL before loading the PDF
    fetchSecureUrl(noteId)
      .then((secureUrl) => {
        if (secureUrl) {
          initPdfViewer(pdfViewerContainer, secureUrl, noteId);
        } else {
          showError(pdfViewerContainer, "Could not load the secure PDF URL");
        }
      })
      .catch((error) => {
        showError(pdfViewerContainer, "Error loading PDF: " + error.message);
      });
  } else {
    // For backwards compatibility, check if a direct URL is provided
    const pdfUrl = pdfViewerContainer.dataset.pdfUrl;
    if (pdfUrl) {
      initPdfViewer(pdfViewerContainer, pdfUrl);
    } else {
      showError(pdfViewerContainer, "No PDF URL or note ID provided");
    }
  }
});

/**
 * Fetch a secure URL for the PDF
 * @param {string} noteId - The ID of the note
 * @returns {Promise<string>} - A promise that resolves to the secure URL
 */
async function fetchSecureUrl(noteId) {
  try {
    const response = await fetch(`/notes/${noteId}/file/`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Server error");
    }

    const data = await response.json();
    return data.url;
  } catch (error) {
    throw error;
  }
}

/**
 * Display an error in the PDF viewer container
 * @param {HTMLElement} container - The container element
 * @param {string} message - The error message to display
 */
function showError(container, message) {
  container.innerHTML = `
    <div class="p-4 text-center">
      <p class="text-error mb-2">Error loading PDF</p>
      <p class="text-sm opacity-70">${message}</p>
    </div>
  `;
}

/**
 * Initialize the PDF viewer
 * @param {HTMLElement} container - The container element
 * @param {string} pdfUrl - The URL of the PDF to display
 * @param {string} noteId - Optional note ID for secure URLs
 */
function initPdfViewer(container, pdfUrl, noteId = null) {
  // Show loading message
  container.innerHTML =
    '<div class="text-center p-4"><span class="loading loading-spinner loading-md"></span> Loading PDF...</div>';

  // State variables for PDF viewing
  let pdfDoc = null;
  let pageNum = 1;
  let pageRendering = false;
  let pageNumPending = null;
  let canvas = null;
  let ctx = null;

  // Token refresh logic
  let tokenRefreshTimer = null;

  // If using secure URLs, we need to refresh the token periodically
  if (noteId) {
    // Refresh token every 4 minutes (signed URLs expire after 5 minutes)
    const REFRESH_INTERVAL = 4 * 60 * 1000; // 4 minutes

    tokenRefreshTimer = setInterval(async () => {
      try {
        const newUrl = await fetchSecureUrl(noteId);
        // We don't need to reload the PDF, just update the URL for next operations
        pdfUrl = newUrl;
      } catch (error) {
        // If token refresh fails multiple times, we might want to show a warning
      }
    }, REFRESH_INTERVAL);
  }

  // Create UI elements
  function createUI() {
    // Clear container
    container.innerHTML = "";

    // Create canvas for rendering
    canvas = document.createElement("canvas");
    canvas.className = "mx-auto border border-base-300 rounded";
    container.appendChild(canvas);
    ctx = canvas.getContext("2d");

    // Create controls
    const controls = document.createElement("div");
    controls.className = "flex items-center justify-between mt-4";
    controls.innerHTML = `
      <div class="flex">
        <button id="pdf-prev" class="btn btn-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        <button id="pdf-next" class="btn btn-sm">
          Next
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
      <div class="text-sm">
        Page <span id="pdf-page-num"></span> of <span id="pdf-page-count"></span>
      </div>
    `;
    container.appendChild(controls);

    // Add event listeners
    document.getElementById("pdf-prev").addEventListener("click", onPrevPage);
    document.getElementById("pdf-next").addEventListener("click", onNextPage);
  }

  // Render a specific page number
  function renderPage(num) {
    pageRendering = true;

    // Using promise to fetch the page
    pdfDoc.getPage(num).then(function (page) {
      // Get container width to calculate proper scaling
      const containerWidth = container.clientWidth - 40; // Account for padding
      const viewport = page.getViewport({ scale: 1.0 });

      // Calculate scale to fit width properly
      const scale = containerWidth / viewport.width;
      const scaledViewport = page.getViewport({ scale: scale });

      // Set canvas dimensions
      canvas.height = scaledViewport.height;
      canvas.width = scaledViewport.width;

      // Render PDF page
      const renderContext = {
        canvasContext: ctx,
        viewport: scaledViewport,
      };

      const renderTask = page.render(renderContext);

      // Wait for rendering to finish
      renderTask.promise.then(function () {
        pageRendering = false;
        if (pageNumPending !== null) {
          // New page rendering is pending
          renderPage(pageNumPending);
          pageNumPending = null;
        }
      });
    });

    // Update page counter
    document.getElementById("pdf-page-num").textContent = num;
  }

  // Queue a page rendering if another is in progress
  function queueRenderPage(num) {
    if (pageRendering) {
      pageNumPending = num;
    } else {
      renderPage(num);
    }
  }

  // Display previous page
  function onPrevPage() {
    if (pageNum <= 1) {
      return;
    }
    pageNum--;
    queueRenderPage(pageNum);
  }

  // Display next page
  function onNextPage() {
    if (pageNum >= pdfDoc.numPages) {
      return;
    }
    pageNum++;
    queueRenderPage(pageNum);
  }

  // Handle window resize to adjust PDF scaling
  function handleResize() {
    if (pdfDoc && !pageRendering) {
      // Re-render current page with new scaling when window is resized
      queueRenderPage(pageNum);
    }
  }

  // Load the PDF document
  pdfjsLib
    .getDocument(pdfUrl)
    .promise.then(function (doc) {
      pdfDoc = doc;
      createUI();

      document.getElementById("pdf-page-count").textContent = pdfDoc.numPages;

      // Initial page rendering
      renderPage(pageNum);

      // Add resize handler
      window.addEventListener("resize", handleResize);
    })
    .catch(function (error) {
      showError(container, `Error loading PDF: ${error.message}`);
    });

  // Return a cleanup function to handle any resource releasing
  return function cleanup() {
    // Clear the token refresh timer if it exists
    if (tokenRefreshTimer) {
      clearInterval(tokenRefreshTimer);
    }

    // Remove event listeners
    window.removeEventListener("resize", handleResize);
  };
}
