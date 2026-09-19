The Authentication Service issues OAuth 2.1 tokens with a 15-minute lifetime under DEC-002. Three services now report refresh storms, the Payment Service worst of all. This review compares extending the lifetime, client-side jitter and a caching proxy, and recommends jitter on the grounds that reopening DEC-002 for a load problem trades a security property for convenience.

# Authentication Token Lifetime Review

Date: 2026-09-05
Owner: P. Adeyemi, Platform
Status: Draft for comment

## Background

The Authentication Service issues OAuth 2.1 client credentials tokens with a
15-minute lifetime, established under DEC-002 and implemented in AUTH-204. The
previous model of static credentials issued from the platform vault was retired
at the same time and is recorded as superseded under DEC-007.

## Problem

Three services now report token refresh storms under load. The Payment Service
is the worst affected: at peak it holds roughly 900 concurrent workers, each
refreshing independently, which produces a synchronised burst against the auth
endpoint every fifteen minutes.

## Options considered

**Extend token lifetime to 60 minutes.** Reduces refresh volume fourfold. The
security review objects: a 60-minute window materially widens the exposure if a
token leaks, and the 15-minute figure was chosen deliberately in DEC-002 rather
than by default.

**Client-side jitter.** Spread refresh across the window. No change to the
security posture. Requires a change in every client library, but the change is
small and backwards-compatible.

**Token caching proxy.** A sidecar holds one token per host rather than per
worker. Strongest reduction, largest operational surface.

## Recommendation

Client-side jitter, with a proxy revisited if the auth endpoint remains hot.
Explicitly not proposing a lifetime change: reopening DEC-002 for a load
problem that has a cheaper fix would trade a security property for convenience.

## Open question

Nobody has confirmed whether the 15-minute figure is a compliance requirement
or an engineering choice. The decision record does not say. If it is the
former, the first option is not available at all and this document should say
so plainly rather than listing it.
