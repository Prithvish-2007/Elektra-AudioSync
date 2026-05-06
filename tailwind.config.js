/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#030712',
        card: '#111827',
        elevated: '#1f2937',
      },
    },
  },
  plugins: [],
}
