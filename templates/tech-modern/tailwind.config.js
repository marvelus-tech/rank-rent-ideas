/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        midnight: '#1a1a2e',
        cyan: '#00d4ff',
        ink: '#e0e0e0',
      },
      boxShadow: {
        cyan: '0 0 24px rgba(0,212,255,0.45)',
      },
      fontFamily: {
        display: ['"Clash Display"', 'sans-serif'],
        body: ['"General Sans"', 'sans-serif'],
      },
      backgroundImage: {
        grid: 'linear-gradient(rgba(0,212,255,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.07) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
}
