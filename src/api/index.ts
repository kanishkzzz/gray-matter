import { GrayMatterAPI } from "./client";
import { API_CONFIG } from "./config";
import { MockTransport } from "./mock/transport";
import { HttpTransport } from "./transport";

export { GrayMatterAPI } from "./client";
export { API_CONFIG } from "./config";
export { GrayMatterApiError, isAbortError } from "./errors";
export type { ApiErrorCode } from "./errors";
export type { Transport, RequestSpec } from "./transport";

/**
 * The application's API instance.
 *
 * Mock vs live is decided here and nowhere else. Set
 * `NEXT_PUBLIC_USE_MOCK_API=false` to point at the FastAPI backend; no feature
 * or component changes.
 */
export const api = new GrayMatterAPI(
  API_CONFIG.useMock
    ? new MockTransport()
    : new HttpTransport(API_CONFIG.baseUrl),
);

/** Escape hatch for tests and stories that need an isolated instance. */
export function createApi(transport = new MockTransport()): GrayMatterAPI {
  return new GrayMatterAPI(transport);
}
