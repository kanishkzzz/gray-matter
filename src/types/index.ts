/**
 * Gray Matter API contract.
 *
 * These shapes are fixed. They are the single source of truth shared by the
 * mock transport and the live FastAPI backend. Changing anything here is a
 * contract change, not a refactor.
 *
 * Field names are snake_case because the backend is Python. They are not
 * renamed on the way in — a camelCase mapping layer would be one more place
 * for the mock and the live API to drift apart.
 */

/* ---------------------------------------------------------------------------
 * Enumerations
 * ------------------------------------------------------------------------ */

/** A Source is anything the graph can cite. Decisions can cite other decisions. */
export type SourceType =
  | "meeting"
  | "document"
  | "ticket"
  | "message"
  | "decision";

export type EntityType = "service" | "system" | "process" | "component" | "team";

export type DecisionStatus =
  | "Implemented"
  | "Approved"
  | "Proposed"
  | "Superseded"
  | "Rejected";

export type TicketStatus = "Done" | "In Progress" | "To Do" | "Blocked";

export type ConflictSeverity = "high" | "medium" | "low";

/** Node kinds the relationship renderer knows how to draw. */
export type RelationshipNodeType =
  | "meeting"
  | "document"
  | "message"
  | "decision"
  | "ticket"
  | "entity"
  | "change";

/* ---------------------------------------------------------------------------
 * Records
 * ------------------------------------------------------------------------ */

export interface Source {
  id: string;
  type: SourceType;
  title: string;
  /** ISO-8601 date, `YYYY-MM-DD`. */
  date: string;
  snippet: string;
}

export interface Entity {
  id: string;
  type: EntityType;
  name: string;
}

export interface Ticket {
  id: string;
  /** Human-facing tracker key, e.g. `PAY-101`. */
  key: string;
  title: string;
  status: TicketStatus;
}

export interface DecisionSummary {
  id: string;
  title: string;
  /** ISO-8601 date, `YYYY-MM-DD`. */
  date: string;
  status: DecisionStatus;
}

export interface Conflict {
  id: string;
  /** Name of the entity the conflict is about, e.g. `Payment Service`. */
  entity: string;
  existing_value: string;
  proposed_value: string;
  /** Sources supporting both sides. Never empty — a conflict without evidence is not reportable. */
  evidence: Source[];
  severity: ConflictSeverity;
  requires_review: boolean;
}

/* ---------------------------------------------------------------------------
 * Relationship path — the product's central structure
 * ------------------------------------------------------------------------ */

export interface RelationshipNode {
  id: string;
  type: RelationshipNodeType;
  label: string;
}

export interface RelationshipEdge {
  /** `RelationshipNode.id` of the source node. */
  from: string;
  /** `RelationshipNode.id` of the target node. */
  to: string;
  /** Edge verb, rendered in mono uppercase, e.g. `resulted in`. */
  label: string;
}

export interface RelationshipPath {
  nodes: RelationshipNode[];
  edges: RelationshipEdge[];
}

/* ---------------------------------------------------------------------------
 * Endpoint payloads
 * ------------------------------------------------------------------------ */

/** `GET /health` */
export interface HealthResponse {
  status: string;
  sources: number;
  entities: number;
  relationships: number;
  decisions: number;
  conflicts: number;
}

/** `POST /ask` request */
export interface AskRequest {
  question: string;
}

/** `POST /ask` response */
export interface AskResponse {
  answer: string;
  evidence: Source[];
  path: RelationshipPath | null;
  related_decisions: DecisionSummary[];
}

/** `GET /decisions` */
export interface DecisionsResponse {
  decisions: DecisionSummary[];
}

/** `GET /decisions/{id}` */
export interface DecisionDetail {
  id: string;
  title: string;
  /** ISO-8601 date, `YYYY-MM-DD`. */
  date: string;
  status: DecisionStatus;
  rationale: string;
  decided_by: string;
  evidence: Source[];
  path: RelationshipPath;
  implemented_by: Ticket[];
  affects: Entity[];
}

/** `POST /analyze` request */
export interface AnalyzeRequest {
  change: string;
}

/** `POST /analyze` response */
export interface AnalyzeResponse {
  affected: Entity[];
  related_decisions: DecisionSummary[];
  related_tickets: Ticket[];
  conflicts: Conflict[];
  path: RelationshipPath;
}
