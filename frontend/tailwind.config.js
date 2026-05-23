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
              "surface-container-high": "#e6e8ea",
              "inverse-primary": "#4ae176",
              "surface": "#f7f9fb",
              "tertiary-fixed-dim": "#bcc7de",
              "secondary-fixed": "#ffdbca",
              "on-tertiary": "#ffffff",
              "on-primary-fixed": "#002109",
              "inverse-on-surface": "#eff1f3",
              "on-primary": "#ffffff",
              "primary": "#006e2f",
              "surface-bright": "#f7f9fb",
              "on-tertiary-fixed-variant": "#3c475a",
              "on-tertiary-container": "#354053",
              "secondary-container": "#fd761a",
              "on-secondary-container": "#5c2400",
              "primary-fixed": "#6bff8f",
              "surface-tint": "#006e2f",
              "surface-variant": "#e0e3e5",
              "surface-container-lowest": "#ffffff",
              "on-primary-container": "#004b1e",
              "on-secondary-fixed-variant": "#783200",
              "error": "#ba1a1a",
              "secondary-fixed-dim": "#ffb690",
              "secondary": "#9d4300",
              "tertiary-container": "#a1acc3",
              "background": "#f7f9fb",
              "surface-dim": "#d8dadc",
              "on-secondary-fixed": "#341100",
              "on-error-container": "#93000a",
              "tertiary-fixed": "#d8e3fb",
              "surface-container-highest": "#e0e3e5",
              "on-surface-variant": "#3d4a3d",
              "primary-fixed-dim": "#4ae176",
              "outline": "#6d7b6c",
              "on-primary-fixed-variant": "#005321",
              "on-surface": "#191c1e",
              "outline-variant": "#bccbb9",
              "on-secondary": "#ffffff",
              "inverse-surface": "#2d3133",
              "on-background": "#191c1e",
              "on-tertiary-fixed": "#111c2d",
              "surface-container-low": "#f2f4f6",
              "error-container": "#ffdad6",
              "primary-container": "#22c55e",
              "on-error": "#ffffff",
              "tertiary": "#545f73",
              "surface-container": "#eceef0",
              "barbecue-fire": "#e63900"
      },
      "borderRadius": {
              "DEFAULT": "0.25rem",
              "lg": "0.5rem",
              "xl": "0.75rem",
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
