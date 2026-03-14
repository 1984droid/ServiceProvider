"""
Tests for Inspection Template Service

Comprehensive tests for template loading, validation, caching, and applicability.
"""

import pytest
import json
from pathlib import Path
from django.core.cache import cache
from apps.inspections.services.template_service import (
    TemplateService,
    TemplateNotFoundError,
    TemplateValidationError
)
from apps.assets.models import Equipment
from tests.factories import CustomerFactory, EquipmentFactory


@pytest.mark.django_db
class TestTemplateServiceLoading:
    """Test template loading and validation."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_load_dielectric_template(self):
        """Test loading the published dielectric template."""
        template = TemplateService.load_template('ansi_a92_2_periodic_dielectric')

        assert template is not None
        assert template['format'] == 'AF_INSPECTION_TEMPLATE'
        assert template['format_version'] == 1
        assert template['template']['template_key'] == 'ansi_a92_2_periodic_dielectric'
        assert template['template']['name'] == 'ANSI A92.2-2021 Periodic - Insulating Components & Dielectric Testing'
        assert template['template']['status'] == 'PUBLISHED'

    def test_load_hydraulic_system_template(self):
        """Test loading hydraulic system template."""
        template = TemplateService.load_template('ansi_a92_2_2021_hydraulic_system_module')

        assert template is not None
        assert template['template']['template_key'] == 'ansi_a92_2_2021_hydraulic_system_module'
        assert template['template']['status'] == 'DRAFT'
        assert len(template['procedure']['steps']) == 11

    def test_load_nonexistent_template_raises_error(self):
        """Test that loading nonexistent template raises TemplateNotFoundError."""
        with pytest.raises(TemplateNotFoundError):
            TemplateService.load_template('this_template_does_not_exist')

    def test_template_caching(self):
        """Test that templates are cached after first load."""
        # First load - should hit disk
        template1 = TemplateService.load_template('ansi_a92_2_periodic_dielectric')

        # Second load - should hit cache
        template2 = TemplateService.load_template('ansi_a92_2_periodic_dielectric')

        # Both should be identical
        assert template1 == template2

    def test_template_load_without_cache(self):
        """Test loading template bypassing cache."""
        template1 = TemplateService.load_template('ansi_a92_2_periodic_dielectric', use_cache=True)
        template2 = TemplateService.load_template('ansi_a92_2_periodic_dielectric', use_cache=False)

        # Should still be equal
        assert template1['template']['template_key'] == template2['template']['template_key']

    def test_get_template_object(self):
        """Test getting template as Pydantic object."""
        from apps.inspections.schemas.template_schema import InspectionTemplate

        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        assert isinstance(template, InspectionTemplate)
        assert template.template.template_key == 'ansi_a92_2_periodic_dielectric'
        assert template.format == 'AF_INSPECTION_TEMPLATE'


@pytest.mark.django_db
class TestTemplateServiceDiscovery:
    """Test template discovery and listing."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_list_all_templates(self):
        """Test listing all available templates."""
        templates = TemplateService.list_all_templates()

        assert len(templates) > 0
        assert len(templates) == 22  # 17 modular templates + 5 monolithic templates (frequent, periodic, load_test, dielectric, major_structural)

        # Check structure of each template summary
        for template in templates:
            assert 'template_key' in template
            assert 'name' in template
            assert 'status' in template
            assert 'standard_code' in template
            assert 'standard_revision' in template
            assert 'step_count' in template
            assert 'rule_count' in template

    def test_list_templates_sorted_by_name(self):
        """Test that templates are sorted by name."""
        templates = TemplateService.list_all_templates()

        names = [t['name'] for t in templates]
        assert names == sorted(names)

    def test_get_published_templates(self):
        """Test getting only published templates."""
        published = TemplateService.get_published_templates()

        assert len(published) >= 1  # At least dielectric is published
        for template in published:
            assert template['status'] == 'PUBLISHED'

    def test_get_templates_by_standard(self):
        """Test getting templates by standard code."""
        templates = TemplateService.get_templates_by_standard('ANSI/SAIA A92.2')

        assert len(templates) == 22  # All our templates are ANSI A92.2 (17 modular + 5 monolithic)
        for template in templates:
            assert template['standard_code'] == 'ANSI/SAIA A92.2'
            assert template['standard_revision'] == '2021'

    def test_get_templates_by_nonexistent_standard(self):
        """Test getting templates for standard with no templates."""
        templates = TemplateService.get_templates_by_standard('ASME B30.5')

        assert len(templates) == 0


@pytest.mark.django_db
class TestTemplateApplicability:
    """Test template applicability to equipment."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_get_applicable_templates_for_aerial_device(self):
        """Test getting applicable templates for aerial device equipment."""
        equipment = EquipmentFactory(
            equipment_type='A92_2_AERIAL',
            capabilities=['AERIAL_DEVICE'],
            equipment_data={}
        )

        applicable = TemplateService.get_applicable_templates(equipment)

        # Should have multiple applicable templates
        assert len(applicable) > 0

        # Check structure
        for template in applicable:
            assert 'template_key' in template
            assert 'ready' in template
            assert 'missing_data' in template
            assert 'missing_capabilities' in template

    def test_get_applicable_templates_for_insulated_boom(self):
        """Test templates for equipment with insulating system."""
        equipment = EquipmentFactory(
            equipment_type='A92_2_AERIAL',
            capabilities=['AERIAL_DEVICE', 'INSULATING_SYSTEM'],
            equipment_data={}
        )

        applicable = TemplateService.get_applicable_templates(equipment)

        # Dielectric template should be included
        template_keys = [t['template_key'] for t in applicable]
        assert 'ansi_a92_2_periodic_dielectric' in template_keys

    def test_template_readiness_missing_capabilities(self):
        """Test that template readiness detects missing capabilities."""
        # Equipment without INSULATING_SYSTEM capability
        equipment = EquipmentFactory(
            equipment_type='A92_2_AERIAL',
            capabilities=['AERIAL_DEVICE'],
            equipment_data={}
        )

        applicable = TemplateService.get_applicable_templates(equipment)

        # Find dielectric template
        dielectric = next(
            (t for t in applicable if t['template_key'] == 'ansi_a92_2_periodic_dielectric'),
            None
        )

        # Should not be applicable due to missing INSULATING_SYSTEM
        assert dielectric is None or not dielectric['ready']

    def test_template_readiness_with_all_requirements(self):
        """Test template readiness when all requirements met."""
        equipment = EquipmentFactory(
            equipment_type='A92_2_AERIAL',
            capabilities=['AERIAL_DEVICE', 'INSULATING_SYSTEM'],
            equipment_data={
                'placard': {
                    'rated_capacity': 500,
                    'max_working_height': 45
                }
            }
        )

        applicable = TemplateService.get_applicable_templates(equipment)

        # Find dielectric template
        dielectric = next(
            (t for t in applicable if t['template_key'] == 'ansi_a92_2_periodic_dielectric'),
            None
        )

        assert dielectric is not None
        # May still have missing data requirements - that's okay


@pytest.mark.django_db
class TestTemplateContentAccess:
    """Test accessing template content (steps, enums, etc.)."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_get_template_step(self):
        """Test getting a specific step from template."""
        step = TemplateService.get_template_step(
            'ansi_a92_2_periodic_dielectric',
            'dielectric_test_execute'
        )

        assert step is not None
        assert step['step_key'] == 'dielectric_test_execute'
        assert step['type'] == 'MEASUREMENT'
        assert step['required'] is True

    def test_get_nonexistent_step(self):
        """Test getting step that doesn't exist."""
        step = TemplateService.get_template_step(
            'ansi_a92_2_periodic_dielectric',
            'this_step_does_not_exist'
        )

        assert step is None

    def test_get_required_steps(self):
        """Test getting all required steps."""
        steps = TemplateService.get_required_steps('ansi_a92_2_periodic_dielectric')

        assert len(steps) > 0
        # All returned steps should be required
        for step in steps:
            assert step['required'] is True

    def test_get_template_enums(self):
        """Test getting all enum definitions."""
        enums = TemplateService.get_template_enums('ansi_a92_2_periodic_dielectric')

        assert 'severity' in enums
        assert 'step_status' in enums
        assert isinstance(enums['severity'], list)
        assert 'SAFE' in enums['severity']
        assert 'UNSAFE_OUT_OF_SERVICE' in enums['severity']

    def test_get_enum_values(self):
        """Test getting values for specific enum."""
        values = TemplateService.get_enum_values(
            'ansi_a92_2_periodic_dielectric',
            'severity'
        )

        assert values is not None
        assert isinstance(values, list)
        assert 'SAFE' in values
        assert 'MINOR' in values
        assert 'SERVICE_REQUIRED' in values
        assert 'UNSAFE_OUT_OF_SERVICE' in values

    def test_get_nonexistent_enum(self):
        """Test getting enum that doesn't exist."""
        values = TemplateService.get_enum_values(
            'ansi_a92_2_periodic_dielectric',
            'this_enum_does_not_exist'
        )

        assert values is None


@pytest.mark.django_db
class TestTemplateCacheManagement:
    """Test cache clearing and reloading."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_clear_specific_template_cache(self):
        """Test clearing cache for specific template."""
        # Load template (caches it)
        template1 = TemplateService.load_template('ansi_a92_2_periodic_dielectric')

        # Clear its cache
        TemplateService.clear_cache('ansi_a92_2_periodic_dielectric')

        # Load again (should re-read from disk)
        template2 = TemplateService.load_template('ansi_a92_2_periodic_dielectric')

        # Should still be equal
        assert template1['template']['template_key'] == template2['template']['template_key']

    def test_reload_template(self):
        """Test forcing reload of template."""
        template1 = TemplateService.load_template('ansi_a92_2_periodic_dielectric')
        template2 = TemplateService.reload_template('ansi_a92_2_periodic_dielectric')

        # Should be re-loaded
        assert template1['template']['template_key'] == template2['template']['template_key']


@pytest.mark.django_db
class TestTemplateUtilities:
    """Test utility functions."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_compute_template_hash(self):
        """Test computing template hash for integrity."""
        hash1 = TemplateService.compute_template_hash('ansi_a92_2_periodic_dielectric')

        assert hash1 is not None
        assert len(hash1) == 64  # SHA256 hex digest

        # Hash should be deterministic
        hash2 = TemplateService.compute_template_hash('ansi_a92_2_periodic_dielectric')
        assert hash1 == hash2

    def test_validate_template_file_valid(self):
        """Test validating a valid template file."""
        template_file = (
            Path(TemplateService.TEMPLATE_BASE_DIR) /
            'ansi_a92_2_2021' /
            'dielectric_module_a92_2_2021.json'
        )

        is_valid, error_msg = TemplateService.validate_template_file(template_file)

        assert is_valid is True
        assert error_msg is None

    def test_validate_template_file_invalid_json(self):
        """Test validating template with invalid JSON."""
        # Create a temporary invalid JSON file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json')
            temp_path = Path(f.name)

        try:
            is_valid, error_msg = TemplateService.validate_template_file(temp_path)

            assert is_valid is False
            assert 'Invalid JSON' in error_msg
        finally:
            temp_path.unlink()


@pytest.mark.django_db
class TestTemplatePydanticValidation:
    """Test Pydantic validation of templates."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_template_object_validation(self):
        """Test that template object validates correctly."""
        from apps.inspections.schemas.template_schema import InspectionTemplate

        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        # Check Pydantic model methods work
        assert template.count_steps() == 6
        assert template.count_rules() == 4

        # Check enum retrieval
        severity_values = template.get_enum_values('severity')
        assert severity_values is not None
        assert 'SAFE' in severity_values

        # Check step retrieval
        step = template.get_step('dielectric_test_execute')
        assert step is not None
        assert step.step_key == 'dielectric_test_execute'

    def test_template_required_steps(self):
        """Test getting required steps from template object."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        required = template.get_required_steps()
        assert len(required) > 0
        for step in required:
            assert step.required is True

    def test_template_blocking_steps(self):
        """Test getting blocking steps from template object."""
        template = TemplateService.get_template_object('ansi_a92_2_2021_hydraulic_system_module')

        blocking = template.get_blocking_steps()
        # At least one step should be blocking (preparation step)
        assert len(blocking) > 0


@pytest.mark.django_db
class TestTemplateStepCounts:
    """Test step counts across all templates."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_all_templates_have_steps(self):
        """Test that all templates have at least one step."""
        templates = TemplateService.list_all_templates()

        for template_summary in templates:
            assert template_summary['step_count'] > 0

    def test_dielectric_template_has_correct_step_count(self):
        """Test dielectric template has expected number of steps."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        assert template.count_steps() == 6

    def test_hydraulic_system_has_correct_step_count(self):
        """Test hydraulic system template has expected number of steps."""
        template = TemplateService.get_template_object('ansi_a92_2_2021_hydraulic_system_module')

        assert template.count_steps() == 11


@pytest.mark.django_db
class TestTemplateRules:
    """Test rule counts and structure."""

    def setup_method(self):
        """Clear cache before each test."""
        cache.clear()

    def test_dielectric_template_has_rules(self):
        """Test dielectric template has automated rules."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        assert template.count_rules() == 4
        assert template.rules is not None
        assert len(template.rules) == 4

    def test_rule_structure(self):
        """Test that rules have proper structure."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_dielectric')

        for rule in template.rules:
            assert rule.rule_id is not None
            assert rule.title is not None
            assert rule.on_fail is not None
            assert rule.on_fail.severity is not None
            assert rule.on_fail.defect_title is not None
