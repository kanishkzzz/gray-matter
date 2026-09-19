import { cn } from "@/lib/utils";
import type { HealthResponse } from "@/types";

/**
 * Knowledge health.
 *
 * A ruled ledger band, not a grid of stat cards: one continuous strip divided
 * by hairlines, so it reads as a single statement about the corpus rather than
 * five floating tiles. The figures are set in mono because they are counts
 * drawn straight from the graph.
 *
 * The conflict count is the only figure permitted colour, and only when it is
 * non-zero — it is the one thing here that asks for action.
 */
export function KnowledgeHealth({ health }: { health: HealthResponse }) {
  const figures = [
    { label: "Sources", value: health.sources },
    { label: "Entities", value: health.entities },
    { label: "Relationships", value: health.relationships },
    { label: "Decisions", value: health.decisions },
    {
      label: health.conflicts === 1 ? "Open conflict" : "Open conflicts",
      value: health.conflicts,
      flagged: health.conflicts > 0,
    },
  ];

  return (
    <dl className="flex flex-wrap border-y border-rule">
      {figures.map((figure, index) => (
        <div
          key={figure.label}
          className={cn(
            "min-w-35 flex-1 px-4 py-3",
            index > 0 && "border-l border-rule",
          )}
        >
          <dt className="mono-label text-ink-faint">{figure.label}</dt>
          <dd
            className={cn(
              "mt-1 font-mono text-24 tabular-nums",
              figure.flagged ? "text-warning" : "text-ink",
            )}
          >
            {figure.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}
