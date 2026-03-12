# 10 Key End-to-End Flows

Tags: flows, diagrams, lifecycle

This section summarizes the most important “gold standard” flows.

## Flow A — Inspection → Repair → Verification → Compliance → Invoice
1) InspectionRun finalized
2) Defects created (including severity UNSAFE)
3) Generate WorkOrderLineProposals
4) Bulk-promote proposals → WorkOrder
5) Issue parts from inventory locations (truck/warehouse)
6) Complete WorkOrder
7) UNSAFE defects become verification REQUIRED
8) Recheck InspectionRun performed and PASSED
9) Compliance snapshot becomes COMPLIANT
10) Generate Invoice draft from WorkOrder, issue invoice
11) Record Payment, sync to QBO

See diagrams/flow_inspection_to_invoice.mmd

## Flow B — Purchasing → Receiving → Vendor Bill → Stock + AP
1) Reorder suggestion or special order request
2) Create PurchaseOrder and send to Vendor
3) ReceivingReceipt records physical arrival (partial allowed)
4) InventoryTransaction(RECEIVE) increases stock in receiving location
5) VendorBill records invoice number and unit cost
6) Sync VendorBill to QBO

See diagrams/flow_purchasing_to_ap.mmd

## Flow C — Special Order Part tied to Work Order
1) Work order requests a special order part
2) Convert request into PO line (linked to WO)
3) Receive into Special Order Staging
4) Reservation created for WO
5) Issue part to WO; cannot be used by other jobs
6) WO completion triggers invoicing & cost ledger emission

See diagrams/flow_special_order.mmd

## Flow D — Core deposit (customer) + vendor credit
1) Sell reman part and charge core deposit (invoice line)
2) Core obligation created for customer
3) Customer returns core → record return
4) CreditMemo issued, obligation cleared
5) Vendor core obligation created on purchase (if applicable)
6) Vendor receives core return → VendorCredit issued → obligation cleared

See diagrams/flow_cores.mmd
