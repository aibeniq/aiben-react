import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
    },
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
    },
    ".dnd-placeholder": {
      display: "none", // Required for react-beautiful-dnd
    },

    // Global overlay management styles to prevent UI responsiveness issues
    '[data-scope="drawer"][data-part="backdrop"]:not([data-state="open"])': {
      display: "none !important",
      pointerEvents: "none !important",
      opacity: "0 !important",
    },

    // Ensure modal overlays don't interfere when not active
    ".chakra-modal__overlay:not(.chakra-modal__overlay--active)": {
      display: "none !important",
      pointerEvents: "none !important",
    },

    // Ensure floating elements always stay interactive
    '[aria-label="Get help"]': {
      pointerEvents: "auto !important",
      zIndex: "9999 !important",
      isolation: "isolate !important",
    },

    // Ensure sidebar menu button always stays interactive at all screen sizes
    '[aria-label="Open Menu"]': {
      pointerEvents: "auto !important",
      zIndex: "1001 !important",
      isolation: "isolate !important",
      cursor: "pointer !important",
    },

    // Prevent portal elements from blocking interactions when empty
    "[data-portal]:empty": {
      display: "none !important",
      pointerEvents: "none !important",
    },

    // Ensure main content areas are always interactive
    'main, [role="main"], .main-content': {
      pointerEvents: "auto",
      isolation: "isolate",
    },
  },
  theme: {
    tokens: {
      colors: {
        ui: {
          main: { value: "#009688" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})
