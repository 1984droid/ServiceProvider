# 01 System Overview

Tags: system, architecture, multi-tenant, safety, finance

## What this platform is
A multi-tenant operations platform for:
- a heavy-duty repair business (work orders, inspections, maintenance, parts)
- a leasing business (asset ownership + billing + compliance oversight)
- customer fleets (assets, compliance, maintenance history, spend visibility)

The system is designed to be:
- **structured** (minimal free text)
- **auditable** (append-only ledgers and immutable finalized records)
- **integratable** (QuickBooks Online for accounting, Samsara for telematics/meter readings)

## Core idea: one asset, multiple stakeholders
One physical asset can involve multiple tenants:
- Leasing company: owns the asset and wants maintenance/compliance visibility
- Customer: operates the asset (may be a fleet) and needs uptime and accurate billing
- Repair shop: performs inspections/repairs and needs structured operations and parts control

To make this safe:
- cross-tenant visibility is explicitly gated (SharingContract)
- “proof” is recorded via inspections, evidence, and verification loops

## The operational backbone
**Inspection → Defect → Proposal → Work Order → (Repair) → Verification → Compliance**

That is the safety spine of the system.

## The financial backbone
**Work Orders and POS produce billable lines → Invoices → Payments → QBO sync**

The system supports:
- repair shop billing (service + parts + labor)
- POS/front counter sales
- leasing recurring billing
- inventory purchasing (vendors, bills, credits)
- core deposits and credits

## Key posture decisions
1) **Operational truth** lives in this platform.
2) **Accounting truth** lives in QuickBooks Online.
3) **Safety truth** lives in inspections + evidence + verification.
