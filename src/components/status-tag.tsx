import { cn } from "@/lib/utils";
import type { DecisionStatus, TicketStatus } from "@/types";

/**
 * Status is metadata, so it is set in mono and carries no colour — colour in
 * this product means conflict, and a superseded decision is not a conflict.
 * Records no longer in force are struck through, which reads without colour.
 */

const NOT_IN_FORCE: DecisionStatus[] = ["Superseded", "Rejected"];

export function StatusTag({
  status,
  className,
}: {
  status: DecisionStatus;
  className?: string;
}) {
  const retired = NOT_IN_FORCE.includes(status);
  return (
    <span
      className={cn(
        "mono-label",
        retired ? "text-ink-faint line-through" : "text-ink-muted",
        className,
      )}
    >
      {status}
    </span>
  );
}

export function TicketStatusTag({
  status,
  className,
}: {
  status: TicketStatus;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "mono-label",
        status === "Done" ? "text-ink-faint" : "text-ink-muted",
        className,
      )}
    >
      {status}
    </span>
  );
}
