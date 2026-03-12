# 02 Data Catalog (What's created)

## Tenants
- demo_repair_shop (repair company)
- demo_leasing_co (leasing company)
- demo_customer_fleet (fleet customer)

## Assets
- Tractor (vehicle) with meters: odometer_miles, engine_hours
- Trailer
- Aerial device (ANSI A92.2 inspection target) with hours meter

## Inventory locations
- Main Warehouse
- Counter Stock Bin
- Service Truck 12
- Special Order Staging

## Parts
- Brake Pad (stocked)
- Hydraulic Hose (stocked)
- Reman Alternator (rebuildable, core charge)
- Core Deposit Item (non-stocked “financial” line if you choose)
- Dielectric Gloves (consumable)

## Vendors and purchasing
- Vendor: Fleet Supplier Co
- PO with a special-order line linked to the sample work order
- Receipt (partial allowed) + vendor bill with invoice number

## Financial docs
- One invoice generated from a work order
- One payment allocated
- One credit memo (core return)

## Leasing
- SharingContract that allows leasing to see summary compliance
- RecurringBillingSchedule for monthly lease payment
