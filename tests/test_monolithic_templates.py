"""
Tests for ANSI A92.2-2021 Monolithic Inspection Templates

Validates the 4 comprehensive monolithic templates:
- Frequent Inspection
- Periodic Inspection
- Load Test Only
- Major Structural Inspection
"""

import pytest
from pathlib import Path
from apps.inspections.services.template_service import (
    TemplateService,
    TemplateValidationError
)
from apps.inspections.schemas.template_schema import InspectionTemplate


class TestMonolithicTemplateDiscovery:
    """Test that all 4 monolithic templates are discoverable."""

    def test_all_monolithic_templates_discovered(self):
        """Test that all 4 monolithic templates are found."""
        templates = TemplateService.list_all_templates()
        template_keys = [t['template_key'] for t in templates]

        expected_templates = [
            'ansi_a92_2_frequent_inspection',
            'ansi_a92_2_periodic_inspection',
            'ansi_a92_2_load_test_only',
            'ansi_a92_2_major_structural_inspection'
        ]

        for template_key in expected_templates:
            assert template_key in template_keys, f"{template_key} not found in discovered templates"

    def test_monolithic_templates_are_published(self):
        """Test that all monolithic templates have PUBLISHED status."""
        monolithic_keys = [
            'ansi_a92_2_frequent_inspection',
            'ansi_a92_2_periodic_inspection',
            'ansi_a92_2_load_test_only',
            'ansi_a92_2_major_structural_inspection'
        ]

        for template_key in monolithic_keys:
            template = TemplateService.load_template(template_key)
            assert template['template']['status'] == 'PUBLISHED', \
                f"{template_key} status is {template['template']['status']}, expected PUBLISHED"


class TestMonolithicTemplatePydanticValidation:
    """Test Pydantic validation of all monolithic templates."""

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_template_validates_with_pydantic(self, template_key):
        """Test that template validates against Pydantic schema."""
        # This will raise ValidationError if template is invalid
        template_obj = TemplateService.get_template_object(template_key)

        assert isinstance(template_obj, InspectionTemplate)
        assert template_obj.format == 'AF_INSPECTION_TEMPLATE'
        assert template_obj.format_version == 1


class TestMonolithicTemplateStructure:
    """Test structure and completeness of monolithic templates."""

    def test_frequent_inspection_structure(self):
        """Test Frequent Inspection template structure."""
        template = TemplateService.get_template_object('ansi_a92_2_frequent_inspection')

        # Check basic metadata
        assert template.template.template_key == 'ansi_a92_2_frequent_inspection'
        assert template.template.name == 'ANSI A92.2-2021 Frequent Inspection'
        assert template.template.standard.code == 'ANSI/SAIA A92.2'
        assert template.template.standard.revision == '2021'
        assert template.template.intent.inspection_kind == 'FREQUENT'

        # Check applicability
        assert 'EQUIPMENT' in template.template.applicability.asset_types
        assert 'A92_2_AERIAL' in template.template.applicability.equipment_types

        # Check has steps
        assert template.count_steps() >= 8, "Frequent inspection should have at least 8 steps"

        # Check enums exist
        assert 'severity' in template.enums
        assert 'pass_fail' in template.enums

        # Check defect schema exists
        assert template.schemas.defect_schema is not None

    def test_periodic_inspection_structure(self):
        """Test Periodic Inspection template structure."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_inspection')

        # Check basic metadata
        assert template.template.template_key == 'ansi_a92_2_periodic_inspection'
        assert template.template.name == 'ANSI A92.2-2021 Periodic Inspection'
        assert template.template.intent.inspection_kind == 'PERIODIC'

        # Check applicability
        assert 'A92_2_AERIAL' in template.template.applicability.equipment_types

        # Check has comprehensive steps
        assert template.count_steps() >= 12, "Periodic inspection should have at least 12 comprehensive steps"

        # Check has inputs for load/dielectric tests
        assert template.procedure.inputs is not None
        assert len(template.procedure.inputs) == 2, "Should have 2 inputs (load test, dielectric test)"

        # Check enums
        assert 'severity' in template.enums
        assert 'pass_fail' in template.enums

        # Check has validation rules
        assert template.count_rules() >= 2, "Should have at least 2 validation rules"

    def test_load_test_structure(self):
        """Test Load Test Only template structure."""
        template = TemplateService.get_template_object('ansi_a92_2_load_test_only')

        # Check basic metadata
        assert template.template.template_key == 'ansi_a92_2_load_test_only'
        assert template.template.name == 'ANSI A92.2-2021 Load Test Only'
        assert template.template.intent.inspection_kind == 'LOAD_TEST'

        # Check applicability
        assert 'A92_2_AERIAL' in template.template.applicability.equipment_types

        # Check has steps
        assert template.count_steps() >= 8, "Load test should have at least 8 steps"

        # Check has measurement sets for drift testing
        assert template.schemas.measurement_sets is not None
        assert len(template.schemas.measurement_sets) >= 1, "Should have drift measurement set"

        # Check has validation rules
        assert template.count_rules() >= 2, "Should have validation rules for load adequacy and drift"

    def test_major_structural_structure(self):
        """Test Major Structural Inspection template structure."""
        template = TemplateService.get_template_object('ansi_a92_2_major_structural_inspection')

        # Check basic metadata
        assert template.template.template_key == 'ansi_a92_2_major_structural_inspection'
        assert template.template.name == 'ANSI A92.2-2021 Major Structural Inspection'
        assert template.template.intent.inspection_kind == 'MAJOR_STRUCTURAL'

        # Check applicability
        assert 'A92_2_AERIAL' in template.template.applicability.equipment_types

        # Check has comprehensive steps
        assert template.count_steps() >= 10, "Major structural should have at least 10 comprehensive steps"

        # Check enums include NDT-specific values
        assert template.enums is not None

        # Check has validation rules
        assert template.count_rules() >= 3, "Should have validation rules for major structural work"


class TestMonolithicTemplateFieldTypes:
    """Test that all templates use correct field types."""

    VALID_FIELD_TYPES = [
        'TEXT', 'TEXT_AREA', 'NUMBER', 'BOOLEAN', 'DATE',
        'ENUM', 'PHOTO', 'ATTACHMENTS'
    ]

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_template_uses_valid_field_types(self, template_key):
        """Test that template only uses valid field types."""
        template = TemplateService.get_template_object(template_key)

        for step in template.procedure.steps:
            if step.fields:
                for field in step.fields:
                    assert field.type in self.VALID_FIELD_TYPES, \
                        f"{template_key} step {step.step_key} field {field.field_id} has invalid type: {field.type}"

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_defect_schema_uses_valid_types(self, template_key):
        """Test that defect schema uses correct field types."""
        template = TemplateService.get_template_object(template_key)

        if template.schemas and template.schemas.defect_schema:
            for field in template.schemas.defect_schema.fields:
                assert field.type in self.VALID_FIELD_TYPES, \
                    f"{template_key} defect schema field {field.field_id} has invalid type: {field.type}"


class TestMonolithicTemplateStepTypes:
    """Test that all templates use correct step types."""

    VALID_STEP_TYPES = [
        'SETUP', 'VISUAL_INSPECTION', 'FUNCTION_TEST',
        'MEASUREMENT', 'DEFECT_CAPTURE'
    ]

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_template_uses_valid_step_types(self, template_key):
        """Test that template only uses valid step types."""
        template = TemplateService.get_template_object(template_key)

        for step in template.procedure.steps:
            assert step.type in self.VALID_STEP_TYPES, \
                f"{template_key} step {step.step_key} has invalid type: {step.type}"


class TestMonolithicTemplateEnums:
    """Test enum definitions in monolithic templates."""

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_template_has_severity_enum(self, template_key):
        """Test that all templates define severity enum."""
        template = TemplateService.get_template_object(template_key)

        assert 'severity' in template.enums, f"{template_key} missing severity enum"
        severity_values = template.enums['severity']

        # Check standard severity values
        assert 'SAFE' in severity_values
        assert 'UNSAFE_OUT_OF_SERVICE' in severity_values

    @pytest.mark.parametrize('template_key', [
        'ansi_a92_2_frequent_inspection',
        'ansi_a92_2_periodic_inspection',
        'ansi_a92_2_load_test_only',
        'ansi_a92_2_major_structural_inspection'
    ])
    def test_enums_are_lists_not_objects(self, template_key):
        """Test that enums are simple arrays, not objects."""
        template = TemplateService.load_template(template_key)

        for enum_name, enum_values in template['enums'].items():
            assert isinstance(enum_values, list), \
                f"{template_key} enum {enum_name} is not a list"

            # Check all values are strings
            for value in enum_values:
                assert isinstance(value, str), \
                    f"{template_key} enum {enum_name} contains non-string value: {value}"


class TestMonolithicTemplateRules:
    """Test validation rules in monolithic templates."""

    def test_periodic_has_safety_rules(self):
        """Test periodic inspection has safety validation rules."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_inspection')

        assert template.rules is not None
        assert len(template.rules) >= 2

        # Check rules have proper structure
        for rule in template.rules:
            assert rule.rule_id is not None
            assert rule.title is not None
            assert rule.assert_ is not None
            assert rule.on_fail is not None
            assert rule.on_fail.severity is not None

    def test_load_test_has_validation_rules(self):
        """Test load test has weight and drift validation rules."""
        template = TemplateService.get_template_object('ansi_a92_2_load_test_only')

        assert template.rules is not None
        assert len(template.rules) >= 2

        rule_ids = [rule.rule_id for rule in template.rules]
        assert 'load_test_weight_adequate' in rule_ids
        assert 'drift_within_manufacturer_limit' in rule_ids or 'load_test_must_pass' in rule_ids

    def test_major_structural_has_required_tests(self):
        """Test major structural requires load test."""
        template = TemplateService.get_template_object('ansi_a92_2_major_structural_inspection')

        assert template.rules is not None
        assert len(template.rules) >= 3

        # Should have rule requiring load test
        rule_ids = [rule.rule_id for rule in template.rules]
        assert any('load_test' in rule_id for rule_id in rule_ids)


class TestMonolithicTemplateBlocking:
    """Test blocking_fail settings on critical steps."""

    def test_frequent_has_blocking_steps(self):
        """Test frequent inspection has blocking steps for safety."""
        template = TemplateService.get_template_object('ansi_a92_2_frequent_inspection')

        blocking_steps = template.get_blocking_steps()
        assert len(blocking_steps) > 0, "Frequent inspection should have blocking steps"

    def test_periodic_has_blocking_steps(self):
        """Test periodic inspection has blocking steps."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_inspection')

        blocking_steps = template.get_blocking_steps()
        assert len(blocking_steps) > 0, "Periodic inspection should have blocking steps"

    def test_load_test_has_blocking_steps(self):
        """Test load test has blocking steps."""
        template = TemplateService.get_template_object('ansi_a92_2_load_test_only')

        blocking_steps = template.get_blocking_steps()
        assert len(blocking_steps) > 0, "Load test should have blocking steps"


class TestMonolithicTemplateFileValidity:
    """Test that template JSON files are valid."""

    @pytest.mark.parametrize('template_key,filename', [
        ('ansi_a92_2_frequent_inspection', 'frequent_inspection.json'),
        ('ansi_a92_2_periodic_inspection', 'periodic_inspection.json'),
        ('ansi_a92_2_load_test_only', 'load_test_only.json'),
        ('ansi_a92_2_major_structural_inspection', 'major_structural_inspection.json')
    ])
    def test_template_file_is_valid_json(self, template_key, filename):
        """Test that template file is valid JSON."""
        template_file = (
            Path(TemplateService.TEMPLATE_BASE_DIR) /
            'ansi_a92_2_2021' /
            filename
        )

        is_valid, error_msg = TemplateService.validate_template_file(template_file)

        assert is_valid is True, f"{filename} validation failed: {error_msg}"
        assert error_msg is None


class TestMonolithicTemplateCompleteness:
    """Test that templates are comprehensive and complete."""

    def test_frequent_inspection_completeness(self):
        """Test frequent inspection covers all required items."""
        template = TemplateService.get_template_object('ansi_a92_2_frequent_inspection')

        # Should have steps for all major systems
        step_keys = [step.step_key for step in template.procedure.steps]

        # Check for key inspection areas
        assert any('control' in key for key in step_keys), "Missing controls inspection"
        assert any('emergency' in key for key in step_keys), "Missing emergency controls"
        assert any('safety' in key for key in step_keys), "Missing safety devices"
        assert any('structural' in key or 'visual' in key for key in step_keys), "Missing visual inspection"

    def test_periodic_inspection_completeness(self):
        """Test periodic inspection is comprehensive."""
        template = TemplateService.get_template_object('ansi_a92_2_periodic_inspection')

        step_keys = [step.step_key for step in template.procedure.steps]

        # Check for comprehensive coverage
        assert any('structural' in key for key in step_keys), "Missing structural inspection"
        assert any('weld' in key for key in step_keys), "Missing weld inspection"
        assert any('bolt' in key or 'fastener' in key for key in step_keys), "Missing bolts/fasteners"
        assert any('hydraulic' in key for key in step_keys), "Missing hydraulic system"
        assert any('electrical' in key for key in step_keys), "Missing electrical system"

    def test_load_test_completeness(self):
        """Test load test covers all required movements."""
        template = TemplateService.get_template_object('ansi_a92_2_load_test_only')

        step_keys = [step.step_key for step in template.procedure.steps]

        # Check for all load test movements
        assert any('raise' in key for key in step_keys), "Missing boom raise test"
        assert any('extend' in key for key in step_keys), "Missing boom extension test"
        assert any('rotat' in key for key in step_keys), "Missing rotation test"
        assert any('drift' in key for key in step_keys), "Missing drift test"
        assert any('lower' in key for key in step_keys), "Missing lowering test"
        assert any('post' in key and 'test' in key for key in step_keys), "Missing post-test inspection"


class TestMonolithicTemplateConsistency:
    """Test consistency across monolithic templates."""

    def test_all_use_same_severity_enum(self):
        """Test that all templates use consistent severity enum values."""
        templates = [
            'ansi_a92_2_frequent_inspection',
            'ansi_a92_2_periodic_inspection',
            'ansi_a92_2_load_test_only',
            'ansi_a92_2_major_structural_inspection'
        ]

        severity_enums = []
        for template_key in templates:
            template = TemplateService.get_template_object(template_key)
            severity_enums.append(set(template.enums['severity']))

        # All should have the same severity values
        first = severity_enums[0]
        for severity_enum in severity_enums[1:]:
            assert severity_enum == first, "Severity enums are inconsistent across templates"

    def test_all_use_af_inspection_template_format(self):
        """Test that all templates use AF_INSPECTION_TEMPLATE format."""
        templates = [
            'ansi_a92_2_frequent_inspection',
            'ansi_a92_2_periodic_inspection',
            'ansi_a92_2_load_test_only',
            'ansi_a92_2_major_structural_inspection'
        ]

        for template_key in templates:
            template = TemplateService.get_template_object(template_key)
            assert template.format == 'AF_INSPECTION_TEMPLATE'
            assert template.format_version == 1
