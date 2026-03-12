# 18 Operations Runbook

Tags: operations, runbook, monitoring

## Core monitoring signals
- outbox event backlog and failure rate (QBO sync)
- compliance snapshot job success rate
- inventory adjustment volume (possible shrink or process issues)
- negative inventory exceptions
- unsafe defects pending verification count

## Common “breakers”
- token refresh failures (QBO)
- duplicate sync attempts without idempotency keys
- mis-scoped tenant_root leading to cross-tenant errors
- schedule computations without consistent timezone/time-freezing in tests

## Recommended ops dashboards
- QBO connection status by tenant
- outbox failures by entity type
- inventory stockouts and reorder suggestions
- core obligations aging report
