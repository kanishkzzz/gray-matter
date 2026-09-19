/**
 * API configuration.
 *
 * `process.env.NEXT_PUBLIC_*` must be referenced statically so Next can inline
 * the values at build time — do not refactor these into dynamic lookups.
 */

/** Mock mode is on unless explicitly disabled, so the app runs with no .env. */
const useMock = process.env.NEXT_PUBLIC_USE_MOCK_API !== "false";

export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  useMock,
  /** Simulated latency band for mock mode, in milliseconds. */
  mockLatencyMs: { min: 300, max: 600 },
} as const;
