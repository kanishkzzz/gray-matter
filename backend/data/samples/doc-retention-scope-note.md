DEC-003 requires transaction records to be retained for seven years, but the Data Retention Policy does not define which store holds the record. Three candidates exist in the Payment Service: the event log, the settlement table, and the PostgreSQL transaction tables. This note assumes the obligation attaches to the event log, states that assumption so it can be overturned, and blocks PAY-133 on Legal review.

# Data Retention — Scope Note

Date: 2026-09-18
Author: S. Mistry, Finance Systems
Reviewed by: (pending — Legal)

## Purpose

To record what the seven-year retention obligation under DEC-003 actually
covers, because the Data Retention Policy states the period but not the scope,
and that ambiguity now blocks a decommissioning decision.

## What the policy says

Transaction records are retained for seven years from the date of settlement.
Deletion before that period requires written finance approval.

## What is unclear

"Transaction records" is not defined against the current Payment Service data
model. Since the event-driven rebuild under DEC-001 there are three candidate
stores:

1. The event log — append-only, the system of record since 2026.
2. The settlement table — written by the legacy batch job, proposed for
   deprecation under DEC-006.
3. The PostgreSQL transaction tables established under DEC-004.

If the obligation attaches to the event log alone, retiring the batch and
dropping the settlement table carries no retention risk. If it attaches to the
settlement table as well, the table must be archived before PAY-133 closes.

## Position taken

Pending Legal, this note assumes the obligation attaches to the event log,
because the event log is the system of record and the settlement table is
derived from it. A derived table is not independently a record.

This assumption is stated here so that it is visible and can be overturned,
rather than being made silently inside a migration ticket.

## Action

Legal review requested 2026-09-18. PAY-133 should not close before it returns.
