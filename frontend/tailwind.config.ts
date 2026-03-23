import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        shell: {
          bg: "#07111B",
          frame: "#0B1624",
          panel: "#0F1B2B",
          panelSoft: "#132234",
          panelRaised: "#17293D",
          border: "rgba(128, 160, 189, 0.18)",
          borderStrong: "rgba(147, 181, 211, 0.3)",
          text: "#E5EEF8",
          muted: "#91A7BE",
          accent: "#5AC8FA",
          accentSoft: "#7DE0D4",
          warn: "#F59E0B",
          danger: "#F97373",
          success: "#4ADE80"
        }
      },
      boxShadow: {
        panel: "0 24px 80px rgba(2, 8, 23, 0.34)",
        shell: "0 34px 110px rgba(2, 8, 23, 0.42)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.04)"
      }
    }
  },
  plugins: [],
};

export default config;
