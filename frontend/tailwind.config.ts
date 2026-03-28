import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        shell: {
          bg: "#020202",
          frame: "#07090C",
          panel: "#0B0D10",
          panelSoft: "#12161B",
          panelRaised: "#181D24",
          border: "rgba(255, 255, 255, 0.08)",
          borderStrong: "rgba(97, 214, 255, 0.24)",
          text: "#F3F7FB",
          muted: "#8D97A3",
          accent: "#61D6FF",
          accentSoft: "#3CD7A4",
          warn: "#F6B44F",
          danger: "#FB7185",
          success: "#3CD7A4"
        }
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0, 0, 0, 0.38)",
        shell: "0 36px 120px rgba(0, 0, 0, 0.52)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.04)"
      }
    }
  },
  plugins: [],
};

export default config;
