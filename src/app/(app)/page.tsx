import Link from "next/link";

import { api } from "@/api";
import { PageFrame, Section } from "@/components/shell/page-frame";
import { DecisionRegister } from "@/features/decisions/decision-register";
import { KnowledgeHealth } from "@/features/overview/knowledge-health";
import { pluralise } from "@/lib/format";
import type { DecisionSummary, HealthResponse } from "@/types";

const RECENT_COUNT = 5;

export default async function OverviewPage() {
  const [healthResult, decisionsResult] = await Promise.allSettled([
    api.health(),
    api.listDecisions(),
  ]);

  const health: HealthResponse | null =
    healthResult.status === "fulfilled" ? healthResult.value : null;
  const decisions: DecisionSummary[] =
    decisionsResult.status === "fulfilled"
      ? decisionsResult.value.decisions
      : [];

  const recent = decisions.slice(0, RECENT_COUNT);
  const conflicts = health?.conflicts ?? 0;

  return (
    <PageFrame
      eyebrow="NovaPay"
      title="Overview"
      lede="What the knowledge graph currently holds, what changed most recently, and what is waiting on review."
      meta={
        health
          ? `${pluralise(health.sources, "source")} · ${pluralise(health.relationships, "relationship")} · indexed across 12 systems`
          : "Knowledge graph not reachable"
      }
    >
      <Section
        title="Knowledge health"
        description="Composition of the corpus these answers are drawn from."
      >
        {health ? (
          <KnowledgeHealth health={health} />
        ) : (
          <p className="text-13 text-ink-muted">
            The knowledge graph could not be reached, so its composition cannot
            be reported.
          </p>
        )}
      </Section>

      <Section title="Requires review">
        {conflicts === 0 ? (
          <p className="text-13 text-ink-muted">
            No potential conflicts are recorded in the knowledge graph.
          </p>
        ) : (
          <div className="border-l-2 border-warning bg-warning-soft px-4 py-3">
            <p className="mono-label text-warning">
              Potential conflict detected
            </p>
            <p className="mt-1.5 max-w-[68ch] text-13 text-ink">
              {pluralise(conflicts, "potential conflict")} recorded in the
              knowledge graph{" "}
              {conflicts === 1 ? "is" : "are"} awaiting review. Evidence
              indicates existing records disagree with a proposed change.
            </p>
            <Link
              href="/truth-engine"
              className="mt-2 inline-block text-13 text-accent underline underline-offset-2"
            >
              Review in Truth Engine
            </Link>
          </div>
        )}
      </Section>

      <Section
        title="Recent decisions"
        actions={
          decisions.length > RECENT_COUNT ? (
            <Link
              href="/decisions"
              className="text-13 text-accent hover:underline hover:underline-offset-2"
            >
              All {decisions.length} decisions
            </Link>
          ) : undefined
        }
      >
        <DecisionRegister decisions={recent} />
      </Section>
    </PageFrame>
  );
}
