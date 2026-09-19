The settlement batch review on 17 September 2026 recommended retiring the legacy settlement batch job rather than porting it to PostgreSQL. The job is the last component still reading from the MySQL replica, and it blocks decommissioning under PAY-133. Finance confirmed it does not depend on the batch output. Recorded as DEC-006, pending sign-off.

# Settlement Batch Review

Date: 2026-09-17
Attending: R. Okonjo (Payments), L. Haverford (Reliability), S. Mistry (Finance Systems)

## Context

The legacy settlement batch job runs nightly at 02:15 UTC against the Payment
Service and has not been materially changed since the event log rebuild. With
the PostgreSQL migration under DEC-004 now complete on the write path, the
batch is the last component still reading from the MySQL replica.

## Discussion

L. Haverford walked through the failure history: eleven late completions in the
last quarter, all of them on days where the transaction volume exceeded 1.4M.
The job holds a table-level lock for the duration of the settlement window,
which is what pushes the monitoring alerts into a degraded state.

S. Mistry confirmed Finance does not depend on the batch output directly. The
reconciliation report is generated from the event log, not from the batch
table, and has been since March.

R. Okonjo proposed retiring the job entirely rather than porting it to
PostgreSQL. Porting was estimated at three weeks; retirement is roughly four
days of work plus a verification window.

## Outcome

Agreed to recommend deprecation. This is recorded as DEC-006 and remains in
proposed status pending sign-off from the Payments lead. PAY-133 should not be
closed until the batch is retired, because decommissioning the MySQL cluster
while the batch still reads from it would take settlement offline.

Transaction Monitoring will need an alerting rule change once the batch is
gone, tracked under OPS-077.
