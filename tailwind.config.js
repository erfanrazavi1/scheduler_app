/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./templates/**/*.html",
    "./schedules/**/*.py",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Vazirmatn",
          "Tahoma",
          "Arial",
          "system-ui",
          "sans-serif",
        ],
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 150ms ease-out",
      },
    },
  },
  plugins: [],
};
