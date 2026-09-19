import { GrayMatterApiError } from "./errors";

/**
 * Transport is the only place that knows whether data comes from HTTP or from
 * the in-memory mock. `GrayMatterAPI` is written against this interface, so
 * switching to the live FastAPI backend touches no component and no feature.
 */

export interface RequestSpec {
  method: "GET" | "POST";
  /** Path relative to the API root, e.g. `/decisions/DEC-004`. */
  path: string;
  body?: unknown;
  signal?: AbortSignal;
}

export interface Transport {
  request<T>(spec: RequestSpec): Promise<T>;
}

/* -------------------------------------------------------------------------- */

export class HttpTransport implements Transport {
  constructor(private readonly baseUrl: string) {}

  async request<T>({ method, path, body, signal }: RequestSpec): Promise<T> {
    let response: Response;

    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
        signal,
      });
    } catch (cause) {
      if (cause instanceof DOMException && cause.name === "AbortError") {
        throw new GrayMatterApiError("aborted", "Request cancelled.", {
          endpoint: path,
          cause,
        });
      }
      throw new GrayMatterApiError(
        "network",
        `Could not reach ${this.baseUrl}${path}.`,
        { endpoint: path, cause },
      );
    }

    if (!response.ok) {
      throw new GrayMatterApiError(
        response.status === 404 ? "not_found" : "http",
        `${method} ${path} responded ${response.status}.`,
        { status: response.status, endpoint: path },
      );
    }

    try {
      return (await response.json()) as T;
    } catch (cause) {
      throw new GrayMatterApiError(
        "parse",
        `${method} ${path} did not return JSON.`,
        { status: response.status, endpoint: path, cause },
      );
    }
  }
}
