import Link from "next/link";

import { StatusTag } from "@/components/status-tag";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDateIso } from "@/lib/format";
import type { DecisionSummary } from "@/types";

/**
 * The decision register. Presentational — the route fetches.
 *
 * The whole row is the target, but there is only one tab stop per row: the
 * title link is stretched over the row with a pseudo-element.
 */
export function DecisionRegister({
  decisions,
}: {
  decisions: DecisionSummary[];
}) {
  if (decisions.length === 0) {
    return (
      <p className="text-13 text-ink-muted">
        No decisions are recorded in this corpus.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-24">ID</TableHead>
          <TableHead>Decision</TableHead>
          <TableHead className="w-28">Date</TableHead>
          <TableHead className="w-32">Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {decisions.map((decision) => (
          <TableRow key={decision.id} className="relative">
            <TableCell className="mono-meta text-ink-muted">
              {decision.id}
            </TableCell>
            <TableCell>
              <Link
                href={`/decisions/${decision.id}`}
                className="text-ink after:absolute after:inset-0 hover:text-accent hover:underline hover:underline-offset-2"
              >
                {decision.title}
              </Link>
            </TableCell>
            <TableCell className="mono-meta text-ink-muted">
              {formatDateIso(decision.date)}
            </TableCell>
            <TableCell>
              <StatusTag status={decision.status} />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
