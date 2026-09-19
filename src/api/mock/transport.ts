import { API_CONFIG } from "../config";
import { GrayMatterApiError } from "../errors";
import type { RequestSpec, Transport } from "../transport";
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  AskRequest,
  AskResponse,
  DecisionsResponse,
  HealthResponse,
} from "@/types";
import {
  ANALYZE_DEMO,
  ASK_FALLBACK,
  ASK_FIXTURES,
  DECISIONS,
  DECISION_DETAILS,
  ENTITIES,
  GRAPH_COUNTS,
} from "./data";

/**
 * In-memory transport. Routes on path exactly as the HTTP transport does, so
 * the client class runs the same code against both.
 */
export class MockTransport implements Transport {
  async request<T>({ method, path, body, signal }: RequestSpec): Promise<T> {
    await delay(signal, path);

    const route = `${method} ${path.split("?")[0]}`;

    if (route === "GET /health") {
      return health() as T;
    }

    if (route === "GET /decisions") {
      return decisions() as T;
    }

    const decisionMatch = path.match(/^\/decisions\/([^/]+)$/);
    if (method === "GET" && decisionMatch) {
      return decision(decodeURIComponent(decisionMatch[1])) as T;
    }

    if (route === "POST /ask") {
      return ask((body as AskRequest).question) as T;
    }

    if (route === "POST /analyze") {
      return analyze((body as AnalyzeRequest).change) as T;
    }

    throw new GrayMatterApiError("not_found", `No mock route for ${route}.`, {
      status: 404,
      endpoint: path,
    });
  }
}

/* -------------------------------------------------------------------------- */
/* Handlers                                                                   */
/* -------------------------------------------------------------------------- */

function health(): HealthResponse {
  return { status: "ok", ...GRAPH_COUNTS };
}

function decisions(): DecisionsResponse {
  return {
    decisions: clone(
      Object.values(DECISIONS).sort((a, b) => b.date.localeCompare(a.date)),
    ),
  };
}

function decision(id: string) {
  const found = DECISION_DETAILS[id.toUpperCase()];
  if (!found) {
    throw new GrayMatterApiError("not_found", `No decision ${id}.`, {
      status: 404,
      endpoint: `/decisions/${id}`,
    });
  }
  return clone(found);
}

function ask(question: string): AskResponse {
  const q = question.toLowerCase();

  const best = ASK_FIXTURES.map((fixture) => ({
    fixture,
    score: fixture.keywords.filter((k) => q.includes(k)).length,
  }))
    .filter((candidate) => candidate.score > 0)
    .sort((a, b) => b.score - a.score)[0];

  const source = best?.fixture ?? ASK_FALLBACK;

  return clone({
    answer: source.answer,
    evidence: source.evidence,
    path: source.path,
    related_decisions: source.related_decisions,
  });
}

function analyze(change: string): AnalyzeResponse {
  const c = change.toLowerCase();

  // The demo case: a payment datastore change.
  if (ANALYZE_DEMO.match.every((token) => c.includes(token))) {
    return clone({
      affected: ANALYZE_DEMO.affected,
      related_decisions: ANALYZE_DEMO.related_decisions,
      related_tickets: ANALYZE_DEMO.related_tickets,
      conflicts: ANALYZE_DEMO.conflicts,
      path: ANALYZE_DEMO.path,
    });
  }

  // Anything else: name-match entities only. No conflict is invented, and an
  // empty result stays empty — the UI has to render "nothing found" honestly.
  const affected = Object.values(ENTITIES).filter((entity) =>
    c.includes(entity.name.toLowerCase()),
  );

  return clone({
    affected,
    related_decisions: [],
    related_tickets: [],
    conflicts: [],
    path: { nodes: [], edges: [] },
  });
}

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

/** Fixtures are shared module state; hand callers a copy they can safely hold. */
function clone<T>(value: T): T {
  return structuredClone(value);
}

function delay(signal: AbortSignal | undefined, endpoint: string): Promise<void> {
  const { min, max } = API_CONFIG.mockLatencyMs;
  const ms = min + Math.random() * (max - min);

  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(
        new GrayMatterApiError("aborted", "Request cancelled.", { endpoint }),
      );
      return;
    }

    const timer = setTimeout(() => {
      signal?.removeEventListener("abort", onAbort);
      resolve();
    }, ms);

    function onAbort() {
      clearTimeout(timer);
      reject(
        new GrayMatterApiError("aborted", "Request cancelled.", { endpoint }),
      );
    }

    signal?.addEventListener("abort", onAbort, { once: true });
  });
}
