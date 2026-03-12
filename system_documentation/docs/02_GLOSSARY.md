# 02 Glossary

Tags: glossary, definitions

- **Tenant**: a business entity in the platform (repair shop, leasing company, customer fleet).
- **CustomerAccount**: AR “payer” record under a tenant.
- **Asset**: physical item tracked for inspections/maintenance/spend.
- **Asset subtype**: structured type key (e.g., fleet.tractor.sleeper).
- **Capability**: typed properties/features an asset may have (e.g., time_metered, vin_decoded).
- **Field template**: reusable UI field set for asset creation/edit screens.
- **InspectionProgram**: schedule + template pack selection for a type of inspection.
- **InspectionRun**: an executed inspection instance (draft/finalized).
- **InspectionDefect**: a finding; can be OPEN/RESOLVED/DEFERRED.
- **Verification**: post-repair recheck required for safety-critical issues.
- **Proposal (WorkOrderLineProposal)**: staging object bridging defects to structured WO items.
- **WorkOrder**: operational job container (execution truth).
- **WorkOrderItem**: line item, structured as verb + noun + location with cost/price fields.
- **MaintenanceProgram**: PM scheduling rule.
- **MaintenanceDueInstance**: due/overdue instance for a specific asset/program.
- **AssetCostEvent**: append-only cost ledger event for asset spend.
- **InventoryLocation**: warehouse/bin/truck/etc.
- **InventoryTransaction**: append-only stock movement event.
- **Reservation**: allocates stock to a WO or POS ticket.
- **Special order**: part request tied to a WO and reserved on receipt.
- **Core charge/deposit**: refundable charge tied to rebuildable/reman parts; tracked as obligations.
- **QBO**: QuickBooks Online.
- **Outbox event**: queued integration event for idempotent sync.
