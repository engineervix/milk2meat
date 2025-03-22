// ESV Cross-Reference Tool Integration
// https://www.esv.org/resources/esv-crossreference-tool/
// ESV Cross-Reference Tool configuration
document.addEventListener("DOMContentLoaded", function () {
  // Function to update ESV tool styles based on current theme
  function updateESVStyles() {
    const isDarkTheme =
      document.documentElement.getAttribute("data-theme") === "night";

    window.ESV_CROSSREF_OPTIONS = {
      // Colors without the # prefix as required by the tool
      border_color: isDarkTheme ? "444444" : "CCCCCC",
      border_radius: 10,
      header_font_color: isDarkTheme ? "FFFFFF" : "000000",
      body_font_color: isDarkTheme ? "FFFFFF" : "000000",
      footer_font_color: isDarkTheme ? "AAAAAA" : "CCCCCC",
      header_background_color: isDarkTheme ? "333333" : "F0F0F0",
      body_background_color: isDarkTheme ? "222222" : "F0F0F0",
      footer_background_color: isDarkTheme ? "333333" : "F0F0F0",
    };

    // Manually trigger re-linking to apply new styles
    window.dispatchEvent(new Event("esv-crossref.trigger-linkify"));
  }

  // Run initially
  updateESVStyles();

  // Update when theme changes
  window.addEventListener("milk2meat-theme-changed", updateESVStyles);
});
