/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./milk2meat/**/templates/**/*.html", // Catches templates in all Django apps
    "./milk2meat/assets/js/**/*.js", // Only JS files in assets
    // Error pages use custom styling, so we exclude them
    "!milk2meat/**/400.html",
    "!milk2meat/**/403.html",
    "!milk2meat/**/404.html",
    "!milk2meat/**/500.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Avenir",
          "Montserrat",
          "Corbel",
          "URW Gothic",
          "source-sans-pro",
          "sans-serif",
        ],
      },
    },
  },
  // safelist: [
  //   { pattern: /alert-+/ },
  //   "collapse",
  //   "collapse-plus",
  //   "collapse-open",
  //   "collapse-close",
  //   "collapse-title",
  //   "collapse-content",
  //   { pattern: /hover:text-+/ }, // This will catch hover:text-primary
  //   { pattern: /gap-+/ }, // This will catch gap-3 and other gap utilities
  // ],
  plugins: [require("@tailwindcss/typography")],
};
