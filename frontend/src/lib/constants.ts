import { NavigationItem } from "@/lib/types";

export const navigation: NavigationItem[] = [
  {
    href: "/",
    label: "Home",
    shortLabel: "Home",
    description: "Cross-module command center for the current market picture and next actions.",
  },
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
    label: "Anomalies",
    shortLabel: "Anomalies",
    description: "Ranked anomaly tape for cross-asset inconsistencies worth investigating.",
  },
  {
    href: "/thesis",
    label: "Thesis Builder",
    shortLabel: "Thesis",
    description: "Translate plain-English investment ideas into exposures and watch signals.",
  },
  {
    href: "/system",
    label: "System",
    shortLabel: "System",
    description: "Monitor refresh health, manage alert thresholds, and review generated digests.",
  },
];

export const thesisSamples = [
  "AI data centers will drive electricity demand higher",
  "Higher-for-longer rates will pressure small caps",
  "Home energy costs will continue rising",
  "Credit stress will appear before equities react",
];
