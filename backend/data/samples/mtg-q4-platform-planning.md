Q4 platform planning on 19 September 2026 covered four threads: the database migration is complete on the write path but blocked on DEC-006; transaction monitoring work under OPS-077 has not started despite DEC-005 being approved; the authentication token lifetime review needs a security sign-off; and read-replica lag policy remains undecided.

# Q4 Platform Planning

Date: 2026-09-19
Attending: R. Okonjo, P. Adeyemi, L. Haverford, D. Whitlock (Engineering Director)

## Carried over from Q3

The database migration is functionally complete on the write path. What
remains is decommissioning, which is blocked on the settlement batch under
DEC-006. D. Whitlock asked for a date; R. Okonjo would not give one until the
decision is signed off, on the grounds that PAY-133 has already slipped twice
on optimistic estimates.

## Transaction Monitoring

DEC-005 is approved but OPS-077 has not started. The duplicate settlement
incident in August is the concrete case for prioritising it: monitoring covered
the event log and missed a two-and-a-half hour fault in the settlement table
entirely. L. Haverford will scope the coverage gap this sprint.

## Authentication

P. Adeyemi raised the token lifetime review. D. Whitlock's position was that
any change to DEC-002 needs the security review in the room, not as a comment
thread, and that jitter does not need that bar because it changes no security
property.

## Database Architecture

Discussion of whether to formalise a read-replica policy. Currently each team
decides its own lag tolerance, which is what made the August incident possible.
No decision taken; P. Adeyemi to draft a proposal for the next review.

## Not discussed

Retention. DEC-003 stands. S. Mistry's question about whether batch-populated
rows fall under the same seven-year obligation was raised in #payments and has
not been answered by anyone with the authority to answer it.
