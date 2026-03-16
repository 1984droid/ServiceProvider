# VIN Decode Implementation

## Overview
VIN decode functionality is fully implemented using NHTSA vPIC API. The system caches decode results in the `VINDecodeData` model for fast lookups, similar to how USDOT/MC# lookup works with `USDOTProfile`.

## Architecture

### Backend

**Service Layer:** `apps/assets/services/nhtsa_service.py`
- `NHTSAService` class handles communication with NHTSA vPIC API
- Validates VIN format (17 characters, alphanumeric, no I/O/Q)
- Parses 50+ vehicle data fields from NHTSA response
- Returns structured dict with decoded data

**Data Model:** `apps/assets/models.py`
- `VINDecodeData` model stores decode results
- OneToOne relationship with `Vehicle` (optional - can exist standalone)
- Captures: year, make, model, manufacturer, engine specs, dimensions, safety features, etc.
- Stores raw NHTSA response in `raw_response` JSONField

**API Endpoints:** `apps/assets/views.py` - `VINDecodeDataViewSet`
- `POST /api/vin-decode-data/decode_vin/` - Decode VIN via NHTSA API
  - Body: `{"vin": "17-char-vin", "vehicle_id": "uuid-optional"}`
  - Creates/updates VINDecodeData record
  - Returns: Full decode data with 50+ fields
- `GET /api/vin-decode-data/lookup_by_vin/?vin=XXX` - Lookup cached decode
  - Returns: VINDecodeData from database if exists
  - Returns: 404 if not found

### Frontend

**API Client:** `frontend/src/api/vin.api.ts`
- `vinApi.decode(vin)` - Decode VIN (calls NHTSA API)
- `vinApi.lookupByVIN(vin)` - Check cache for existing decode

**UI Component:** `frontend/src/features/assets/VINSearch.tsx`
- Search form with VIN input validation
- Auto-checks cache first before calling NHTSA API
- Displays error messages for invalid VINs
- Callback with decode data on success

## Workflow

1. **User enters VIN** in VINSearch component
2. **Check cache first:** `GET /api/vin-decode-data/lookup_by_vin/?vin=XXX`
   - If found: Return cached data (instant)
   - If not found: Continue to step 3
3. **Decode via NHTSA:** `POST /api/vin-decode-data/decode_vin/`
   - NHTSAService calls NHTSA vPIC API
   - Parses response into structured data
   - Saves to VINDecodeData model
   - Returns decode data
4. **User sees results** and can choose to:
   - Create Vehicle from this data, OR
   - Just save the decode for reference (no Vehicle created)

## Data Independence

VINDecodeData records exist **independently** of Vehicle records:
- Decode VIN → Save to VINDecodeData → User decides whether to create Vehicle
- Similar pattern to USDOTProfile / Customer relationship
- Cached lookups persist even if Vehicle is deleted
- Multiple Vehicles can reference same decoded VIN data (though typically 1:1)

## Key Features

✅ Real NHTSA vPIC API integration
✅ VIN validation (17 chars, no I/O/Q)
✅ 50+ vehicle data fields extracted
✅ Database caching for fast repeat lookups
✅ Standalone decode records (not tied to Vehicle creation)
✅ Error handling for API failures
✅ Frontend cache-first strategy

## Testing

All backend tests pass (424/424):
- VIN validation tests
- API integration tests
- Model tests for VINDecodeData
- Serializer tests

## Example Response

```json
{
  "id": "uuid",
  "vin": "1HGBH41JXMN109186",
  "model_year": 1991,
  "make": "HONDA",
  "model": "ACCORD",
  "manufacturer": "HONDA",
  "vehicle_type": "PASSENGER CAR",
  "body_class": "SEDAN/SALOON",
  "engine_model": "D15B7",
  "engine_cylinders": 4,
  "displacement_liters": "1.5",
  "fuel_type_primary": "GASOLINE",
  "gvwr": "Class 1C: 4,001 - 5,000 lb",
  "plant_city": "SUZUKA",
  "plant_country": "JAPAN",
  "error_code": "0",
  "decoded_at": "2026-03-16T10:30:00Z",
  "raw_response": { ... }
}
```

## Dependencies

- `requests>=2.31.0` - HTTP library for NHTSA API calls
- `responses>=0.24.0` - Test dependency for mocking HTTP requests
