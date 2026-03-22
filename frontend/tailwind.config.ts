import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        shell: {
          bg: "#061018",
          panel: "#0C1623",
          panelSoft: "#101D2E",
          border: "rgba(133, 181, 214, 0.16)",
          text: "#E6F0FA",
          muted: "#8BA5BD",
          accent: "#3BC8FF",
          accentSoft: "#2DD4BF",
          warn: "#F59E0B",
          danger: "#F97373",
          success: "#4ADE80"
        }
      },
      boxShadow: {
        panel: "0 18px 70px rgba(2, 8, 23, 0.38)"
      }
    }
  },
  plugins: [],
};

export default config;
