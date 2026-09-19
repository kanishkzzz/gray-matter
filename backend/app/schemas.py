"""
Gray Matter API contract.

These shapes mirror `src/types/index.ts` field for field. That file calls
itself the single source of truth shared by the mock transport and this
backend, so the names here are its names: snake_case, no aliases, no
camelCase mapping layer. Changing anything here is a contract change and
must land in the TypeScript file in the same commit.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

SourceType = Literal["meeting", "document", "ticket", "message", "decision"]

EntityType = Literal["service", "system", "process", "component", "team"]

DecisionStatus = Literal[
    "Implemented", "Approved", "Proposed", "Superseded", "Rejected"
]

TicketStatus = Literal["Done", "In Progress", "To Do", "Blocked"]

ConflictSeverity = Literal["high", "medium", "low"]

RelationshipNodeType = Literal[
    "meeting", "document", "message", "decision", "ticket", "entity", "change"
]


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


class Source(BaseModel):
    id: str
    type: SourceType
    title: str
    date: str = Field(description="ISO-8601 date, YYYY-MM-DD.")
    snippet: str


class Entity(BaseModel):
    id: str
    type: EntityType
    name: str


class Ticket(BaseModel):
    id: str
    key: str = Field(description="Human-facing tracker key, e.g. PAY-101.")
    title: str
    status: TicketStatus


class DecisionSummary(BaseModel):
    id: str
    title: str
    date: str
    status: DecisionStatus


class Conflict(BaseModel):
    id: str
    entity: str
    existing_value: str
    proposed_value: str
    evidence: list[Source] = Field(
        description="Sources supporting both sides. Never empty — a conflict "
        "without evidence is not reportable."
    )
    severity: ConflictSeverity
    requires_review: bool


# ---------------------------------------------------------------------------
# Relationship path — the product's central structure
# ---------------------------------------------------------------------------


class RelationshipNode(BaseModel):
    id: str
    type: RelationshipNodeType
    label: str


class RelationshipEdge(BaseModel):
    from_: str = Field(
        alias="from", description="RelationshipNode.id of the source node."
    )
    to: str = Field(description="RelationshipNode.id of the target node.")
    label: str = Field(description="Edge verb, e.g. `resulted in`.")

    model_config = {"populate_by_name": True}


class RelationshipPath(BaseModel):
    nodes: list[RelationshipNode]
    edges: list[RelationshipEdge]


# ---------------------------------------------------------------------------
# Endpoint payloads
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """GET /health"""

    status: str
    sources: int
    entities: int
    relationships: int
    decisions: int
    conflicts: int


class AskRequest(BaseModel):
    """POST /ask"""

    question: str


class AskResponse(BaseModel):
    answer: str
    evidence: list[Source]
    path: RelationshipPath | None
    related_decisions: list[DecisionSummary]


class DecisionsResponse(BaseModel):
    """GET /decisions"""

    decisions: list[DecisionSummary]


class DecisionDetail(BaseModel):
    """GET /decisions/{id}"""

    id: str
    title: str
    date: str
    status: DecisionStatus
    rationale: str
    decided_by: str
    evidence: list[Source]
    path: RelationshipPath
    implemented_by: list[Ticket]
    affects: list[Entity]


class AnalyzeRequest(BaseModel):
    """POST /analyze"""

    change: str


class AnalyzeResponse(BaseModel):
    affected: list[Entity]
    related_decisions: list[DecisionSummary]
    related_tickets: list[Ticket]
    conflicts: list[Conflict]
    path: RelationshipPath


# ---------------------------------------------------------------------------
# Ingestion — no TypeScript counterpart yet; the Next.js app has no ingest
# surface. Consumed by the Streamlit console in backend/console.
# ---------------------------------------------------------------------------


class IngestTextRequest(BaseModel):
    text: str
    title: str = "Untitled source"
    source_type: SourceType = "document"
    date: str | None = None


class IngestResponse(BaseModel):
    ok: bool
    source_id: str
    title: str
    cognified: bool = Field(
        description="True when the text also reached the Cognee graph. False "
        "means it is in the relational store only."
    )
    detail: str
