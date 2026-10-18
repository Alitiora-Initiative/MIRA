/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#07090f',
        fg: '#e7efe8',
        surface: '#10151c',
        'surface-2': '#171e28',
        line: '#24302a',
        muted: '#8b978f',
        teal: '#2ee6a6',
        'teal-dim': '#12382c',
        amber: '#e8b86d',
        rose: '#f07178',
        ink: '#07090f',
      },
      fontFamily: {
        sans: ['"Outfit"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      animation: {
        'live-dot': 'pulse-dot 1.6s ease-in-out infinite',
      },
      keyframes: {
        'pulse-dot': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.35' },
        },
      },
    },
  },
  plugins: [],
}
