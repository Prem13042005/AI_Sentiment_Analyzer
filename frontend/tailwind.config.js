/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0f1a2e',
          mid: '#162035',
        },
        teal: {
          DEFAULT: '#00b8a9',
          dark: '#009688',
        },
        gray: {
          bg: '#f5f6fa',
          card: '#ffffff',
          border: '#e8ecf0',
        },
        text: {
          dark: '#1a2332',
          mid: '#4a5568',
          muted: '#8896ab',
        },
        positive: '#22c55e',
        negative: '#ef4444',
        neutral: '#94a3b8',
        warning: '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
