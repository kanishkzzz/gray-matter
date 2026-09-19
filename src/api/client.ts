import type {
  AnalyzeResponse,
  AskResponse,
  DecisionDetail,
  DecisionsResponse,
  HealthResponse,
} from "@/types";
import type { Transport } from "./transport";

/**
 * The only object that talks to the knowledge graph.
 *
 * Features call these methods. Components never do — they take props.
 * One method per endpoint in the contract, nothing more.
 */
export class GrayMatterAPI {
  constructor(private readonly transport: Transport) {}

  /** `GET /health` — graph size and conflict count. */
  health(signal?: AbortSignal): Promise<HealthResponse> {
    return this.transport.request<HealthResponse>({
      method: "GET",
      path: "/health",
      signal,
    });
  }

  /** `POST /ask` — natural-language question against the corpus. */
  ask(question: string, signal?: AbortSignal): Promise<AskResponse> {
    return this.transport.request<AskResponse>({
      method: "POST",
      path: "/ask",
      body: { question },
      signal,
    });
  }

  /** `GET /decisions` — every decision, newest first. */
  listDecisions(signal?: AbortSignal): Promise<DecisionsResponse> {
    return this.transport.request<DecisionsResponse>({
      method: "GET",
      path: "/decisions",
      signal,
    });
  }

  /** `GET /decisions/{id}` — full trace for one decision. */
  getDecision(id: string, signal?: AbortSignal): Promise<DecisionDetail> {
    return this.transport.request<DecisionDetail>({
      method: "GET",
      path: `/decisions/${encodeURIComponent(id)}`,
      signal,
    });
  }

  /** `POST /analyze` — Truth Engine. Impact and conflicts for a proposed change. */
  analyze(change: string, signal?: AbortSignal): Promise<AnalyzeResponse> {
    return this.transport.request<AnalyzeResponse>({
      method: "POST",
      path: "/analyze",
      body: { change },
      signal,
    });
  }
}
