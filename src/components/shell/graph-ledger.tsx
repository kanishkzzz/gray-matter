import type { HealthResponse } from "@/types";
import { cn } from "@/lib/utils";

/**
 * Corpus ledger — what the graph currently holds.
 *
 * Sits at the foot of the nav rail and is visible on every screen. It is the
 * product's standing provenance statement: before you read an answer, you can
 * see what it was drawn from.
 *
 * Presentational only. The route fetches; this takes props.
 */

interface GraphLedgerProps {
  health: HealthResponse | null;
}

export function GraphLedger({ health }: GraphLedgerProps) {
  if (!health) {
    return (
      <div>
        <p className="mono-label text-ink-faint">Knowledge graph</p>
        <p className="mono-meta mt-2 text-ink-muted">Not reachable</p>
      </div>
    );
  }

  return (
    <div>
      <p className="mono-label text-ink-faint">Knowledge graph</p>
      <dl className="mt-2 flex flex-col gap-1">
        <LedgerRow label="sources" value={health.sources} />
        <LedgerRow label="entities" value={health.entities} />
        <LedgerRow label="relationships" value={health.relationships} />
        <LedgerRow label="decisions" value={health.decisions} />
        <LedgerRow
          label={health.conflicts === 1 ? "open conflict" : "open conflicts"}
          value={health.conflicts}
          /* The one place warning is permitted outside a conflict surface:
             this count *is* the conflict count. */
          flagged={health.conflicts > 0}
        />
      </dl>
    </div>
  );
}

function LedgerRow({
  label,
  value,
  flagged = false,
}: {
  label: string;
  value: number;
  flagged?: boolean;
}) {
  return (
    <div className="mono-meta flex items-baseline justify-between gap-2">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={cn("text-ink", flagged && "text-warning")}>{value}</dd>
    </div>
  );
}
