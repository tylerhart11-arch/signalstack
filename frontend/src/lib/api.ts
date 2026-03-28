import {
  AlertConfig,
  AlertEvent,
  AlertHistoryResponse,
  AnomalyResponse,
  OverviewResponse,
  RefreshStatusResponse,
  RegimeCurrentResponse,
  RegimeHistoryResponse,
  SavedThesisResponse,
  ThesisResult,
} from "@/lib/types";

const LOCAL_API_HOSTS = new Set(["localhost", "127.0.0.1", "0.0.0.0"]);

export class ApiError extends Error {
  readonly path: string;
  readonly status: number | null;

  constructor(message: string, options: { path: string; status?: number | null }) {
    super(message);
    this.name = "ApiError";
    this.path = options.path;
    this.status = options.status ?? null;
  }
}

function getApiBaseUrl(): string {
  const configuredBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (typeof window !== "undefined") {
    if (!configuredBaseUrl) {
      return `${window.location.protocol}//${window.location.hostname}:8000`;
    }

    try {
      const configuredUrl = new URL(configuredBaseUrl);
      if (LOCAL_API_HOSTS.has(configuredUrl.hostname) && !LOCAL_API_HOSTS.has(window.location.hostname)) {
        return `${configuredUrl.protocol}//${window.location.hostname}:${configuredUrl.port || "8000"}`;
      }
      return configuredBaseUrl;
    } catch {
      return `${window.location.protocol}//${window.location.hostname}:8000`;
    }
  }

  return configuredBaseUrl || "http://127.0.0.1:8000";
}

async function readErrorDetail(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      const payload = (await response.json()) as { detail?: string };
      if (typeof payload.detail === "string" && payload.detail.trim()) {
        return payload.detail;
      }
    } catch {
      // Ignore JSON parsing errors and fall back to text/status.
    }
  }

  try {
    const text = await response.text();
    if (text.trim()) {
      return text.trim();
    }
  } catch {
    // Ignore text parsing errors and fall back to the status line.
  }

  return response.status >= 500
    ? "The live API could not complete the request."
    : `Request failed with status ${response.status}.`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8_000);

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new ApiError(await readErrorDetail(response), {
        path,
        status: response.status,
      });
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("The live API timed out before it responded.", {
        path,
      });
    }

    if (error instanceof Error) {
      throw new ApiError(error.message || "Could not reach the live API.", {
        path,
      });
    }

    throw new ApiError("Could not reach the live API.", {
      path,
    });
  } finally {
    clearTimeout(timeout);
  }
}

export function describeApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return "Live data is unavailable right now.";
}

export function getOverview(): Promise<OverviewResponse> {
  return requestJson<OverviewResponse>("/api/overview");
}

export function getCurrentRegime(): Promise<RegimeCurrentResponse> {
  return requestJson<RegimeCurrentResponse>("/api/regime/current");
}

export function getRegimeHistory(): Promise<RegimeHistoryResponse> {
  return requestJson<RegimeHistoryResponse>("/api/regime/history");
}

export function getAnomalies(): Promise<AnomalyResponse> {
  return requestJson<AnomalyResponse>("/api/anomalies");
}

export function analyzeThesis(text: string, save = false): Promise<ThesisResult> {
  return requestJson<ThesisResult>("/api/thesis/analyze", {
    method: "POST",
    body: JSON.stringify({ text, save }),
  });
}

export function getSavedTheses(): Promise<SavedThesisResponse[]> {
  return requestJson<SavedThesisResponse[]>("/api/thesis/saved");
}

export function persistThesis(text: string): Promise<SavedThesisResponse> {
  return requestJson<SavedThesisResponse>("/api/thesis/saved", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function getRefreshStatus(): Promise<RefreshStatusResponse> {
  return requestJson<RefreshStatusResponse>("/api/system/refresh-status");
}

export function getAlertConfig(): Promise<AlertConfig> {
  return requestJson<AlertConfig>("/api/alerts/config");
}

export function updateAlertConfig(config: AlertConfig): Promise<AlertConfig> {
  return requestJson<AlertConfig>("/api/alerts/config", {
    method: "PUT",
    body: JSON.stringify(config),
  });
}

export function getAlertHistory(): Promise<AlertHistoryResponse> {
  return requestJson<AlertHistoryResponse>("/api/alerts/history");
}

export function runDigest(): Promise<AlertEvent> {
  return requestJson<AlertEvent>("/api/alerts/run-digest", {
    method: "POST",
    body: JSON.stringify({}),
  });
}
