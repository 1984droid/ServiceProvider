# 00 Overview

This seed dataset creates a small but realistic network:
- Repair shop tenant
- Leasing company tenant
- Customer fleet tenant

It includes:
- assets (vehicle + aerial device)
- meters (odometer/hours)
- maintenance programs + due instances
- inspection program keys (ANSI A92.2-2021 style) for workflow testing
- defects including UNSAFE defect requiring verification (recheck)
- work order proposals and a sample work order
- parts catalog with noun classification
- multi-location inventory (warehouse, bin, service truck, special order staging)
- purchasing documents: vendor, PO, receiving receipt, vendor bill
- financial documents: invoice, payment, credit memo
- core charge sample (reman alternator core deposit)
- leasing sharing contract + recurring billing schedule

The goal is *not* to be exhaustive; the goal is to be **high-leverage** and cover the workflows that break most often.
