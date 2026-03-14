/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Neo-Brutalism (Light Mode)
        neo: {
          bg: '#FFFDF5',
          fg: '#000000',
          accent: '#FF6B6B',
          secondary: '#FFD93D',
          muted: '#C4B5FD',
        },
        // Terminal CLI (Dark Mode - Control Center Blue)
        term: {
          bg: '#020b14',
          fg: '#33ff00',
          primary: '#33ff00',
          secondary: '#00ccff',
          muted: '#103050',
          error: '#ff3333',
        }
      },
      fontFamily: {
        neo: ['"Space Grotesk"', 'sans-serif'],
        term: ['"JetBrains Mono"', '"Fira Code"', '"VT323"', 'monospace'],
      },
      boxShadow: {
        'neo-sm': '4px 4px 0px 0px #000',
        'neo-md': '8px 8px 0px 0px #000',
        'neo-lg': '12px 12px 0px 0px #000',
        'neo-xl': '16px 16px 0px 0px #000',
        'term-glow': '0 0 5px rgba(51, 255, 0, 0.5)',
      },
      borderWidth: {
        DEFAULT: '4px',
        2: '2px',
        4: '4px',
        8: '8px',
      },
      animation: {
        'spin-slow': 'spin-slow 10s linear infinite',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'blink': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0 },
        }
      }
    },
  },
  plugins: [],
}
