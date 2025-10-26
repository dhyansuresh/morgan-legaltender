/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'legal-blue': '#1e3a8a',
        'legal-gold': '#f59e0b',
      },
    },
  },
  plugins: [],
}
