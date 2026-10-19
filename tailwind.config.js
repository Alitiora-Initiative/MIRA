/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#05070a',
        'bg-alt': '#0a0e14',
        fg: '#e8eef5',
        'fg-dim': '#9ba3b0',
        surface: '#0c1016',
        'surface-2': '#141a22',
        'surface-3': '#1a2230',
        line: '#1a1f26',
        'line-dim': '#0f141a',
        muted: '#7d8794',
        'muted-dim': '#5c6470',
        teal: '#2ee6a6',
        'teal-dim': '#0d3d2e',
        'teal-light': '#4fffd4',
        'teal-dark': '#1a9f7a',
        amber: '#e8b86d',
        'amber-dim': '#8f6a42',
        rose: '#f07178',
        'rose-dim': '#8f454a',
        violet: '#a78bfa',
        'violet-dim': '#6d5fa3',
        ink: '#05070a',
      },
      fontFamily: {
        sans: ['"Outfit"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      animation: {
        'live-dot': 'pulse-dot 1.6s ease-in-out infinite',
        'gradient-shift': 'gradient-shift 3s ease infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        'pulse-dot': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.35', transform: 'scale(0.8)' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(46, 230, 166, 0.2), 0 0 40px rgba(46, 230, 166, 0.1)' },
          '50%': { boxShadow: '0 0 30px rgba(46, 230, 166, 0.4), 0 0 60px rgba(46, 230, 166, 0.2)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'fadeIn': {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'cinematic': 'radial-gradient(ellipse at top, rgba(46, 230, 166, 0.08) 0%, transparent 50%)',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(46, 230, 166, 0.2), 0 0 40px rgba(46, 230, 166, 0.1)',
        'glow-strong': '0 0 30px rgba(46, 230, 166, 0.4), 0 0 60px rgba(46, 230, 166, 0.2)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.4)',
        'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.6)',
        'cinematic': '0 0 60px rgba(46, 230, 166, 0.15)',
      },
    },
  },
  plugins: [],
}
