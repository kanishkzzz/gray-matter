On 14 August 2026 the Payment Service wrote 3,812 duplicate settlement entries over two and a half hours. No customer funds moved twice. The cause was the settlement batch job reading a lagging MySQL replica after the write path had cut over to PostgreSQL. Transaction Monitoring did not alert, because its duplicate-transaction rule covers the event log and not the settlement table. Finance found it nine days later.

# Incident Report: Duplicate Settlement Entries

Incident ID: INC-2026-0814
Severity: 2
Date: 2026-08-14
Author: L. Haverford, Reliability

## Summary

Between 02:15 and 04:40 UTC on 14 August 2026, the Payment Service wrote 3,812
duplicate settlement entries. No customer funds moved twice; the duplicates
were confined to the settlement table and were not reflected in the event log.

## Cause

During the dual-write window established under PAY-118, the settlement batch
job read from the MySQL replica while the write path had already cut over to
PostgreSQL. Replication lag on the replica exceeded the batch's assumed
tolerance of 60 seconds, so rows already settled were re-read and re-written.

The dual-write design assumed the batch would be retired before the migration
reached this stage. It was not, and no check enforced that ordering.

## Detection

Transaction Monitoring did not alert. The duplicate-transaction rule described
in the Transaction Monitoring Specification covers the event log only, and the
settlement table is outside its scope. The issue was found by Finance during
month-end reconciliation, nine days later.

## Remediation

Duplicates were removed by a one-off reconciliation script on 16 August.
Replication lag tolerance was raised to 600 seconds as an interim measure.

## Follow-up

1. Extend monitoring coverage to the settlement table (OPS-077).
2. Retire the settlement batch job before closing PAY-133.
3. Record the batch-before-cutover ordering constraint in the migration plan,
   which currently does not state it.

This incident is the strongest argument for DEC-006 and should be cited in the
decision record.
