# 09 Maintenance

Tags: maintenance, scheduling, due_instances, meters, pm

## MaintenanceProgram
Defines interval rules:
- time-based (days/months)
- meter-based (miles/hours)
- both (whichever comes first)

## MaintenanceDueInstance
Concrete “due” row for:
- (asset, maintenance_program)

States:
- SCHEDULED
- DUE
- OVERDUE
- DONE
- SKIPPED (optional)

## Due computations
- computed from last completion date + meter reading at completion
- requires access to AssetMeter current values

## PM completion integration (hybrid)
On work order completion for a PM work order:
- if program is meter-based and meter_reading_at_service missing → do NOT mark DONE
- otherwise mark DONE and record completion metadata

## Post-PM inspections (optional)
Some programs require proof:
- requires_post_pm_inspection flag
- post_pm_inspection_program_key
Completing PM creates a draft/scheduled recheck inspection.

## References
- packages/asset_templates_v2_3_field_mapping_package.zip (maintenance_programs.json)
- packages/work_orders_gold_standard_package_v1.zip (maintenance due integration)
