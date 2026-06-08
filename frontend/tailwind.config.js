/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      "colors": {
              "background": "#F5F5F7",
              "surface": "#FFFFFF",
              "surface-variant": "#F2F2F7",
              "primary": "#34C759",
              "primary-container": "#E8F8EE",
              "on-primary": "#FFFFFF",
              "secondary": "#FF9500",
              "secondary-container": "#FFF4E5",
              "error": "#FF3B30",
              "on-surface": "#1C1C1E",
              "on-surface-variant": "#8E8E93",
              "outline": "#E5E5EA",
              "barbecue-fire": "#FF3B30",
              "inverse-surface": "#1C1C1E",
              "inverse-on-surface": "#F5F5F7",
      },
      "boxShadow": {
              "bento": "0 8px 32px rgba(0, 0, 0, 0.04)",
              "bento-hover": "0 12px 48px rgba(0, 0, 0, 0.08)",
      },
      "borderRadius": {
              "DEFAULT": "0.5rem",
              "md": "0.75rem",
              "lg": "1rem",
              "xl": "1.5rem",
              "2xl": "2rem",
              "3xl": "2.5rem",
              "full": "9999px"
      },
      "spacing": {
              "card-gap": "12px",
              "unit": "8px",
              "container-margin-desktop": "40px",
              "gutter": "16px",
              "container-margin-mobile": "16px",
              "safe": "env(safe-area-inset-bottom, 16px)"
      },
      "fontFamily": {
              "label-bold": ["Inter"],
              "body-md": ["Inter"],
              "body-sm": ["Inter"],
              "headline-lg": ["Plus Jakarta Sans"],
              "display-lg": ["Plus Jakarta Sans"],
              "headline-md": ["Plus Jakarta Sans"],
              "headline-lg-mobile": ["Plus Jakarta Sans"]
      },
      "fontSize": {
              "label-bold": ["12px", {"lineHeight": "1", "letterSpacing": "0.05em", "fontWeight": "700"}],
              "body-md": ["16px", {"lineHeight": "1.6", "fontWeight": "400"}],
              "body-sm": ["14px", {"lineHeight": "1.5", "fontWeight": "400"}],
              "headline-lg": ["32px", {"lineHeight": "1.2", "letterSpacing": "-0.01em", "fontWeight": "700"}],
              "display-lg": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "800"}],
              "headline-md": ["20px", {"lineHeight": "1.4", "fontWeight": "600"}],
              "headline-lg-mobile": ["24px", {"lineHeight": "1.2", "fontWeight": "700"}]
      }
    }
  },
  plugins: []
}
