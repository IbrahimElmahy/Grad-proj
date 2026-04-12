/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      colors: {
        brand: {
          50:  '#e8f0ff',
          100: '#c3d4ff',
          200: '#9ab5ff',
          300: '#6b92ff',
          400: '#3d7fff',
          500: '#1a6bff',
          600: '#0d4fd4',
          700: '#0038aa',
          800: '#002480',
          900: '#001357',
        },
      },
      animation: {
        'fade-in': 'fadeIn .3s ease forwards',
        'slide-up': 'slideUp .3s ease forwards',
        blink: 'blink 1.2s ease-in-out infinite',
        spin: 'spin .7s linear infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0, transform: 'translateY(10px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        slideUp: { from: { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        blink: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.2 } },
      },
    },
  },
  plugins: [],
}
