/**
 * NovaPay — mock knowledge graph.
 *
 * This is a small but *internally consistent* graph, not a bag of fixtures.
 * Sources, entities, decisions and tickets are declared once; every
 * RelationshipPath is assembled from the shared RELATIONSHIPS edge list, so a
 * path can never reference a record that does not exist and `/health` counts
 * are derived rather than asserted.
 */

import type {
  Conflict,
  DecisionDetail,
  DecisionSummary,
  Entity,
  RelationshipEdge,
  RelationshipNode,
  RelationshipNodeType,
  RelationshipPath,
  Source,
  Ticket,
} from "@/types";

/* ---------------------------------------------------------------------------
 * Entities
 * ------------------------------------------------------------------------ */

export const ENTITIES: Record<string, Entity> = {
  "ENT-001": { id: "ENT-001", type: "service", name: "Payment Service" },
  "ENT-002": { id: "ENT-002", type: "service", name: "Authentication Service" },
  "ENT-003": { id: "ENT-003", type: "system", name: "Database Architecture" },
  "ENT-004": { id: "ENT-004", type: "system", name: "Transaction Monitoring" },
  "ENT-005": { id: "ENT-005", type: "process", name: "Database Migration" },
};

/* ---------------------------------------------------------------------------
 * Sources
 * ------------------------------------------------------------------------ */

export const SOURCES: Record<string, Source> = {
  "MTG-001": {
    id: "MTG-001",
    type: "meeting",
    title: "Payments Platform Kickoff",
    date: "2026-03-12",
    snippet:
      "Agreed the payments platform would be rebuilt around an event log rather than synchronous calls, so that settlement and monitoring could be added without further changes to the write path.",
  },
  "MTG-002": {
    id: "MTG-002",
    type: "meeting",
    title: "Authentication Hardening Review",
    date: "2026-05-21",
    snippet:
      "Security review concluded that service-to-service calls were still using long-lived static credentials. OAuth 2.1 client credentials was proposed as the replacement.",
  },
  "MTG-004": {
    id: "MTG-004",
    type: "meeting",
    title: "Database Architecture Meeting",
    date: "2026-09-08",
    snippet:
      "Reviewed datastore options for the Payment Service. MySQL's default isolation behaviour under concurrent settlement writes was raised as the deciding constraint. PostgreSQL was preferred for its transaction consistency guarantees and for existing operational familiarity in the platform team.",
  },
  "MTG-005": {
    id: "MTG-005",
    type: "meeting",
    title: "Q3 Reliability Review",
    date: "2026-09-16",
    snippet:
      "Payment reconciliation gaps were traced to missing real-time visibility over failed transactions. Agreed to fund a monitoring workstream before further payment changes ship.",
  },
  "DOC-001": {
    id: "DOC-001",
    type: "document",
    title: "Payment Architecture",
    date: "2026-02-02",
    snippet:
      "The Payment Service persists transactions to MySQL 8.0 in the primary region, with an asynchronous read replica used for reporting. All schema changes are applied through the migration runner.",
  },
  "DOC-007": {
    id: "DOC-007",
    type: "document",
    title: "Transaction Monitoring Specification",
    date: "2026-07-24",
    snippet:
      "Defines the event taxonomy emitted by the Payment Service and the alerting thresholds for failed, delayed and duplicate transactions.",
  },
  "DOC-009": {
    id: "DOC-009",
    type: "document",
    title: "Data Retention Policy",
    date: "2026-06-30",
    snippet:
      "Transaction records are retained for seven years from the date of settlement to satisfy financial reporting obligations. Deletion before that period requires written finance approval.",
  },
  "DOC-014": {
    id: "DOC-014",
    type: "document",
    title: "Payment Datastore Selection Record",
    date: "2026-09-11",
    snippet:
      "Records the selection of PostgreSQL 16 for the Payment Service. Cites serialisable isolation for settlement batches, native partitioning for the transaction table, and the team's existing PostgreSQL operational runbooks.",
  },
  "DOC-021": {
    id: "DOC-021",
    type: "document",
    title: "Authentication Service Design",
    date: "2026-06-04",
    snippet:
      "Describes token issuance, rotation and revocation for service-to-service authentication, replacing the static credential model documented in the original platform design.",
  },
  "MSG-031": {
    id: "MSG-031",
    type: "message",
    title: "#payments — migration cutover window",
    date: "2026-09-12",
    snippet:
      "Confirming the cutover window is Saturday 03:00–05:00 UTC. Dual-write stays on for two weeks after cutover before the MySQL cluster is decommissioned.",
  },
};

/* ---------------------------------------------------------------------------
 * Tickets
 * ------------------------------------------------------------------------ */

export const TICKETS: Record<string, Ticket> = {
  "PAY-101": {
    id: "PAY-101",
    key: "PAY-101",
    title: "Migrate payment datastore to PostgreSQL",
    status: "Done",
  },
  "PAY-118": {
    id: "PAY-118",
    key: "PAY-118",
    title: "Dual-write payment ledger during migration",
    status: "In Progress",
  },
  "PAY-133": {
    id: "PAY-133",
    key: "PAY-133",
    title: "Decommission MySQL payment cluster",
    status: "In Progress",
  },
  "AUTH-204": {
    id: "AUTH-204",
    key: "AUTH-204",
    title: "Rotate service credentials to OAuth 2.1",
    status: "Done",
  },
  "OPS-077": {
    id: "OPS-077",
    key: "OPS-077",
    title: "Add transaction monitoring alerts",
    status: "To Do",
  },
};

/* ---------------------------------------------------------------------------
 * Decisions
 * ------------------------------------------------------------------------ */

export const DECISIONS: Record<string, DecisionSummary> = {
  "DEC-001": {
    id: "DEC-001",
    title: "Adopt event-driven architecture for payments",
    date: "2026-03-20",
    status: "Implemented",
  },
  "DEC-002": {
    id: "DEC-002",
    title: "Standardise on OAuth 2.1 for service authentication",
    date: "2026-05-28",
    status: "Implemented",
  },
  "DEC-003": {
    id: "DEC-003",
    title: "Retain transaction records for seven years",
    date: "2026-07-02",
    status: "Approved",
  },
  "DEC-004": {
    id: "DEC-004",
    title: "Select PostgreSQL for Payment Service",
    date: "2026-09-10",
    status: "Implemented",
  },
  "DEC-005": {
    id: "DEC-005",
    title: "Introduce real-time transaction monitoring",
    date: "2026-09-16",
    status: "Approved",
  },
  "DEC-006": {
    id: "DEC-006",
    title: "Deprecate legacy settlement batch job",
    date: "2026-09-18",
    status: "Proposed",
  },
  "DEC-007": {
    id: "DEC-007",
    title: "Issue static service credentials from the platform vault",
    date: "2026-01-19",
    status: "Superseded",
  },
};

/* ---------------------------------------------------------------------------
 * The edge list — one declaration of every relationship in the graph
 * ------------------------------------------------------------------------ */

export const RELATIONSHIPS: RelationshipEdge[] = [
  // Payments platform lineage
  { from: "MTG-001", to: "DEC-001", label: "resulted in" },
  { from: "DEC-001", to: "ENT-001", label: "affects" },
  { from: "DEC-001", to: "DOC-007", label: "informed" },

  // Authentication lineage
  { from: "MTG-002", to: "DEC-002", label: "resulted in" },
  { from: "DEC-002", to: "DOC-021", label: "documented in" },
  { from: "DEC-002", to: "AUTH-204", label: "implemented by" },
  { from: "AUTH-204", to: "ENT-002", label: "affects" },
  { from: "DEC-002", to: "DEC-007", label: "supersedes" },

  // Retention lineage
  { from: "DOC-009", to: "DEC-003", label: "resulted in" },
  { from: "DEC-003", to: "ENT-001", label: "affects" },

  // DEC-004 — the demo path
  { from: "MTG-004", to: "DEC-004", label: "resulted in" },
  { from: "DEC-004", to: "PAY-101", label: "implemented by" },
  { from: "PAY-101", to: "ENT-001", label: "affects" },
  { from: "DEC-004", to: "DOC-014", label: "documented in" },
  { from: "DEC-004", to: "ENT-003", label: "affects" },
  { from: "DEC-004", to: "ENT-005", label: "initiates" },
  { from: "PAY-118", to: "ENT-005", label: "affects" },
  { from: "PAY-133", to: "ENT-005", label: "affects" },
  { from: "MSG-031", to: "ENT-005", label: "mentions" },
  { from: "ENT-001", to: "DOC-001", label: "documented in" },

  // Monitoring lineage
  { from: "DOC-007", to: "DEC-005", label: "resulted in" },
  { from: "MTG-005", to: "DEC-005", label: "resulted in" },
  { from: "DEC-005", to: "OPS-077", label: "implemented by" },
  { from: "OPS-077", to: "ENT-004", label: "affects" },
  { from: "ENT-004", to: "ENT-001", label: "monitors" },

  // Settlement deprecation
  { from: "DEC-001", to: "DEC-006", label: "informed" },
  { from: "DEC-006", to: "ENT-001", label: "affects" },
];

/* ---------------------------------------------------------------------------
 * Path assembly
 * ------------------------------------------------------------------------ */

const NODE_TYPE_BY_PREFIX: Record<string, RelationshipNodeType> = {
  MTG: "meeting",
  DOC: "document",
  MSG: "message",
  DEC: "decision",
  ENT: "entity",
  CHG: "change",
};

/** Resolve a record ID to the node the relationship renderer should draw. */
export function toNode(id: string): RelationshipNode {
  const prefix = id.split("-")[0];
  const type = NODE_TYPE_BY_PREFIX[prefix] ?? "ticket";

  switch (type) {
    case "entity":
      return { id, type, label: ENTITIES[id]?.name ?? id };
    case "decision":
      return { id, type, label: DECISIONS[id]?.title ?? id };
    case "ticket":
      return { id, type, label: TICKETS[id]?.title ?? id };
    case "change":
      return { id, type, label: id };
    default:
      return { id, type, label: SOURCES[id]?.title ?? id };
  }
}

/**
 * Build a path from a list of edges drawn from RELATIONSHIPS.
 * Node order follows first appearance, which is the order the renderer draws in.
 */
export function buildPath(edges: RelationshipEdge[]): RelationshipPath {
  const seen = new Set<string>();
  const nodes: RelationshipNode[] = [];

  for (const edge of edges) {
    for (const id of [edge.from, edge.to]) {
      if (!seen.has(id)) {
        seen.add(id);
        nodes.push(toNode(id));
      }
    }
  }

  return { nodes, edges };
}

/** Look up a declared relationship. Throws at module load if the edge is fictional. */
function edge(from: string, to: string): RelationshipEdge {
  const found = RELATIONSHIPS.find((r) => r.from === from && r.to === to);
  if (!found) {
    throw new Error(
      `Mock data error: relationship ${from} -> ${to} is not declared in RELATIONSHIPS.`,
    );
  }
  return found;
}

/* ---------------------------------------------------------------------------
 * Decision details
 * ------------------------------------------------------------------------ */

export const DECISION_DETAILS: Record<string, DecisionDetail> = {
  "DEC-004": {
    ...DECISIONS["DEC-004"],
    rationale:
      "The Payment Service requires strict transaction consistency across settlement batches. MySQL's default isolation behaviour permitted interleaved writes during concurrent settlement, which had already produced two reconciliation gaps in Q2. PostgreSQL provides serialisable isolation and native table partitioning for the transaction ledger, and the platform team already operates PostgreSQL for the ledger service, so no new operational capability is required.",
    decided_by: "Priya Sharma",
    evidence: [SOURCES["MTG-004"], SOURCES["DOC-014"]],
    path: buildPath([
      edge("MTG-004", "DEC-004"),
      edge("DEC-004", "PAY-101"),
      edge("PAY-101", "ENT-001"),
      edge("DEC-004", "DOC-014"),
    ]),
    implemented_by: [TICKETS["PAY-101"]],
    affects: [ENTITIES["ENT-001"], ENTITIES["ENT-003"], ENTITIES["ENT-005"]],
  },

  "DEC-001": {
    ...DECISIONS["DEC-001"],
    rationale:
      "Synchronous calls between payment, settlement and monitoring meant every new consumer required a change to the payment write path. Moving to an append-only event log decouples consumers from the write path and gives settlement a replayable record.",
    decided_by: "Marcus Webb",
    evidence: [SOURCES["MTG-001"]],
    path: buildPath([edge("MTG-001", "DEC-001"), edge("DEC-001", "ENT-001")]),
    implemented_by: [],
    affects: [ENTITIES["ENT-001"]],
  },

  "DEC-002": {
    ...DECISIONS["DEC-002"],
    rationale:
      "Service-to-service calls authenticated with long-lived static credentials issued from the platform vault. Rotation was manual and had not been performed since issuance. OAuth 2.1 client credentials moves token lifetime to minutes and makes revocation immediate.",
    decided_by: "Priya Sharma",
    evidence: [SOURCES["MTG-002"], SOURCES["DOC-021"]],
    path: buildPath([
      edge("MTG-002", "DEC-002"),
      edge("DEC-002", "AUTH-204"),
      edge("AUTH-204", "ENT-002"),
      edge("DEC-002", "DOC-021"),
      edge("DEC-002", "DEC-007"),
    ]),
    implemented_by: [TICKETS["AUTH-204"]],
    affects: [ENTITIES["ENT-002"]],
  },

  "DEC-003": {
    ...DECISIONS["DEC-003"],
    rationale:
      "Financial reporting obligations require transaction records to remain retrievable for seven years from settlement. The retention window is set at the datastore rather than in application code so that it survives service rewrites.",
    decided_by: "Anna Kowalski",
    evidence: [SOURCES["DOC-009"]],
    path: buildPath([edge("DOC-009", "DEC-003"), edge("DEC-003", "ENT-001")]),
    implemented_by: [],
    affects: [ENTITIES["ENT-001"]],
  },

  "DEC-005": {
    ...DECISIONS["DEC-005"],
    rationale:
      "Reconciliation gaps were being discovered days after settlement because failed and duplicate transactions produced no alert. Real-time monitoring over the payment event stream closes the detection window to minutes.",
    decided_by: "Marcus Webb",
    evidence: [SOURCES["MTG-005"], SOURCES["DOC-007"]],
    path: buildPath([
      edge("DOC-007", "DEC-005"),
      edge("MTG-005", "DEC-005"),
      edge("DEC-005", "OPS-077"),
      edge("OPS-077", "ENT-004"),
      edge("ENT-004", "ENT-001"),
    ]),
    implemented_by: [TICKETS["OPS-077"]],
    affects: [ENTITIES["ENT-004"], ENTITIES["ENT-001"]],
  },

  "DEC-006": {
    ...DECISIONS["DEC-006"],
    rationale:
      "The nightly settlement batch predates the payment event log and now duplicates work the stream processor already performs. Deprecating it removes a second source of settlement truth.",
    decided_by: "Marcus Webb",
    evidence: [SOURCES["MTG-001"]],
    path: buildPath([edge("DEC-001", "DEC-006"), edge("DEC-006", "ENT-001")]),
    implemented_by: [],
    affects: [ENTITIES["ENT-001"]],
  },

  "DEC-007": {
    ...DECISIONS["DEC-007"],
    rationale:
      "Static credentials were issued from the platform vault to give services a single credential source. Superseded by DEC-002 after the authentication hardening review found that rotation was never performed in practice.",
    decided_by: "Priya Sharma",
    evidence: [SOURCES["DOC-021"]],
    path: buildPath([edge("DEC-002", "DEC-007")]),
    implemented_by: [],
    affects: [ENTITIES["ENT-002"]],
  },
};

/* ---------------------------------------------------------------------------
 * Conflicts
 * ------------------------------------------------------------------------ */

/** DEC-004 rendered as a citable source, so a decision can be its own evidence. */
const DEC_004_AS_SOURCE: Source = {
  id: "DEC-004",
  type: "decision",
  title: "Select PostgreSQL for Payment Service",
  date: "2026-09-10",
  snippet:
    "The Payment Service will persist transactions to PostgreSQL 16. Decided by Priya Sharma following the Database Architecture Meeting on 8 September 2026.",
};

export const CONFLICTS: Conflict[] = [
  {
    id: "CFL-001",
    entity: "Payment Service",
    existing_value: "MySQL",
    proposed_value: "PostgreSQL",
    evidence: [SOURCES["DOC-001"], DEC_004_AS_SOURCE],
    severity: "high",
    requires_review: true,
  },
];

/* ---------------------------------------------------------------------------
 * Analyze — the Truth Engine demo case
 * ------------------------------------------------------------------------ */

export const ANALYZE_DEMO = {
  /** Change strings containing all of these tokens resolve to the demo case. */
  match: ["payment", "postgres"],

  affected: [
    ENTITIES["ENT-001"],
    ENTITIES["ENT-003"],
    ENTITIES["ENT-005"],
    ENTITIES["ENT-004"],
  ],
  related_decisions: [DECISIONS["DEC-004"]],
  related_tickets: [TICKETS["PAY-101"], TICKETS["PAY-133"]],
  conflicts: CONFLICTS,
  path: buildPath([
    edge("MTG-004", "DEC-004"),
    edge("DEC-004", "PAY-101"),
    edge("PAY-101", "ENT-001"),
    edge("ENT-001", "DOC-001"),
  ]),
};

/* ---------------------------------------------------------------------------
 * Ask — canned answers
 *
 * Keyword-matched. The fallback deliberately returns no evidence and a null
 * path: "nothing found" is a real answer in this product and the UI has to
 * render it as well as it renders a hit.
 * ------------------------------------------------------------------------ */

export interface AskFixture {
  keywords: string[];
  answer: string;
  evidence: Source[];
  path: RelationshipPath | null;
  related_decisions: DecisionSummary[];
}

export const ASK_FIXTURES: AskFixture[] = [
  {
    keywords: ["postgres", "database", "datastore", "mysql", "dec-004"],
    answer:
      "The Payment Service uses PostgreSQL because MySQL's isolation behaviour under concurrent settlement writes produced reconciliation gaps in Q2 2026. Evidence indicates the choice was made at the Database Architecture Meeting on 8 September 2026 and recorded as DEC-004 by Priya Sharma. It is implemented by PAY-101 and documented in the Payment Datastore Selection Record.",
    evidence: [SOURCES["MTG-004"], SOURCES["DOC-014"], SOURCES["DOC-001"]],
    path: buildPath([
      edge("MTG-004", "DEC-004"),
      edge("DEC-004", "PAY-101"),
      edge("PAY-101", "ENT-001"),
      edge("DEC-004", "DOC-014"),
    ]),
    related_decisions: [DECISIONS["DEC-004"]],
  },
  {
    keywords: ["monitoring", "alert", "transaction monitoring", "reconciliation"],
    answer:
      "Transaction monitoring exists because reconciliation gaps were being found days after settlement, with no alert on failed or duplicate transactions. Evidence indicates the requirement originated in the payments platform kickoff, was specified in the Transaction Monitoring Specification, and was approved as DEC-005 following the Q3 Reliability Review. OPS-077 is the implementing ticket and is not yet started.",
    evidence: [SOURCES["MTG-005"], SOURCES["DOC-007"], SOURCES["MTG-001"]],
    // Seven nodes: exercises the >6 collapse behaviour in the path renderer.
    path: buildPath([
      edge("MTG-001", "DEC-001"),
      edge("DEC-001", "DOC-007"),
      edge("DOC-007", "DEC-005"),
      edge("DEC-005", "OPS-077"),
      edge("OPS-077", "ENT-004"),
      edge("ENT-004", "ENT-001"),
    ]),
    related_decisions: [DECISIONS["DEC-005"], DECISIONS["DEC-001"]],
  },
  {
    keywords: ["auth", "oauth", "credential", "authentication", "token"],
    answer:
      "Service-to-service authentication uses OAuth 2.1 client credentials. Evidence indicates this replaced static vault-issued credentials after the Authentication Hardening Review found that rotation had never been performed. DEC-002 supersedes DEC-007 and was implemented by AUTH-204.",
    evidence: [SOURCES["MTG-002"], SOURCES["DOC-021"]],
    path: buildPath([
      edge("MTG-002", "DEC-002"),
      edge("DEC-002", "AUTH-204"),
      edge("AUTH-204", "ENT-002"),
      edge("DEC-002", "DEC-007"),
    ]),
    related_decisions: [DECISIONS["DEC-002"], DECISIONS["DEC-007"]],
  },
  {
    keywords: ["retention", "seven years", "retain", "policy", "compliance"],
    answer:
      "Transaction records are retained for seven years from settlement. Evidence indicates the requirement comes from financial reporting obligations recorded in the Data Retention Policy, and was approved as DEC-003. The retention window is enforced at the datastore rather than in application code.",
    evidence: [SOURCES["DOC-009"]],
    path: buildPath([edge("DOC-009", "DEC-003"), edge("DEC-003", "ENT-001")]),
    related_decisions: [DECISIONS["DEC-003"]],
  },
];

export const ASK_FALLBACK: Omit<AskFixture, "keywords"> = {
  answer:
    "No indexed source addresses this question. Searched 10 sources, 5 entities and 7 decisions across the NovaPay corpus. Narrow the question to a named service, decision or document, or connect the system that holds this information.",
  evidence: [],
  path: null,
  related_decisions: [],
};

/* ---------------------------------------------------------------------------
 * Derived counts — /health reports what is actually in the graph
 * ------------------------------------------------------------------------ */

export const GRAPH_COUNTS = {
  sources: Object.keys(SOURCES).length,
  entities: Object.keys(ENTITIES).length,
  relationships: RELATIONSHIPS.length,
  decisions: Object.keys(DECISIONS).length,
  conflicts: CONFLICTS.length,
};
