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
      // https://coolors.co/4b6cb7-a67c52-68a357-4a90c3-e9b949-c94545-f8f5ec-333745-5d7d68
      colors: {
        // Primary - for main actions, branding
        primary: {
          DEFAULT: "#4b6cb7",
          100: "#0f1625",
          200: "#1e2b4a",
          300: "#2c4170",
          400: "#3b5695",
          500: "#4b6cb7",
          600: "#708ac6",
          700: "#94a7d4",
          800: "#b8c4e3",
          900: "#dbe2f1",
        },
        // Secondary - for supporting elements
        secondary: {
          DEFAULT: "#a67c52",
          100: "#211910",
          200: "#433221",
          300: "#644b31",
          400: "#866442",
          500: "#a67c52",
          600: "#ba9774",
          700: "#ccb196",
          800: "#ddcbb9",
          900: "#eee5dc",
        },
        // Success - for positive actions/feedback
        success: {
          DEFAULT: "#68a357",
          100: "#152011",
          200: "#294123",
          300: "#3e6134",
          400: "#538246",
          500: "#68a357",
          600: "#85b678",
          700: "#a4c89a",
          800: "#c2dbbb",
          900: "#e1eddd",
        },
        // Info - for informational elements
        info: {
          DEFAULT: "#4a90c3",
          100: "#0e1d29",
          200: "#1b3b51",
          300: "#29587a",
          400: "#3675a2",
          500: "#4a90c3",
          600: "#6fa7cf",
          700: "#93bddb",
          800: "#b7d3e7",
          900: "#dbe9f3",
        },
        // Warning - for cautionary actions/notices
        warning: {
          DEFAULT: "#e9b949",
          100: "#362807",
          200: "#6d500d",
          300: "#a37814",
          400: "#daa11b",
          500: "#e9b949",
          600: "#edc76e",
          700: "#f2d592",
          800: "#f6e3b6",
          900: "#fbf1db",
        },
        // Danger - for destructive actions/errors
        danger: {
          DEFAULT: "#c94545",
          100: "#2a0c0c",
          200: "#541818",
          300: "#7e2424",
          400: "#a83131",
          500: "#c94545",
          600: "#d46a6a",
          700: "#df9090",
          800: "#e9b5b5",
          900: "#f4dada",
        },
        // Light and dark for backgrounds, text, etc
        light: {
          DEFAULT: "#f8f5ec",
          100: "#473c1a",
          200: "#8d7734",
          300: "#c4ab5f",
          400: "#ded0a6",
          500: "#f8f5ec",
          600: "#f9f7f0",
          700: "#fbf9f4",
          800: "#fcfbf8",
          900: "#fefdfb",
        },
        dark: {
          DEFAULT: "#333745",
          100: "#0a0b0e",
          200: "#15161c",
          300: "#1f222a",
          400: "#2a2d38",
          500: "#333745",
          600: "#555b73",
          700: "#79819c",
          800: "#a6abbd",
          900: "#d2d5de",
        },
        // A scripture specific color for Bible verses
        scripture: {
          DEFAULT: "#5d7d68",
          100: "#131915",
          200: "#25322a",
          300: "#384c3f",
          400: "#4b6554",
          500: "#5d7d68",
          600: "#799c85",
          700: "#9bb5a4",
          800: "#bccec2",
          900: "#dee6e1",
        },
      },
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
  // Enable safelist for dynamic class generation
  safelist: [
    { pattern: /alert-/ }, // For alert components
    { pattern: /btn-/ }, // For button components
    "dark",
    "dark:bg-dark-800",
    "dark:bg-dark-900",
    "dark:text-light-100",
    "dark:text-light-200",
    "dark:border-dark-700",
    "dark:border-dark-600",
  ],
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
  darkMode: "class", // Enable dark mode with class strategy
};
