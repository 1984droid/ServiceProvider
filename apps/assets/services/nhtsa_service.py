"""
NHTSA VIN Decode Service

Handles VIN decoding via NHTSA vPIC API.
Simple decoder - returns structured data. View layer handles database storage.

API Documentation: https://vpic.nhtsa.dot.gov/api/
"""
import requests
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class NHTSAService:
    """Service for interacting with NHTSA vPIC API."""

    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

    def decode_vin(self, vin: str) -> Dict:
        """
        Decode VIN using NHTSA vPIC API.

        Args:
            vin: VIN to decode (17 characters)

        Returns:
            Dict with decoded VIN data

        Raises:
            ValueError: If VIN is invalid
            requests.HTTPError: If NHTSA API call fails
        """
        # Clean VIN
        clean_vin = vin.upper().strip()

        # Validate VIN length
        if len(clean_vin) != 17:
            raise ValueError(f"Invalid VIN length: {len(clean_vin)}. VIN must be exactly 17 characters.")

        # Validate VIN contains only alphanumeric (no I, O, Q)
        invalid_chars = set('IOQ')
        if not clean_vin.isalnum() or any(c in invalid_chars for c in clean_vin):
            raise ValueError("Invalid VIN format. VIN must be alphanumeric and cannot contain I, O, or Q.")

        # Fetch from NHTSA API
        raw_data = self._fetch_from_nhtsa(clean_vin)

        # Parse and structure the data
        decoded_data = self._parse_nhtsa_response(raw_data, clean_vin)

        return decoded_data

    def _fetch_from_nhtsa(self, vin: str) -> dict:
        """
        Fetch VIN decode data from NHTSA vPIC API.

        Args:
            vin: VIN to decode

        Returns:
            Raw NHTSA API response as dict

        Raises:
            requests.HTTPError: If API call fails
            ValueError: If VIN not found or API error
        """
        url = f"{self.BASE_URL}/DecodeVin/{vin}"
        params = {'format': 'json'}

        logger.info(f"Fetching VIN decode from NHTSA for {vin}")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check for NHTSA API errors
            if not data.get('Results'):
                raise ValueError("NHTSA API returned no results")

            return data

        except requests.Timeout:
            logger.error(f"NHTSA API timeout for VIN {vin}")
            raise requests.HTTPError("NHTSA API request timed out")
        except requests.RequestException as e:
            logger.error(f"NHTSA API error for VIN {vin}: {e}")
            raise

    def _parse_nhtsa_response(self, nhtsa_data: dict, vin: str) -> Dict:
        """
        Parse NHTSA vPIC response into structured dict.

        NHTSA returns array of {Variable, Value} objects.
        We extract key fields and organize into clean dict.

        Args:
            nhtsa_data: Raw NHTSA API response
            vin: The VIN that was decoded

        Returns:
            Structured dict with decoded VIN data
        """
        results = nhtsa_data.get('Results', [])

        # Create lookup dict from NHTSA results array
        data_dict = {item['Variable']: item['Value'] for item in results if item.get('Value')}

        def get_value(key: str):
            """Get value from data_dict, return None if empty or not found."""
            val = data_dict.get(key)
            if val in [None, '', 'Not Applicable', 'N/A']:
                return None
            return val

        # Extract error info
        error_codes = get_value('Error Code') or '0'
        error_text = get_value('Error Text') or ''

        # Determine if decode was successful
        decoded = error_codes == '0' or error_codes == '0,0,0'

        # Build structured response
        decoded_data = {
            'vin': vin,
            'decoded': decoded,

            # Core vehicle info
            'year': int(get_value('Model Year')) if get_value('Model Year') else None,
            'make': get_value('Make'),
            'model': get_value('Model'),
            'trim': get_value('Trim'),
            'series': get_value('Series'),
            'manufacturer': get_value('Manufacturer Name'),

            # Classification
            'vehicle_type': get_value('Vehicle Type'),
            'body_class': get_value('Body Class'),
            'body_type': get_value('Body Type'),
            'doors': get_value('Doors'),

            # Engine
            'engine_model': get_value('Engine Model'),
            'engine_configuration': get_value('Engine Configuration'),
            'engine_cylinders': int(get_value('Engine Number of Cylinders')) if get_value('Engine Number of Cylinders') else None,
            'displacement_liters': float(get_value('Displacement (L)')) if get_value('Displacement (L)') else None,
            'fuel_type_primary': get_value('Fuel Type - Primary'),
            'fuel_type_secondary': get_value('Fuel Type - Secondary'),
            'engine_brake_hp': get_value('Engine Brake (hp)'),

            # Transmission
            'transmission_style': get_value('Transmission Style'),
            'transmission_speeds': get_value('Transmission Speeds'),

            # Dimensions & capacity
            'gvwr': get_value('Gross Vehicle Weight Rating (GVWR)'),
            'gvwr_from': get_value('Gross Vehicle Weight Rating From'),
            'gvwr_to': get_value('Gross Vehicle Weight Rating To'),
            'curb_weight_pounds': get_value('Curb Weight (pounds)'),

            # Wheels & tires
            'drive_type': get_value('Drive Type'),
            'wheel_base_type': get_value('Wheel Base Type'),
            'wheel_base_inches': get_value('Wheelbase (inches)'),
            'tire_pressure_front': get_value('Tire Pressure Front (psi)'),
            'tire_pressure_rear': get_value('Tire Pressure Rear (psi)'),

            # Safety
            'abs': get_value('ABS'),
            'airbag_locations': get_value('Airbag Locations'),
            'esc': get_value('Electronic Stability Control (ESC)'),

            # Manufacturing
            'plant_city': get_value('Plant City'),
            'plant_state': get_value('Plant State'),
            'plant_country': get_value('Plant Country'),

            # Additional
            'cab_type': get_value('Cab Type'),
            'trailer_type': get_value('Trailer Type Connection'),
            'trailer_body_type': get_value('Trailer Body Type'),
            'bed_length_inches': get_value('Bed Length (inches)'),

            # Metadata
            'suggested_vin': get_value('Suggested VIN'),
            'error_code': error_codes,
            'error_text': error_text,

            # Store complete raw response
            'raw_nhtsa_data': nhtsa_data,
        }

        # Remove None values to keep response clean
        decoded_data = {k: v for k, v in decoded_data.items() if v is not None}

        return decoded_data
