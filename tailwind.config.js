/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./milk2meat/**/templates/**/*.html", // Catches templates in all Django apps
    "./milk2meat/frontend/js/**/*.js", // Only JS files in frontend dir
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
        serif: [
          "Charter",
          "Bitstream Charter",
          "Sitka Text",
          "Cambria",
          "serif",
        ],
      },
    },
  },
  plugins: [
    require("daisyui"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
  daisyui: {
    themes: ["winter", "night"],
  },
  safelist: [{ pattern: /alert-+/ }],
  darkMode: ["selector", '[data-theme="night"]'],
};
