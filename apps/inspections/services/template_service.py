"""
Inspection Template Service

Service layer for loading, validating, caching, and managing inspection templates.
Handles the AF_INSPECTION_TEMPLATE format from asset_templates_v2_3.

Design Principles:
- Validation first: All templates validated with Pydantic before use
- Caching: Templates cached for performance (1 hour TTL)
- Immutable: Templates are read-only; changes require file updates
- Fail fast: Invalid templates rejected immediately with clear errors
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from django.conf import settings
from django.core.cache import cache
from pydantic import ValidationError as PydanticValidationError

from ..schemas.template_schema import (
    InspectionTemplate,
    TemplateSummary,
    ProcedureStep,
)


class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass


class TemplateNotFoundError(Exception):
    """Raised when template cannot be found."""
    pass


class TemplateService:
    """
    Service for loading and managing inspection templates.

    Templates are stored as JSON files in:
    apps/inspections/templates/inspection_templates/<standard>/<template>.json

    Caching Strategy:
    - Full templates cached for 1 hour
    - Template list cached for 1 hour
    - Cache invalidated on template file changes (dev mode)
    """

    # Template directory structure
    TEMPLATE_BASE_DIR = Path(settings.BASE_DIR) / 'apps' / 'inspections' / 'templates' / 'inspection_templates'

    # Cache configuration
    CACHE_PREFIX = 'inspection_template:'
    CACHE_LIST_KEY = 'inspection_template:list'
    CACHE_TIMEOUT = 3600  # 1 hour

    # Supported standards
    SUPPORTED_STANDARDS = {
        'ansi_a92_2_2021': 'ANSI/SAIA A92.2-2021'
    }

    # ========================================================================
    # Core Loading & Validation
    # ========================================================================

    @classmethod
    def load_template(cls, template_key: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load and validate a template by key.

        Args:
            template_key: Unique template identifier
            use_cache: Whether to use cached version (default: True)

        Returns:
            Dict representation of validated template

        Raises:
            TemplateNotFoundError: If template file doesn't exist
            TemplateValidationError: If template fails validation
        """
        # Check cache first
        if use_cache:
            cache_key = f"{cls.CACHE_PREFIX}{template_key}"
            cached = cache.get(cache_key)
            if cached:
                return cached

        # Find template file
        template_file = cls._find_template_file(template_key)
        if not template_file:
            raise TemplateNotFoundError(
                f"Template '{template_key}' not found in any supported standard directory"
            )

        # Load JSON
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
        except json.JSONDecodeError as e:
            raise TemplateValidationError(
                f"Template '{template_key}' contains invalid JSON: {str(e)}"
            )
        except Exception as e:
            raise TemplateValidationError(
                f"Failed to read template '{template_key}': {str(e)}"
            )

        # Validate with Pydantic
        try:
            validated_template = InspectionTemplate(**template_data)
        except PydanticValidationError as e:
            raise TemplateValidationError(
                f"Template '{template_key}' failed validation:\n{e}"
            )

        # Convert to dict for caching
        template_dict = validated_template.model_dump(by_alias=True)

        # Cache it
        if use_cache:
            cache_key = f"{cls.CACHE_PREFIX}{template_key}"
            cache.set(cache_key, template_dict, cls.CACHE_TIMEOUT)

        return template_dict

    @classmethod
    def get_template_object(cls, template_key: str, use_cache: bool = True) -> InspectionTemplate:
        """
        Load template as Pydantic object.

        Args:
            template_key: Unique template identifier
            use_cache: Whether to use cached version

        Returns:
            Validated InspectionTemplate object

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateValidationError: If validation fails
        """
        template_dict = cls.load_template(template_key, use_cache=use_cache)
        return InspectionTemplate(**template_dict)

    # ========================================================================
    # Template Discovery
    # ========================================================================

    @classmethod
    def list_all_templates(cls, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        List all available templates with metadata.

        Args:
            use_cache: Whether to use cached list

        Returns:
            List of template summaries sorted by name
        """
        # Check cache
        if use_cache:
            cached_list = cache.get(cls.CACHE_LIST_KEY)
            if cached_list:
                return cached_list

        templates = []

        # Scan all standard directories
        for standard_dir_name in cls.SUPPORTED_STANDARDS.keys():
            standard_dir = cls.TEMPLATE_BASE_DIR / standard_dir_name
            if not standard_dir.exists():
                continue

            # Load each template file
            for template_file in standard_dir.glob("*.json"):
                try:
                    template = cls.get_template_object(template_file.stem, use_cache=False)
                    summary = TemplateSummary.from_template(template)
                    templates.append(summary.model_dump())
                except (TemplateNotFoundError, TemplateValidationError):
                    # Skip invalid templates silently
                    continue

        # Sort by name
        templates.sort(key=lambda x: x['name'])

        # Cache the list
        if use_cache:
            cache.set(cls.CACHE_LIST_KEY, templates, cls.CACHE_TIMEOUT)

        return templates

    @classmethod
    def get_templates_by_standard(cls, standard_code: str) -> List[Dict[str, Any]]:
        """
        Get all templates for a specific standard.

        Args:
            standard_code: Standard code (e.g., 'ANSI/SAIA A92.2')

        Returns:
            List of templates matching the standard
        """
        all_templates = cls.list_all_templates()
        return [
            t for t in all_templates
            if t['standard_code'] == standard_code
        ]

    @classmethod
    def get_published_templates(cls) -> List[Dict[str, Any]]:
        """
        Get only published (production-ready) templates.

        Returns:
            List of templates with status=PUBLISHED
        """
        all_templates = cls.list_all_templates()
        return [t for t in all_templates if t['status'] == 'PUBLISHED']

    # ========================================================================
    # Equipment Applicability
    # ========================================================================

    @classmethod
    def get_applicable_templates(cls, equipment) -> List[Dict[str, Any]]:
        """
        Get templates applicable to specific equipment.

        Args:
            equipment: Equipment instance (from apps.assets.models.Equipment)

        Returns:
            List of applicable templates with readiness status

        Each template dict includes:
        - All standard template fields
        - ready: bool - whether equipment has required data
        - missing_data: list - what data is missing
        - missing_capabilities: list - what capabilities are missing
        """
        all_templates = cls.list_all_templates()
        applicable = []

        equipment_capabilities = getattr(equipment, 'capabilities', [])
        equipment_data = getattr(equipment, 'equipment_data', {})

        for template_summary in all_templates:
            template_key = template_summary['template_key']

            try:
                # Load full template to check applicability
                full_template = cls.get_template_object(template_key)

                # Check if template applies to this equipment
                if not cls._check_template_applicability(
                    full_template,
                    equipment_capabilities
                ):
                    continue

                # Check equipment data completeness
                missing_data = cls._check_missing_equipment_data(
                    full_template,
                    equipment_data
                )

                # Check capability requirements
                missing_capabilities = cls._check_missing_capabilities(
                    full_template,
                    equipment_capabilities
                )

                # Build applicability result
                applicable.append({
                    **template_summary,
                    'ready': len(missing_data) == 0 and len(missing_capabilities) == 0,
                    'missing_data': missing_data,
                    'missing_capabilities': missing_capabilities
                })

            except (TemplateNotFoundError, TemplateValidationError):
                continue

        return applicable

    @classmethod
    def _check_template_applicability(
        cls,
        template: InspectionTemplate,
        equipment_capabilities: List[str]
    ) -> bool:
        """
        Check if template applies to equipment based on capabilities.

        Args:
            template: Full template object
            equipment_capabilities: Equipment capabilities (includes domain and features)

        Returns:
            True if template applies, False otherwise
        """
        # If no applicability rules, assume applicable
        if not template.template.applicability:
            return True

        applicability = template.template.applicability

        # Check domain matches equipment capabilities
        # Domain (e.g., AERIAL_DEVICE) should be in capabilities
        domain = template.template.intent.domain
        if domain and domain not in equipment_capabilities:
            return False

        # Check required capabilities
        if applicability.required_capabilities:
            for required_cap in applicability.required_capabilities:
                if required_cap not in equipment_capabilities:
                    return False

        return True

    @classmethod
    def _check_missing_equipment_data(
        cls,
        template: InspectionTemplate,
        equipment_data: Dict[str, Any]
    ) -> List[str]:
        """
        Check what equipment data is missing for template.

        Args:
            template: Full template object
            equipment_data: Equipment's equipment_data JSON field

        Returns:
            List of missing data keys
        """
        missing = []

        # Check procedure inputs
        if template.procedure.inputs:
            for input_field in template.procedure.inputs:
                if input_field.required:
                    # Check if data exists in equipment_data
                    if input_field.input_id not in equipment_data:
                        missing.append(input_field.input_id)

        return missing

    @classmethod
    def _check_missing_capabilities(
        cls,
        template: InspectionTemplate,
        equipment_capabilities: List[str]
    ) -> List[str]:
        """
        Check what capabilities are missing for template.

        Args:
            template: Full template object
            equipment_capabilities: Equipment capabilities

        Returns:
            List of missing capability codes
        """
        missing = []

        if template.template.applicability and template.template.applicability.required_capabilities:
            for required_cap in template.template.applicability.required_capabilities:
                if required_cap not in equipment_capabilities:
                    missing.append(required_cap)

        return missing

    # ========================================================================
    # Template Content Access
    # ========================================================================

    @classmethod
    def get_template_step(
        cls,
        template_key: str,
        step_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific step from a template.

        Args:
            template_key: Template identifier
            step_key: Step identifier

        Returns:
            Step dict or None if not found
        """
        template = cls.get_template_object(template_key)
        step = template.get_step(step_key)
        return step.model_dump() if step else None

    @classmethod
    def get_required_steps(cls, template_key: str) -> List[Dict[str, Any]]:
        """
        Get all required steps for a template.

        Args:
            template_key: Template identifier

        Returns:
            List of required step dicts
        """
        template = cls.get_template_object(template_key)
        return [step.model_dump() for step in template.get_required_steps()]

    @classmethod
    def get_template_enums(cls, template_key: str) -> Dict[str, List[str]]:
        """
        Get all enum definitions for a template.

        Args:
            template_key: Template identifier

        Returns:
            Dict of enum name to list of values
        """
        template = cls.get_template_object(template_key)
        return template.enums

    @classmethod
    def get_enum_values(cls, template_key: str, enum_name: str) -> Optional[List[str]]:
        """
        Get values for a specific enum in a template.

        Args:
            template_key: Template identifier
            enum_name: Enum name

        Returns:
            List of enum values or None if not found
        """
        template = cls.get_template_object(template_key)
        return template.get_enum_values(enum_name)

    # ========================================================================
    # Cache Management
    # ========================================================================

    @classmethod
    def clear_cache(cls, template_key: Optional[str] = None):
        """
        Clear template cache.

        Args:
            template_key: If provided, clear only this template.
                         If None, clear all template caches.
        """
        if template_key:
            cache_key = f"{cls.CACHE_PREFIX}{template_key}"
            cache.delete(cache_key)
        else:
            # Clear all template caches
            cache.delete(cls.CACHE_LIST_KEY)
            # Note: Individual template caches will expire naturally

    @classmethod
    def reload_template(cls, template_key: str) -> Dict[str, Any]:
        """
        Force reload of a template from disk.

        Args:
            template_key: Template to reload

        Returns:
            Reloaded template dict
        """
        cls.clear_cache(template_key)
        return cls.load_template(template_key, use_cache=False)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    @classmethod
    def _find_template_file(cls, template_key: str) -> Optional[Path]:
        """
        Find template file by key across all standard directories.

        Searches for JSON files and checks the template_key inside each file.

        Args:
            template_key: Template identifier from template['template']['template_key']

        Returns:
            Path to template file or None if not found
        """
        for standard_dir_name in cls.SUPPORTED_STANDARDS.keys():
            standard_dir = cls.TEMPLATE_BASE_DIR / standard_dir_name
            if not standard_dir.exists():
                continue

            # First try direct filename match (fast path)
            template_file = standard_dir / f"{template_key}.json"
            if template_file.exists():
                return template_file

            # If not found, scan all JSON files and check template_key inside
            for json_file in standard_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('template', {}).get('template_key') == template_key:
                            return json_file
                except (json.JSONDecodeError, KeyError):
                    continue

        return None

    @classmethod
    def compute_template_hash(cls, template_key: str) -> str:
        """
        Compute SHA256 hash of template for integrity checking.

        Args:
            template_key: Template identifier

        Returns:
            Hex digest of template hash
        """
        template = cls.load_template(template_key, use_cache=False)

        # Convert to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(template, sort_keys=True, separators=(',', ':'))

        # Compute SHA256
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    @classmethod
    def validate_template_file(cls, template_file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate a template file without loading it into service.

        Args:
            template_file_path: Path to template file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            InspectionTemplate(**template_data)
            return (True, None)

        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON: {str(e)}")
        except PydanticValidationError as e:
            return (False, f"Validation failed: {str(e)}")
        except Exception as e:
            return (False, f"Unexpected error: {str(e)}")
