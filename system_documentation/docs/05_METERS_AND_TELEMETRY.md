# 05 Meters and Telematics

Tags: meters, odometer, engine_hours, samsara, maintenance

## Meter storage (critical)
Do NOT store current meter readings in Asset.capabilities.

Use a dedicated model:
- AssetMeter (current value per meter_type)
Optional:
- AssetMeterReading (history)

Meter types (start):
- odometer_miles
- engine_hours
- reefer_hours
- pto_hours

## Sources
- manual entry (service writer / inspector)
- work order completion meter_at_service
- telematics (Samsara) — periodic updates

## Maintenance dependency
MaintenanceDueInstance computations depend on meters.
Work order completion should only mark PM “DONE” when:
- required meter reading is present (hybrid policy).

## Samsara integration posture
Samsara is a meter source, not a “system of record”.
- Your platform remains the truth for due status and compliance.

Recommended ingestion:
- scheduled pull or webhook → update AssetMeter.current_value with source='telematics'
