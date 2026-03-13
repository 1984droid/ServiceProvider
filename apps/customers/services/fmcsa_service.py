"""
FMCSA API Service

Handles lookups to the FMCSA Safer Web Service API.
Caches results in USDOTProfile model with timestamps.
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from apps.customers.models import USDOTProfile

logger = logging.getLogger(__name__)


class FMCSAService:
    """Service for interacting with FMCSA Safer Web API."""

    BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services/carriers"

    def __init__(self):
        self.webkey = settings.FMCSA_WEBKEY
        if not self.webkey:
            raise ValueError("FMCSA_WEBKEY not configured in settings")

    def lookup_by_usdot(self, usdot_number: str, force_refresh: bool = False) -> USDOTProfile:
        """
        Lookup carrier by USDOT number.

        Args:
            usdot_number: USDOT number to lookup
            force_refresh: If True, fetch from FMCSA even if cached

        Returns:
            USDOTProfile instance (from cache or newly created)

        Raises:
            ValueError: If USDOT number is invalid
            requests.HTTPError: If FMCSA API call fails
        """
        # Clean USDOT number
        clean_usdot = ''.join(c for c in usdot_number if c.isalnum())

        if not clean_usdot:
            raise ValueError("Invalid USDOT number")

        # Check cache first (unless force refresh)
        if not force_refresh:
            try:
                profile = USDOTProfile.objects.get(usdot_number=clean_usdot)
                logger.info(f"Found cached USDOT profile for {clean_usdot}")
                return profile
            except USDOTProfile.DoesNotExist:
                logger.info(f"No cached profile found for {clean_usdot}, fetching from FMCSA")

        # Fetch from FMCSA API
        data = self._fetch_from_fmcsa(clean_usdot, lookup_type='USDOT')

        # Create or update profile
        profile = self._save_profile(data, clean_usdot)

        return profile

    def lookup_by_mc(self, mc_number: str, force_refresh: bool = False) -> USDOTProfile:
        """
        Lookup carrier by MC number.

        Args:
            mc_number: MC number to lookup
            force_refresh: If True, fetch from FMCSA even if cached

        Returns:
            USDOTProfile instance (from cache or newly created)

        Raises:
            ValueError: If MC number is invalid
            requests.HTTPError: If FMCSA API call fails
        """
        # Clean MC number
        clean_mc = ''.join(c for c in mc_number if c.isalnum())

        if not clean_mc:
            raise ValueError("Invalid MC number")

        # Check cache first (unless force refresh)
        if not force_refresh:
            try:
                profile = USDOTProfile.objects.get(mc_number=clean_mc)
                logger.info(f"Found cached USDOT profile for MC {clean_mc}")
                return profile
            except USDOTProfile.DoesNotExist:
                logger.info(f"No cached profile found for MC {clean_mc}, fetching from FMCSA")

        # Fetch from FMCSA API
        data = self._fetch_from_fmcsa(clean_mc, lookup_type='MC_MX')

        # Create or update profile
        usdot_number = data.get('content', {}).get('carrier', {}).get('dotNumber', '')
        profile = self._save_profile(data, usdot_number)

        return profile

    def _fetch_from_fmcsa(self, identifier: str, lookup_type: str = 'USDOT') -> dict:
        """
        Fetch data from FMCSA API.

        Args:
            identifier: USDOT or MC number
            lookup_type: 'USDOT' or 'MC_MX'

        Returns:
            Raw FMCSA API response as dict

        Raises:
            requests.HTTPError: If API call fails
            ValueError: If carrier not found
        """
        url = f"{self.BASE_URL}/{identifier}"
        params = {
            'webKey': self.webkey
        }

        logger.info(f"Fetching {lookup_type} {identifier} from FMCSA API")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Log the raw response for debugging
            logger.debug(f"FMCSA API response: {data}")

            # Check if data is None or empty
            if not data:
                raise ValueError(f"Empty response from FMCSA API for {lookup_type} {identifier}")

            # Check if content is null (carrier not found)
            if not isinstance(data, dict) or data.get('content') is None:
                raise ValueError(f"Carrier not found for {lookup_type} {identifier}")

            # Check if carrier exists in content
            if 'carrier' not in data.get('content', {}):
                raise ValueError(f"Carrier not found for {lookup_type} {identifier}")

            logger.info(f"Successfully fetched {lookup_type} {identifier} from FMCSA")

            # Fetch docket numbers to get MC number
            try:
                docket_url = f"{self.BASE_URL}/{identifier}/docket-numbers"
                docket_response = requests.get(docket_url, params=params, timeout=10)
                docket_response.raise_for_status()
                docket_data = docket_response.json()

                # Add docket numbers to the main data
                data['docket_numbers'] = docket_data.get('content', [])
                logger.debug(f"Fetched docket numbers: {data['docket_numbers']}")
            except Exception as e:
                logger.warning(f"Failed to fetch docket numbers for {identifier}: {str(e)}")
                data['docket_numbers'] = []

            return data

        except requests.RequestException as e:
            logger.error(f"FMCSA API request failed for {lookup_type} {identifier}: {str(e)}")
            raise

    def _save_profile(self, fmcsa_data: dict, usdot_number: str) -> USDOTProfile:
        """
        Save or update USDOT profile from FMCSA data.

        Args:
            fmcsa_data: Raw FMCSA API response
            usdot_number: USDOT number (primary identifier)

        Returns:
            USDOTProfile instance
        """
        carrier = fmcsa_data.get('content', {}).get('carrier', {})
        docket_numbers = fmcsa_data.get('docket_numbers', [])

        # Extract MC number from docket numbers
        mc_number = ''
        for docket in docket_numbers:
            if docket.get('prefix') == 'MC':
                mc_number = str(docket.get('docketNumber', ''))
                break

        # Extract all relevant fields (convert None to empty string for CharField fields)
        profile_data = {
            'usdot_number': str(carrier.get('dotNumber', usdot_number)),
            'mc_number': mc_number,
            'legal_name': carrier.get('legalName') or '',
            'dba_name': carrier.get('dbaName') or '',
            'entity_type': carrier.get('entityType') or '',

            # Physical address
            'physical_address': carrier.get('phyStreet') or '',
            'physical_city': carrier.get('phyCity') or '',
            'physical_state': carrier.get('phyState') or '',
            'physical_zip': carrier.get('phyZipcode') or '',

            # Mailing address
            'mailing_address': carrier.get('maiStreet') or '',
            'mailing_city': carrier.get('maiCity') or '',
            'mailing_state': carrier.get('maiState') or '',
            'mailing_zip': carrier.get('maiZipcode') or '',

            # Contact
            'phone': carrier.get('telephone') or '',
            'email': carrier.get('emailAddress') or '',

            # Operational data - extract description from nested object
            'carrier_operation': (
                carrier.get('carrierOperation', {}).get('carrierOperationDesc')
                if isinstance(carrier.get('carrierOperation'), dict)
                else carrier.get('carrierOperation') or ''
            ),
            'cargo_carried': carrier.get('cargoCarried') or '',
            'operation_classification': carrier.get('operatingStatus') or [],

            # Safety data
            'safety_rating': carrier.get('safetyRating') or '',
            'out_of_service_date': carrier.get('oosDate', None),
            'total_power_units': carrier.get('totalPowerUnits', None),
            'total_drivers': carrier.get('totalDrivers', None),

            # Store complete raw response with timestamp
            'raw_fmcsa_data': fmcsa_data,
            'lookup_date': timezone.now(),
        }

        # Create or update profile (use USDOT as unique identifier)
        profile, created = USDOTProfile.objects.update_or_create(
            usdot_number=profile_data['usdot_number'],
            defaults=profile_data
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} USDOT profile for {profile.usdot_number}")

        return profile
