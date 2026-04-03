"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { describeApiError } from "@/lib/api";

type Loader<T> = () => Promise<T>;

const DEFAULT_REFRESH_MS = 5 * 60 * 1000;

export function useLivePageData<T>(loader: Loader<T>, refreshMs: number = DEFAULT_REFRESH_MS) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const loaderRef = useRef(loader);

  loaderRef.current = loader;

  const loadData = useCallback(async () => {
    setError(null);

    try {
      const nextData = await loaderRef.current();
      setData(nextData);
    } catch (loadError) {
      setError(describeApiError(loadError));
      setData(null);
    }
  }, []);

  useEffect(() => {
    void loadData();

    const refreshInterval = window.setInterval(() => {
      void loadData();
    }, refreshMs);

    const refreshOnFocus = () => {
      if (document.visibilityState === "visible") {
        void loadData();
      }
    };

    window.addEventListener("focus", refreshOnFocus);
    document.addEventListener("visibilitychange", refreshOnFocus);

    return () => {
      window.clearInterval(refreshInterval);
      window.removeEventListener("focus", refreshOnFocus);
      document.removeEventListener("visibilitychange", refreshOnFocus);
    };
  }, [loadData, refreshMs]);

  return {
    data,
    error,
    loadData,
  };
}
