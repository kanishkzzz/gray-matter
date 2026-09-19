/**
 * A single error type for every API failure, so feature code has one thing to
 * catch and error states have one shape to render.
 */

export type ApiErrorCode =
  | "network" /** request never reached the server */
  | "http" /** server responded with a non-2xx status */
  | "not_found" /** 404 — a record that does not exist */
  | "parse" /** response was not the shape we expect */
  | "aborted"; /** caller cancelled the request */

export class GrayMatterApiError extends Error {
  readonly code: ApiErrorCode;
  readonly status: number | null;
  readonly endpoint: string;

  constructor(
    code: ApiErrorCode,
    message: string,
    options: { status?: number | null; endpoint: string; cause?: unknown },
  ) {
    super(message, { cause: options.cause });
    this.name = "GrayMatterApiError";
    this.code = code;
    this.status = options.status ?? null;
    this.endpoint = options.endpoint;
  }

  get isAborted(): boolean {
    return this.code === "aborted";
  }

  /** Copy shown to the user. Never blames the user, never says "the AI". */
  get userMessage(): string {
    switch (this.code) {
      case "not_found":
        return "That record is not in the knowledge graph.";
      case "network":
        return "The knowledge graph could not be reached.";
      case "parse":
        return "The knowledge graph returned a response this build cannot read.";
      case "aborted":
        return "Request cancelled.";
      case "http":
      default:
        return "The knowledge graph returned an error.";
    }
  }
}

export function isAbortError(error: unknown): boolean {
  if (error instanceof GrayMatterApiError) return error.isAborted;
  return error instanceof DOMException && error.name === "AbortError";
}
