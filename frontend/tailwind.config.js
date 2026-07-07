/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eefbf4",
          100: "#d6f5e2",
          200: "#aeebc9",
          300: "#7adaac",
          400: "#45c18b",
          500: "#22a571",
          600: "#15855b",
          700: "#136a4b",
          800: "#12543d",
          900: "#104533",
          950: "#06271c",
        },
        surface: {
          light: "#f7f8fa",
          dark: "#0b0f14",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,24,40,0.06), 0 1px 3px rgba(16,24,40,0.08)",
        "card-dark": "0 1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
