"use client";

import * as React from "react";
import Link from "next/link";

import { EvidencePanel } from "@/components/evidence-panel";
import { RelationshipPathView } from "@/components/relationship-path";
import { PageFrame, Section } from "@/components/shell/page-frame";
import { StatusTag, TicketStatusTag } from "@/components/status-tag";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { formatDate, pluralise } from "@/lib/format";
import type { DecisionDetail } from "@/types";

/**
 * Decision Trace — why this decision exists, what evidence supports it, what
 * implements it and what it affects.
 *
 * The relationship path leads, because the relationship is the product. Prose
 * comes after the structure, not before it.
 *
 * Selection is shared between the path and the evidence rail: choosing a node
 * opens its source, and choosing a source marks its node.
 */
export function DecisionTrace({ decision }: { decision: DecisionDetail }) {
  const [selectedId, setSelectedId] = React.useState<string | null>(
    decision.evidence[0]?.id ?? null,
  );
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const evidenceIds = React.useMemo(
    () => new Set(decision.evidence.map((s) => s.id)),
    [decision.evidence],
  );

  /** A node the user picked that has no source excerpt behind it. */
  const unsourced =
    selectedId && !evidenceIds.has(selectedId)
      ? decision.path.nodes.find((n) => n.id === selectedId)
      : undefined;

  const panel = (
    <EvidencePanel
      eyebrow={decision.id}
      sources={decision.evidence}
      selectedId={selectedId}
      onSelect={(source) => setSelectedId(source.id)}
      emptyMessage={`No indexed source supports ${decision.id}.`}
    />
  );

  return (
    <PageFrame
      eyebrow={
        <span className="flex items-center gap-1.5">
          <Link
            href="/decisions"
            className="text-ink-muted hover:text-accent hover:underline hover:underline-offset-2"
          >
            All decisions
          </Link>
          <span aria-hidden="true" className="text-ink-faint">
            /
          </span>
          <span>{decision.id}</span>
        </span>
      }
      title={decision.title}
      meta={
        <span className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
          <StatusTag status={decision.status} />
          <Sep />
          <span>recorded {formatDate(decision.date)}</span>
          <Sep />
          <span>{decision.decided_by}</span>
          <Sep />
          <span>
            derived from {pluralise(decision.evidence.length, "source")}
          </span>
        </span>
      }
      actions={
        <Button
          variant="outline"
          className="xl:hidden"
          onClick={() => setDrawerOpen(true)}
        >
          Evidence ({decision.evidence.length})
        </Button>
      }
      rail={panel}
    >
      <Section
        title="Trace"
        description="Left is what came before; right is what it led to. Select a node to open its source."
      >
        <RelationshipPathView
          path={decision.path}
          selectedId={selectedId}
          onSelectNode={(node) => {
            setSelectedId(node.id);
            // Below 1280px the rail is not on screen, so surface it.
            if (window.matchMedia("(max-width: 1279px)").matches) {
              setDrawerOpen(true);
            }
          }}
        />

        {unsourced ? (
          <p className="mt-3 border-l-2 border-rule-strong pl-3 text-13 text-ink-muted">
            <span className="mono-label text-ink-faint">{unsourced.id}</span> is
            a {unsourced.type}. No source excerpt is recorded for it.
          </p>
        ) : null}
      </Section>

      <Section title="Rationale">
        <p className="max-w-[68ch] text-15 text-ink">{decision.rationale}</p>
      </Section>

      <Section
        title="Implemented by"
        description={
          decision.implemented_by.length === 0
            ? undefined
            : "Work recorded against this decision."
        }
      >
        {decision.implemented_by.length === 0 ? (
          <p className="text-13 text-ink-muted">
            No implementing work is recorded against {decision.id}.
          </p>
        ) : (
          <ul className="border-y border-rule">
            {decision.implemented_by.map((ticket) => (
              <li
                key={ticket.id}
                className="flex items-baseline justify-between gap-4 border-b border-rule py-2 last:border-b-0"
              >
                <span className="flex min-w-0 items-baseline gap-3">
                  <span className="mono-meta shrink-0 text-ink-muted">
                    {ticket.key}
                  </span>
                  <span className="truncate text-13 text-ink">
                    {ticket.title}
                  </span>
                </span>
                <TicketStatusTag status={ticket.status} />
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section
        title="Affects"
        description="Entities that change if this decision changes."
      >
        {decision.affects.length === 0 ? (
          <p className="text-13 text-ink-muted">
            No affected entities are recorded.
          </p>
        ) : (
          <ul className="border-y border-rule">
            {decision.affects.map((entity) => (
              <li
                key={entity.id}
                className="flex items-baseline justify-between gap-4 border-b border-rule py-2 last:border-b-0"
              >
                <span className="flex min-w-0 items-baseline gap-3">
                  <span className="mono-meta shrink-0 text-ink-muted">
                    {entity.id}
                  </span>
                  <span className="truncate text-13 text-ink">
                    {entity.name}
                  </span>
                </span>
                <span className="mono-label text-ink-faint">{entity.type}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      {/* Below 1280px the rail collapses into this drawer. */}
      <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
        <DrawerContent className="xl:hidden" showCloseButton={false}>
          <DrawerHeader className="sr-only">
            <DrawerTitle>Evidence for {decision.id}</DrawerTitle>
            <DrawerDescription>
              Sources supporting {decision.title}
            </DrawerDescription>
          </DrawerHeader>
          <DrawerBody>{panel}</DrawerBody>
        </DrawerContent>
      </Drawer>
    </PageFrame>
  );
}

function Sep() {
  return (
    <span aria-hidden="true" className="text-ink-faint">
      ·
    </span>
  );
}
