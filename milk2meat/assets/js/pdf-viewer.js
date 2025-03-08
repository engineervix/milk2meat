import * as pdfjsLib from "pdfjs-dist";

// Set the worker source
pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/js/pdf.worker.min.js";

// Export the library for global use
window.pdfjsLib = pdfjsLib;

// PDF viewer functionality
document.addEventListener("DOMContentLoaded", function () {
  const pdfViewerContainer = document.getElementById("pdf-viewer");

  // Only initialize if we have a PDF viewer container
  if (!pdfViewerContainer) return;

  const pdfUrl = pdfViewerContainer.dataset.pdfUrl;
  if (!pdfUrl) return;

  // Show loading message
  pdfViewerContainer.innerHTML =
    '<div class="text-center p-4"><span class="loading loading-spinner loading-md"></span> Loading PDF...</div>';

  // Load the PDF
  pdfjsLib
    .getDocument(pdfUrl)
    .promise.then(function (pdf) {
      // Remove loading message
      pdfViewerContainer.innerHTML = "";

      // Get the first page
      pdf.getPage(1).then(function (page) {
        // Get container width to calculate proper scaling
        const containerWidth = pdfViewerContainer.clientWidth;
        const viewport = page.getViewport({ scale: 1.0 });

        // Calculate scale to fit width properly
        const scale = containerWidth / viewport.width;
        const scaledViewport = page.getViewport({ scale: scale });

        // Prepare canvas with proper dimensions
        const canvas = document.createElement("canvas");
        pdfViewerContainer.appendChild(canvas);

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;
        canvas.className = "mx-auto"; // Center the canvas

        const context = canvas.getContext("2d");

        // Render PDF page
        page.render({
          canvasContext: context,
          viewport: scaledViewport,
        });

        // Add page info
        const pageInfo = document.createElement("div");
        pageInfo.className = "text-center text-sm mt-2 opacity-70";
        pageInfo.textContent = `Page 1 of ${pdf.numPages}`;
        pdfViewerContainer.appendChild(pageInfo);

        // If PDF has multiple pages, add a note
        if (pdf.numPages > 1) {
          const multiPageNote = document.createElement("div");
          multiPageNote.className = "text-center text-sm mt-1 opacity-60";
          multiPageNote.textContent = "Download the PDF to view all pages";
          pdfViewerContainer.appendChild(multiPageNote);
        }
      });
    })
    .catch(function (error) {
      // console.error("Error loading PDF:", error);
      pdfViewerContainer.innerHTML =
        '<div class="p-4 text-center"><p class="text-error">Error loading PDF. Please download to view.</p></div>';
    });
});
