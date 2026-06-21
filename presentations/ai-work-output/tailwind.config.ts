import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0a1628',
        gold: '#d4a853',
        cream: '#f8f1df',
        slate: '#8ca0b3',
      },
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        body: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      boxShadow: {
        luxe: '0 22px 60px rgba(0, 0, 0, 0.42)',
      },
      backgroundImage: {
        grain:
          "radial-gradient(circle at 15% 20%, rgba(212,168,83,0.18), transparent 35%), radial-gradient(circle at 80% 10%, rgba(124,145,166,0.2), transparent 40%), radial-gradient(circle at 50% 90%, rgba(212,168,83,0.12), transparent 45%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
