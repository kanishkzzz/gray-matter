"""
NovaPay - the seeded knowledge graph.

Ported from `src/api/mock/data.ts`, which describes itself as "a small but
*internally consistent* graph, not a bag of fixtures". That property is kept
here and enforced at import time by `GraphStore.validate()`: every edge, every
piece of evidence and every assertion must name a record that exists.

The seed exists so the product runs with no LLM key, no vector store and no
ingested corpus. Ingested content is added on top of it, never instead of it.
"""

from __future__ import annotations

from .records import (
    Assertion,
    DecisionRecord,
    Edge,
    EntityRecord,
    SourceRecord,
    TicketRecord,
)

# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------

ENTITIES: list[EntityRecord] = [
    EntityRecord(
        "ENT-001",
        "service",
        "Payment Service",
        aliases=("payments", "payment", "payment platform"),
    ),
    EntityRecord(
        "ENT-002",
        "service",
        "Authentication Service",
        aliases=("auth", "authentication", "auth service"),
    ),
    EntityRecord(
        "ENT-003",
        "system",
        "Database Architecture",
        aliases=("datastore", "database"),
    ),
    EntityRecord(
        "ENT-004",
        "system",
        "Transaction Monitoring",
        aliases=("monitoring", "alerting", "alerts"),
    ),
    EntityRecord(
        "ENT-005",
        "process",
        "Database Migration",
        aliases=("migration", "cutover"),
    ),
]

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

SOURCES: list[SourceRecord] = [
    SourceRecord(
        "MTG-001",
        "meeting",
        "Payments Platform Kickoff",
        "2026-03-12",
        "Agreed the payments platform would be rebuilt around an event log "
        "rather than synchronous calls, so that settlement and monitoring "
        "could be added without further changes to the write path.",
        keywords=("event driven", "event log", "architecture", "kickoff"),
    ),
    SourceRecord(
        "MTG-002",
        "meeting",
        "Authentication Hardening Review",
        "2026-05-21",
        "Security review concluded that service-to-service calls were still "
        "using long-lived static credentials. OAuth 2.1 client credentials "
        "was proposed as the replacement.",
        keywords=("oauth", "credential", "security", "token", "rotation"),
    ),
    SourceRecord(
        "MTG-004",
        "meeting",
        "Database Architecture Meeting",
        "2026-09-08",
        "Reviewed datastore options for the Payment Service. MySQL's default "
        "isolation behaviour under concurrent settlement writes was raised as "
        "the deciding constraint. PostgreSQL was preferred for its "
        "transaction consistency guarantees and for existing operational "
        "familiarity in the platform team.",
        keywords=("postgres", "postgresql", "mysql", "datastore", "isolation"),
    ),
    SourceRecord(
        "MTG-005",
        "meeting",
        "Q3 Reliability Review",
        "2026-09-16",
        "Payment reconciliation gaps were traced to missing real-time "
        "visibility over failed transactions. Agreed to fund a monitoring "
        "workstream before further payment changes ship.",
        keywords=("reconciliation", "monitoring", "reliability", "alert"),
    ),
    SourceRecord(
        "DOC-001",
        "document",
        "Payment Architecture",
        "2026-02-02",
        "The Payment Service persists transactions to MySQL 8.0 in the "
        "primary region, with an asynchronous read replica used for "
        "reporting. All schema changes are applied through the migration "
        "runner.",
        keywords=(
            "mysql",
            "datastore",
            "database",
            "replica",
            "persists",
            "schema",
        ),
    ),
    SourceRecord(
        "DOC-007",
        "document",
        "Transaction Monitoring Specification",
        "2026-07-24",
        "Defines the event taxonomy emitted by the Payment Service and the "
        "alerting thresholds for failed, delayed and duplicate transactions.",
        keywords=(
            "monitoring",
            "alert",
            "alerting",
            "threshold",
            "taxonomy",
            "failed",
            "duplicate",
        ),
    ),
    SourceRecord(
        "DOC-009",
        "document",
        "Data Retention Policy",
        "2026-06-30",
        "Transaction records are retained for seven years from the date of "
        "settlement to satisfy financial reporting obligations. Deletion "
        "before that period requires written finance approval.",
        keywords=(
            "retention",
            "retain",
            "retained",
            "records",
            "transaction",
            "seven years",
            "policy",
            "compliance",
            "archive",
        ),
    ),
    SourceRecord(
        "DOC-014",
        "document",
        "Payment Datastore Selection Record",
        "2026-09-11",
        "Records the selection of PostgreSQL 16 for the Payment Service. "
        "Cites serialisable isolation for settlement batches, native "
        "partitioning for the transaction table, and the team's existing "
        "PostgreSQL operational runbooks.",
        keywords=(
            "postgres",
            "postgresql",
            "database",
            "datastore",
            "selection",
            "isolation",
            "partitioning",
        ),
    ),
    SourceRecord(
        "DOC-021",
        "document",
        "Authentication Service Design",
        "2026-06-04",
        "Describes token issuance, rotation and revocation for "
        "service-to-service authentication, replacing the static credential "
        "model documented in the original platform design.",
        keywords=(
            "oauth",
            "token",
            "authentication",
            "authenticate",
            "credential",
            "rotation",
            "revocation",
        ),
    ),
    SourceRecord(
        "MSG-031",
        "message",
        "#payments - migration cutover window",
        "2026-09-12",
        "Confirming the cutover window is Saturday 03:00-05:00 UTC. "
        "Dual-write stays on for two weeks after cutover before the MySQL "
        "cluster is decommissioned.",
        keywords=("cutover", "migration", "dual write", "mysql"),
    ),
]

# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

TICKETS: list[TicketRecord] = [
    TicketRecord(
        "PAY-101", "PAY-101", "Migrate payment datastore to PostgreSQL", "Done"
    ),
    TicketRecord(
        "PAY-118",
        "PAY-118",
        "Dual-write payment ledger during migration",
        "In Progress",
    ),
    TicketRecord(
        "PAY-133", "PAY-133", "Decommission MySQL payment cluster", "In Progress"
    ),
    TicketRecord(
        "AUTH-204", "AUTH-204", "Rotate service credentials to OAuth 2.1", "Done"
    ),
    TicketRecord("OPS-077", "OPS-077", "Add transaction monitoring alerts", "To Do"),
]

# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------

DECISIONS: list[DecisionRecord] = [
    DecisionRecord(
        "DEC-001",
        "Adopt event-driven architecture for payments",
        "2026-03-20",
        "Implemented",
        rationale=(
            "Synchronous calls between payment, settlement and monitoring "
            "meant every new consumer required a change to the payment write "
            "path. Moving to an append-only event log decouples consumers "
            "from the write path and gives settlement a replayable record."
        ),
        decided_by="Marcus Webb",
        evidence=("MTG-001",),
        keywords=("event driven", "event log", "architecture"),
    ),
    DecisionRecord(
        "DEC-002",
        "Standardise on OAuth 2.1 for service authentication",
        "2026-05-28",
        "Implemented",
        rationale=(
            "Service-to-service calls authenticated with long-lived static "
            "credentials issued from the platform vault. Rotation was manual "
            "and had not been performed since issuance. OAuth 2.1 client "
            "credentials moves token lifetime to minutes and makes revocation "
            "immediate."
        ),
        decided_by="Priya Sharma",
        evidence=("MTG-002", "DOC-021"),
        keywords=(
            "oauth",
            "authentication",
            "authenticate",
            "credential",
            "token",
            "auth",
            "service-to-service",
        ),
    ),
    DecisionRecord(
        "DEC-003",
        "Retain transaction records for seven years",
        "2026-07-02",
        "Approved",
        rationale=(
            "Financial reporting obligations require transaction records to "
            "remain retrievable for seven years from settlement. The "
            "retention window is set at the datastore rather than in "
            "application code so that it survives service rewrites."
        ),
        decided_by="Anna Kowalski",
        evidence=("DOC-009",),
        keywords=(
            "retention",
            "retain",
            "retained",
            "records",
            "seven years",
            "policy",
            "compliance",
        ),
    ),
    DecisionRecord(
        "DEC-004",
        "Select PostgreSQL for Payment Service",
        "2026-09-10",
        "Implemented",
        rationale=(
            "The Payment Service requires strict transaction consistency "
            "across settlement batches. MySQL's default isolation behaviour "
            "permitted interleaved writes during concurrent settlement, which "
            "had already produced two reconciliation gaps in Q2. PostgreSQL "
            "provides serialisable isolation and native table partitioning "
            "for the transaction ledger, and the platform team already "
            "operates PostgreSQL for the ledger service, so no new "
            "operational capability is required."
        ),
        decided_by="Priya Sharma",
        evidence=("MTG-004", "DOC-014"),
        keywords=("postgres", "postgresql", "database", "datastore", "mysql"),
    ),
    DecisionRecord(
        "DEC-005",
        "Introduce real-time transaction monitoring",
        "2026-09-16",
        "Approved",
        rationale=(
            "Reconciliation gaps were being discovered days after settlement "
            "because failed and duplicate transactions produced no alert. "
            "Real-time monitoring over the payment event stream closes the "
            "detection window to minutes."
        ),
        decided_by="Marcus Webb",
        evidence=("MTG-005", "DOC-007"),
        keywords=("monitoring", "alert", "reconciliation", "transaction monitoring"),
    ),
    DecisionRecord(
        "DEC-006",
        "Deprecate legacy settlement batch job",
        "2026-09-18",
        "Proposed",
        rationale=(
            "The nightly settlement batch predates the payment event log and "
            "now duplicates work the stream processor already performs. "
            "Deprecating it removes a second source of settlement truth."
        ),
        decided_by="Marcus Webb",
        evidence=("MTG-001",),
        keywords=("settlement", "batch", "deprecate"),
    ),
    DecisionRecord(
        "DEC-007",
        "Issue static service credentials from the platform vault",
        "2026-01-19",
        "Superseded",
        rationale=(
            "Static credentials were issued from the platform vault to give "
            "services a single credential source. Superseded by DEC-002 after "
            "the authentication hardening review found that rotation was "
            "never performed in practice."
        ),
        decided_by="Priya Sharma",
        evidence=("DOC-021",),
        keywords=("credential", "vault", "static", "auth"),
    ),
]

# ---------------------------------------------------------------------------
# The edge list - one declaration of every relationship in the graph
# ---------------------------------------------------------------------------

EDGES: list[Edge] = [
    # Payments platform lineage
    Edge("MTG-001", "DEC-001", "resulted in"),
    Edge("DEC-001", "ENT-001", "affects"),
    Edge("DEC-001", "DOC-007", "informed"),
    # Authentication lineage
    Edge("MTG-002", "DEC-002", "resulted in"),
    Edge("DEC-002", "DOC-021", "documented in"),
    Edge("DEC-002", "AUTH-204", "implemented by"),
    Edge("AUTH-204", "ENT-002", "affects"),
    Edge("DEC-002", "DEC-007", "supersedes"),
    # Retention lineage
    Edge("DOC-009", "DEC-003", "resulted in"),
    Edge("DEC-003", "ENT-001", "affects"),
    # DEC-004 - the demo path
    Edge("MTG-004", "DEC-004", "resulted in"),
    Edge("DEC-004", "PAY-101", "implemented by"),
    Edge("PAY-101", "ENT-001", "affects"),
    Edge("DEC-004", "DOC-014", "documented in"),
    Edge("DEC-004", "ENT-003", "affects"),
    Edge("DEC-004", "ENT-005", "initiates"),
    Edge("PAY-118", "ENT-005", "affects"),
    Edge("PAY-133", "ENT-005", "affects"),
    Edge("MSG-031", "ENT-005", "mentions"),
    Edge("ENT-001", "DOC-001", "documented in"),
    # Monitoring lineage
    Edge("DOC-007", "DEC-005", "resulted in"),
    Edge("MTG-005", "DEC-005", "resulted in"),
    Edge("DEC-005", "OPS-077", "implemented by"),
    Edge("OPS-077", "ENT-004", "affects"),
    Edge("ENT-004", "ENT-001", "monitors"),
    # Settlement deprecation
    Edge("DEC-001", "DEC-006", "informed"),
    Edge("DEC-006", "ENT-001", "affects"),
]

# ---------------------------------------------------------------------------
# Assertions - what each source claims about one attribute of one entity
#
# `/analyze` compares a proposed change against these. CFL-001 in the mock
# data (Payment Service: MySQL vs PostgreSQL) falls out of the first two
# entries rather than being written down as a conflict.
# ---------------------------------------------------------------------------

_DATASTORE_TERMS = ("database", "datastore", "db", "store", "persistence")
_AUTH_TERMS = ("auth", "authentication", "credential", "credentials")

ASSERTIONS: list[Assertion] = [
    Assertion(
        "ENT-001",
        "datastore",
        "MySQL",
        asserted_by="DOC-001",
        attribute_terms=_DATASTORE_TERMS,
    ),
    Assertion(
        "ENT-001",
        "datastore",
        "PostgreSQL",
        asserted_by="DEC-004",
        attribute_terms=_DATASTORE_TERMS,
    ),
    Assertion(
        "ENT-002",
        "authentication",
        "static vault credentials",
        asserted_by="DEC-007",
        attribute_terms=_AUTH_TERMS,
    ),
    Assertion(
        "ENT-002",
        "authentication",
        "OAuth 2.1 client credentials",
        asserted_by="DEC-002",
        attribute_terms=_AUTH_TERMS,
    ),
    Assertion(
        "ENT-001",
        "retention",
        "seven years from settlement",
        asserted_by="DEC-003",
        attribute_terms=("retention", "retain", "archive", "delete", "purge"),
    ),
]

# ---------------------------------------------------------------------------
# Vocabulary the change parser recognises as a concrete technology value.
# ---------------------------------------------------------------------------

KNOWN_VALUES: dict[str, str] = {
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "dynamodb": "DynamoDB",
    "cassandra": "Cassandra",
    "sqlite": "SQLite",
    "redis": "Redis",
    "oauth 2.1": "OAuth 2.1 client credentials",
    "oauth": "OAuth 2.1 client credentials",
    "saml": "SAML",
    "mtls": "mutual TLS",
}
