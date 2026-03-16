"""
Inspection Template Filtering Service

Filters available inspection templates based on asset characteristics:
- Asset type (Vehicle vs Equipment)
- Equipment type (standards-based: A92_2_AERIAL, B30_5_CRANE, etc.)
- Vehicle body type (SERVICE, FLATBED, DUMP, etc.)
- Capabilities (INSULATING_SYSTEM, BARE_HAND_WORK_UNIT, etc.)

Design Principles:
- Standards-driven: Templates are aligned with ANSI/ASME/OSHA standards
- Asset-aware: Only show templates applicable to the specific asset
- Capability-based: Filter based on required capabilities (e.g., dielectric test only for insulated units)
"""

from typing import List, Dict, Any, Optional
from .template_service import TemplateService


class TemplateFilterService:
    """
    Service for filtering inspection templates based on asset characteristics.

    Usage:
        # Get applicable templates for a vehicle
        templates = TemplateFilterService.get_applicable_templates_for_vehicle(vehicle)

        # Get applicable templates for equipment
        templates = TemplateFilterService.get_applicable_templates_for_equipment(equipment)
    """

    # ========================================================================
    # Equipment Type to Domain Mapping
    # ========================================================================

    # Maps equipment_type values to template domain values
    EQUIPMENT_TYPE_TO_DOMAIN = {
        # ANSI A92 Series - All map to AERIAL_DEVICE domain
        'A92_2_AERIAL': 'AERIAL_DEVICE',
        'A92_20_SCISSOR': 'AERIAL_DEVICE',
        'A92_20_BOOM': 'AERIAL_DEVICE',
        'A92_3_VERTICAL': 'AERIAL_DEVICE',

        # ANSI/ASME B30 Series - Crane domains
        'B30_5_CRANE': 'CRANE',
        'B30_22_ARTICULATING': 'CRANE',

        # Other equipment
        'DIGGER_DERRICK': 'DIGGER_DERRICK',
        'FORKLIFT': 'FORKLIFT',
        'GENERATOR': 'GENERATOR',
        'COMPRESSOR': 'COMPRESSOR',
        'WELDER': 'WELDER',
        'CRANE_BOOM_TRUCK': 'CRANE',
    }

    # Maps equipment_type to specific standard codes for filtering
    EQUIPMENT_TYPE_TO_STANDARDS = {
        'A92_2_AERIAL': ['ANSI/SAIA A92.2'],
        'A92_20_SCISSOR': ['ANSI/SAIA A92.20'],
        'A92_20_BOOM': ['ANSI/SAIA A92.20'],
        'A92_3_VERTICAL': ['ANSI/SAIA A92.3'],
        'B30_5_CRANE': ['ANSI/ASME B30.5'],
        'B30_22_ARTICULATING': ['ANSI/ASME B30.22'],
    }

    # ========================================================================
    # Public API
    # ========================================================================

    @classmethod
    def get_applicable_templates_for_vehicle(cls, vehicle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get inspection templates applicable to a vehicle.

        Args:
            vehicle: Vehicle dict with keys: id, body_type, capabilities, etc.

        Returns:
            List of applicable template dicts

        Examples:
            >>> vehicle = {'id': '123', 'body_type': 'SERVICE', 'capabilities': []}
            >>> templates = TemplateFilterService.get_applicable_templates_for_vehicle(vehicle)
            [
                {'template_key': 'dot_annual_inspection', 'name': 'DOT Annual Inspection'},
                {'template_key': 'service_body_inspection', 'name': 'Service Body Inspection'}
            ]
        """
        all_templates = TemplateService.list_all_templates()
        applicable = []

        for template_summary in all_templates:
            # Load full template to check applicability rules
            template = TemplateService.load_template(template_summary['template_key'])

            # Check if template applies to vehicles
            if not cls._applies_to_asset_type(template, 'VEHICLE'):
                continue

            # Check body type requirements (if any)
            if not cls._matches_body_type(template, vehicle.get('body_type', '')):
                continue

            # Check capability requirements
            if not cls._has_required_capabilities(template, vehicle.get('capabilities', [])):
                continue

            applicable.append(template_summary)

        return applicable

    @classmethod
    def get_applicable_templates_for_equipment(cls, equipment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get inspection templates applicable to equipment.

        Args:
            equipment: Equipment dict with keys: id, equipment_type, capabilities, etc.

        Returns:
            List of applicable template dicts

        Examples:
            >>> equipment = {
            ...     'id': '456',
            ...     'equipment_type': 'A92_2_AERIAL',
            ...     'capabilities': ['INSULATING_SYSTEM', 'BARE_HAND_WORK_UNIT']
            ... }
            >>> templates = TemplateFilterService.get_applicable_templates_for_equipment(equipment)
            [
                {'template_key': 'ansi_a92_2_periodic_base', 'name': 'ANSI A92.2 Periodic Inspection'},
                {'template_key': 'ansi_a92_2_periodic_dielectric', 'name': 'ANSI A92.2 Dielectric Test'}
            ]
        """
        all_templates = TemplateService.list_all_templates()
        applicable = []

        equipment_type = equipment.get('equipment_type', '')
        equipment_capabilities = equipment.get('capabilities', [])

        for template_summary in all_templates:
            # Load full template to check applicability rules
            template = TemplateService.load_template(template_summary['template_key'])

            # Check if template applies to equipment
            if not cls._applies_to_asset_type(template, 'EQUIPMENT'):
                continue

            # Check equipment type / domain match
            if not cls._matches_equipment_type(template, equipment_type):
                continue

            # Check capability requirements
            if not cls._has_required_capabilities(template, equipment_capabilities):
                continue

            applicable.append(template_summary)

        return applicable

    # ========================================================================
    # Private Filtering Logic
    # ========================================================================

    @classmethod
    def _applies_to_asset_type(cls, template: Dict[str, Any], asset_type: str) -> bool:
        """
        Check if template applies to the given asset type (VEHICLE or EQUIPMENT).

        Args:
            template: Full template dict
            asset_type: 'VEHICLE' or 'EQUIPMENT'

        Returns:
            True if template applies to this asset type
        """
        applicability = template.get('template', {}).get('applicability')

        # If no applicability rules specified, assume it applies to all
        if not applicability:
            return True

        asset_types = applicability.get('asset_types', [])

        # If no asset_types specified, assume it applies to all
        if not asset_types:
            return True

        return asset_type in asset_types

    @classmethod
    def _matches_equipment_type(cls, template: Dict[str, Any], equipment_type: str) -> bool:
        """
        Check if template matches the equipment type based on domain and standards.

        Args:
            template: Full template dict
            equipment_type: Equipment type code (e.g., 'A92_2_AERIAL', 'B30_5_CRANE')

        Returns:
            True if template applies to this equipment type
        """
        if not equipment_type:
            # No equipment type specified - only show generic templates
            return False

        # Get template domain
        template_domain = template.get('template', {}).get('intent', {}).get('domain', '')

        # Get expected domain for this equipment type
        expected_domain = cls.EQUIPMENT_TYPE_TO_DOMAIN.get(equipment_type)

        if not expected_domain:
            # Unknown equipment type - don't show any templates
            return False

        # Check if domains match
        if template_domain != expected_domain:
            return False

        # Additional check: If equipment type has specific standard requirements, verify template standard
        expected_standards = cls.EQUIPMENT_TYPE_TO_STANDARDS.get(equipment_type, [])
        if expected_standards:
            template_standard = template.get('template', {}).get('standard', {}).get('code', '')
            # Check if template standard matches any expected standard
            if not any(std in template_standard for std in expected_standards):
                return False

        return True

    @classmethod
    def _matches_body_type(cls, template: Dict[str, Any], body_type: str) -> bool:
        """
        Check if template matches vehicle body type requirements.

        Args:
            template: Full template dict
            body_type: Vehicle body type (e.g., 'SERVICE', 'FLATBED', 'DUMP')

        Returns:
            True if template applies to this body type
        """
        # All vehicle templates apply to all body types
        return True

    @classmethod
    def _has_required_capabilities(cls, template: Dict[str, Any], asset_capabilities: List[str]) -> bool:
        """
        Check if asset has all required capabilities for this template.

        Args:
            template: Full template dict
            asset_capabilities: List of capability strings from asset

        Returns:
            True if asset has all required capabilities

        Examples:
            >>> template = {
            ...     'template': {
            ...         'applicability': {
            ...             'required_capabilities': ['INSULATING_SYSTEM']
            ...         }
            ...     }
            ... }
            >>> cls._has_required_capabilities(template, ['INSULATING_SYSTEM', 'BARE_HAND_WORK_UNIT'])
            True
            >>> cls._has_required_capabilities(template, ['BARE_HAND_WORK_UNIT'])
            False
        """
        applicability = template.get('template', {}).get('applicability')

        # If no applicability rules, template applies to all
        if not applicability:
            return True

        required_capabilities = applicability.get('required_capabilities', [])

        # If no required capabilities, template applies to all
        if not required_capabilities:
            return True

        # Check if asset has ALL required capabilities
        return all(cap in asset_capabilities for cap in required_capabilities)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @classmethod
    def get_domain_for_equipment_type(cls, equipment_type: str) -> Optional[str]:
        """
        Get the template domain for a given equipment type.

        Args:
            equipment_type: Equipment type code (e.g., 'A92_2_AERIAL')

        Returns:
            Domain string (e.g., 'AERIAL_DEVICE') or None if unknown
        """
        return cls.EQUIPMENT_TYPE_TO_DOMAIN.get(equipment_type)

    @classmethod
    def get_standards_for_equipment_type(cls, equipment_type: str) -> List[str]:
        """
        Get the applicable standards for a given equipment type.

        Args:
            equipment_type: Equipment type code (e.g., 'A92_2_AERIAL')

        Returns:
            List of standard codes (e.g., ['ANSI/SAIA A92.2'])
        """
        return cls.EQUIPMENT_TYPE_TO_STANDARDS.get(equipment_type, [])
