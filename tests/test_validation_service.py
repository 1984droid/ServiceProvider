"""
Tests for Response Validation Service

Tests field validation, step validation, and required field checking.
"""

import pytest
from decimal import Decimal
from apps.inspections.services.validation_service import (
    ResponseValidator,
    FieldValidationResult,
    StepValidationResult,
    ValidationError
)


class TestBooleanValidation:
    """Test boolean field validation."""

    def test_validate_boolean_true(self):
        field = {'field_id': 'test', 'type': 'BOOLEAN'}
        result = ResponseValidator.validate_field(field, True)
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_boolean_false(self):
        field = {'field_id': 'test', 'type': 'BOOLEAN'}
        result = ResponseValidator.validate_field(field, False)
        assert result.valid

    def test_validate_boolean_invalid_type(self):
        field = {'field_id': 'test', 'type': 'BOOLEAN'}
        result = ResponseValidator.validate_field(field, "true")
        assert not result.valid
        assert 'Expected boolean' in result.errors[0]


class TestTextValidation:
    """Test text field validation."""

    def test_validate_text_simple(self):
        field = {'field_id': 'test', 'type': 'TEXT'}
        result = ResponseValidator.validate_field(field, 'Hello World')
        assert result.valid

    def test_validate_text_empty(self):
        field = {'field_id': 'test', 'type': 'TEXT'}
        result = ResponseValidator.validate_field(field, '')
        assert result.valid

    def test_validate_text_min_length(self):
        field = {'field_id': 'test', 'type': 'TEXT', 'min_length': 5}
        result = ResponseValidator.validate_field(field, 'abc')
        assert not result.valid
        assert 'at least 5 characters' in result.errors[0]

    def test_validate_text_max_length(self):
        field = {'field_id': 'test', 'type': 'TEXT', 'max_length': 10}
        result = ResponseValidator.validate_field(field, 'a' * 20)
        assert not result.valid
        assert 'at most 10 characters' in result.errors[0]

    def test_validate_text_invalid_type(self):
        field = {'field_id': 'test', 'type': 'TEXT'}
        result = ResponseValidator.validate_field(field, 123)
        assert not result.valid


class TestNumberValidation:
    """Test numeric field validation."""

    def test_validate_number_int(self):
        field = {'field_id': 'test', 'type': 'NUMBER'}
        result = ResponseValidator.validate_field(field, 42)
        assert result.valid

    def test_validate_number_float(self):
        field = {'field_id': 'test', 'type': 'NUMBER'}
        result = ResponseValidator.validate_field(field, 3.14)
        assert result.valid

    def test_validate_number_decimal(self):
        field = {'field_id': 'test', 'type': 'NUMBER'}
        result = ResponseValidator.validate_field(field, Decimal('10.5'))
        assert result.valid

    def test_validate_number_string_convertible(self):
        field = {'field_id': 'test', 'type': 'NUMBER'}
        result = ResponseValidator.validate_field(field, "42.5")
        assert result.valid

    def test_validate_number_string_invalid(self):
        field = {'field_id': 'test', 'type': 'NUMBER'}
        result = ResponseValidator.validate_field(field, "abc")
        assert not result.valid

    def test_validate_number_min(self):
        field = {'field_id': 'test', 'type': 'NUMBER', 'min': 10}
        result = ResponseValidator.validate_field(field, 5)
        assert not result.valid
        assert 'at least 10' in result.errors[0]

    def test_validate_number_max(self):
        field = {'field_id': 'test', 'type': 'NUMBER', 'max': 100}
        result = ResponseValidator.validate_field(field, 150)
        assert not result.valid
        assert 'at most 100' in result.errors[0]

    def test_validate_number_in_range(self):
        field = {'field_id': 'test', 'type': 'NUMBER', 'min': 0, 'max': 100}
        result = ResponseValidator.validate_field(field, 50)
        assert result.valid


class TestEnumValidation:
    """Test enum field validation."""

    def test_validate_enum_valid_value(self):
        field = {'field_id': 'test', 'type': 'ENUM', 'values': ['PASS', 'FAIL', 'NA']}
        result = ResponseValidator.validate_field(field, 'PASS')
        assert result.valid

    def test_validate_enum_invalid_value(self):
        field = {'field_id': 'test', 'type': 'ENUM', 'values': ['PASS', 'FAIL', 'NA']}
        result = ResponseValidator.validate_field(field, 'MAYBE')
        assert not result.valid
        assert 'not in allowed values' in result.errors[0]

    def test_validate_enum_no_values(self):
        field = {'field_id': 'test', 'type': 'ENUM', 'values': []}
        result = ResponseValidator.validate_field(field, 'PASS')
        assert not result.valid

    def test_validate_enum_invalid_type(self):
        field = {'field_id': 'test', 'type': 'ENUM', 'values': ['PASS', 'FAIL']}
        result = ResponseValidator.validate_field(field, 123)
        assert not result.valid


class TestChoiceMultiValidation:
    """Test multi-choice field validation."""

    def test_validate_choice_multi_empty(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C']}
        result = ResponseValidator.validate_field(field, [])
        assert result.valid

    def test_validate_choice_multi_single(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C']}
        result = ResponseValidator.validate_field(field, ['A'])
        assert result.valid

    def test_validate_choice_multi_multiple(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C']}
        result = ResponseValidator.validate_field(field, ['A', 'C'])
        assert result.valid

    def test_validate_choice_multi_invalid_value(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C']}
        result = ResponseValidator.validate_field(field, ['A', 'D'])
        assert not result.valid

    def test_validate_choice_multi_min_selections(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C'], 'min_selections': 2}
        result = ResponseValidator.validate_field(field, ['A'])
        assert not result.valid
        assert 'at least 2 options' in result.errors[0]

    def test_validate_choice_multi_max_selections(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C'], 'max_selections': 2}
        result = ResponseValidator.validate_field(field, ['A', 'B', 'C'])
        assert not result.valid
        assert 'at most 2 options' in result.errors[0]

    def test_validate_choice_multi_not_array(self):
        field = {'field_id': 'test', 'type': 'CHOICE_MULTI', 'values': ['A', 'B', 'C']}
        result = ResponseValidator.validate_field(field, 'A')
        assert not result.valid


class TestAttachmentsValidation:
    """Test attachments field validation."""

    def test_validate_attachments_empty(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        result = ResponseValidator.validate_field(field, [])
        assert result.valid

    def test_validate_attachments_valid_url(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        attachments = [
            {'filename': 'photo.jpg', 'url': 'https://example.com/photo.jpg'}
        ]
        result = ResponseValidator.validate_field(field, attachments)
        assert result.valid

    def test_validate_attachments_valid_file_data(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        attachments = [
            {'filename': 'photo.jpg', 'file_data': 'base64encodeddata'}
        ]
        result = ResponseValidator.validate_field(field, attachments)
        assert result.valid

    def test_validate_attachments_missing_filename(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        attachments = [
            {'url': 'https://example.com/photo.jpg'}
        ]
        result = ResponseValidator.validate_field(field, attachments)
        assert not result.valid

    def test_validate_attachments_missing_url_and_data(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        attachments = [
            {'filename': 'photo.jpg'}
        ]
        result = ResponseValidator.validate_field(field, attachments)
        assert not result.valid

    def test_validate_attachments_not_array(self):
        field = {'field_id': 'test', 'type': 'ATTACHMENTS'}
        result = ResponseValidator.validate_field(field, {'filename': 'test.jpg'})
        assert not result.valid


class TestNullValues:
    """Test validation of null/None values."""

    def test_null_value_required_field(self):
        field = {'field_id': 'test', 'type': 'TEXT', 'required': True}
        result = ResponseValidator.validate_field(field, None)
        assert not result.valid
        assert 'required' in result.errors[0]

    def test_null_value_optional_field(self):
        field = {'field_id': 'test', 'type': 'TEXT', 'required': False}
        result = ResponseValidator.validate_field(field, None)
        assert result.valid


class TestStepValidation:
    """Test full step response validation."""

    def test_validate_step_all_fields_valid(self):
        template_step = {
            'step_key': 'test_step',
            'fields': [
                {'field_id': 'cleanliness', 'type': 'ENUM', 'values': ['CLEAN', 'DIRTY'], 'required': True},
                {'field_id': 'notes', 'type': 'TEXT', 'required': False}
            ]
        }
        field_data = {
            'cleanliness': 'CLEAN',
            'notes': 'All good'
        }
        result = ResponseValidator.validate_step_response(template_step, field_data)
        assert result.valid
        assert len(result.field_results) == 2

    def test_validate_step_missing_required_field(self):
        template_step = {
            'step_key': 'test_step',
            'fields': [
                {'field_id': 'cleanliness', 'type': 'ENUM', 'values': ['CLEAN', 'DIRTY'], 'required': True},
            ]
        }
        field_data = {}
        result = ResponseValidator.validate_step_response(template_step, field_data)
        assert not result.valid
        assert 'cleanliness' in result.field_results
        assert not result.field_results['cleanliness'].valid

    def test_validate_step_unknown_field(self):
        template_step = {
            'step_key': 'test_step',
            'fields': [
                {'field_id': 'cleanliness', 'type': 'ENUM', 'values': ['CLEAN', 'DIRTY']}
            ]
        }
        field_data = {
            'cleanliness': 'CLEAN',
            'unknown_field': 'value'
        }
        result = ResponseValidator.validate_step_response(template_step, field_data)
        assert not result.valid
        assert 'Unknown field' in result.errors[0]

    def test_validate_step_invalid_field_value(self):
        template_step = {
            'step_key': 'test_step',
            'fields': [
                {'field_id': 'temperature', 'type': 'NUMBER', 'min': 0, 'max': 100, 'required': True}
            ]
        }
        field_data = {
            'temperature': 150
        }
        result = ResponseValidator.validate_step_response(template_step, field_data)
        assert not result.valid
        assert not result.field_results['temperature'].valid


class TestRequiredStepsChecking:
    """Test checking for required steps completion."""

    def test_check_required_steps_all_complete(self):
        template = {
            'procedure': {
                'steps': [
                    {
                        'step_key': 'step1',
                        'required': True,
                        'fields': [{'field_id': 'field1', 'required': True}]
                    },
                    {
                        'step_key': 'step2',
                        'required': False,
                        'fields': []
                    }
                ]
            }
        }
        step_data = {
            'step1': {'field1': 'value'}
        }
        missing = ResponseValidator.check_required_steps(template, step_data)
        assert len(missing) == 0

    def test_check_required_steps_missing_step(self):
        template = {
            'procedure': {
                'steps': [
                    {'step_key': 'step1', 'required': True, 'fields': []},
                    {'step_key': 'step2', 'required': True, 'fields': []}
                ]
            }
        }
        step_data = {
            'step1': {}
        }
        missing = ResponseValidator.check_required_steps(template, step_data)
        assert 'step2' in missing
        assert len(missing) == 1

    def test_check_required_steps_missing_required_field(self):
        template = {
            'procedure': {
                'steps': [
                    {
                        'step_key': 'step1',
                        'required': True,
                        'fields': [
                            {'field_id': 'field1', 'required': True},
                            {'field_id': 'field2', 'required': False}
                        ]
                    }
                ]
            }
        }
        step_data = {
            'step1': {'field2': 'value'}  # Missing required field1
        }
        missing = ResponseValidator.check_required_steps(template, step_data)
        assert 'step1' in missing
