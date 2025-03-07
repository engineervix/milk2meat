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
  plugins: [
    require("daisyui"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
  daisyui: {
    themes: ["emerald", "dark"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    logs: true,
    rtl: false,
    prefix: "",
  },
  darkMode: "class", // Enable dark mode with class strategy
};
