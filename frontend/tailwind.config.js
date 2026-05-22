/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#006e2f',
        'on-primary': '#ffffff',
        secondary: '#9d4300',
        'on-secondary': '#ffffff',
        surface: '#f7f9fb',
        'surface-variant': '#e0e3e5',
        background: '#f7f9fb',
        'on-background': '#191c1e',
        error: '#ba1a1a',
        'barbecue-start': '#fd761a',
        'barbecue-end': '#93000a',
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'lvl1': '0 4px 6px -1px rgba(84, 95, 115, 0.05), 0 2px 4px -1px rgba(84, 95, 115, 0.03)',
        'lvl2': '0 12px 24px -4px rgba(84, 95, 115, 0.08), 0 4px 8px -2px rgba(84, 95, 115, 0.04)',
        'glass': '0 24px 48px -12px rgba(84, 95, 115, 0.15)',
      },
      borderRadius: {
        'standard': '0.5rem',  // 8px
        'card': '1rem',        // 16px
        'pill': '9999px',
      }
    },
  },
  plugins: [],
}
