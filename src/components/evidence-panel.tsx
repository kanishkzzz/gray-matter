"use client";

import { cn } from "@/lib/utils";
import { formatDateIso } from "@/lib/format";
import type { Source, SourceType } from "@/types";

/**
 * Evidence panel — the right rail.
 *
 * Provenance is the product, so a source is never summarised away: every entry
 * shows what kind of record it is, its id, its date and its own words. Nothing
 * here is generated text.
 */

const SOURCE_LABEL: Record<SourceType, string> = {
  meeting: "Meeting",
  document: "Document",
  ticket: "Ticket",
  message: "Message",
  decision: "Decision",
};

interface EvidencePanelProps {
  /** Mono kicker above the heading, e.g. `DEC-004`. */
  eyebrow?: string;
  title?: string;
  sources: Source[];
  selectedId?: string | null;
  onSelect?: (source: Source) => void;
  /** Shown when `sources` is empty. States coverage rather than just "none". */
  emptyMessage?: string;
  className?: string;
}

export function EvidencePanel({
  eyebrow,
  title = "Evidence",
  sources,
  selectedId,
  onSelect,
  emptyMessage = "No indexed source supports this record.",
  className,
}: EvidencePanelProps) {
  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div className="shrink-0 border-b border-rule px-4 py-3">
        {eyebrow ? (
          <p className="mono-label text-ink-faint">{eyebrow}</p>
        ) : null}
        <div className="flex items-baseline justify-between gap-2">
          <h2 className="font-display text-18 text-ink">{title}</h2>
          <span className="mono-meta text-ink-muted">
            {sources.length === 1 ? "1 source" : `${sources.length} sources`}
          </span>
        </div>
      </div>

      {sources.length === 0 ? (
        <div className="px-4 py-4">
          <p className="text-13 text-ink-muted">{emptyMessage}</p>
        </div>
      ) : (
        <ul className="min-h-0 flex-1 overflow-y-auto">
          {sources.map((source) => (
            <li key={source.id} className="border-b border-rule last:border-b-0">
              <SourceEntry
                source={source}
                selected={source.id === selectedId}
                onSelect={onSelect}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */

export function SourceEntry({
  source,
  selected = false,
  onSelect,
}: {
  source: Source;
  selected?: boolean;
  onSelect?: (source: Source) => void;
}) {
  const interactive = Boolean(onSelect);

  const content = (
    <>
      <p className="mono-label text-ink-faint">
        {SOURCE_LABEL[source.type]} · {source.id} · {formatDateIso(source.date)}
      </p>
      <p className="mt-1 text-13 font-medium text-ink">{source.title}</p>
      <p className="mt-1.5 text-13 text-ink-muted">{source.snippet}</p>
    </>
  );

  if (!interactive) {
    return (
      <div
        className={cn(
          "border-l-2 px-4 py-3",
          selected ? "border-accent bg-accent-soft" : "border-transparent",
        )}
      >
        {content}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onSelect?.(source)}
      aria-pressed={selected}
      className={cn(
        "block w-full border-l-2 px-4 py-3 text-left transition-colors duration-100",
        selected
          ? "border-accent bg-accent-soft"
          : "border-transparent hover:bg-tint-hover",
      )}
    >
      {content}
    </button>
  );
}
