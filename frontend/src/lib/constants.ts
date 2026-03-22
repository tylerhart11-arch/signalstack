import { NavigationItem } from "@/lib/types";

export const navigation: NavigationItem[] = [
  {
    href: "/overview",
    label: "Overview",
    shortLabel: "Overview",
    description: "Cross-asset dashboard for major macro and market indicators.",
  },
  {
    href: "/regime",
    label: "Regime",
    shortLabel: "Regime",
    description: "Explainable macro regime classification and historical context.",
  },
  {
    href: "/feed",
    label: "Curiosity Feed",
    shortLabel: "Feed",
    description: "Ranked anomaly tape for cross-asset inconsistencies worth investigating.",
  },
  {
    href: "/thesis",
    label: "Thesis Builder",
    shortLabel: "Thesis",
    description: "Translate plain-English investment ideas into exposures and watch signals.",
  },
];

export const thesisSamples = [
  "AI data centers will drive electricity demand higher",
  "Higher-for-longer rates will pressure small caps",
  "Home energy costs will continue rising",
  "Credit stress will appear before equities react",
];
