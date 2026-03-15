"""
Tests for Inspection Outcome Calculator

Verifies automatic pass/fail determination based on defects.
"""

import pytest
from django.utils import timezone
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.inspections.services.outcome_calculator import OutcomeCalculator
from apps.customers.models import Customer
from apps.assets.models import Equipment


@pytest.mark.django_db
class TestOutcomeCalculator:
    """Test automatic outcome calculation."""

    @pytest.fixture
    def customer(self):
        """Create test customer."""
        return Customer.objects.create(
            name="Test Customer",
            is_active=True
        )

    @pytest.fixture
    def equipment(self, customer):
        """Create test equipment."""
        return Equipment.objects.create(
            customer=customer,
            equipment_type="A92_2_AERIAL",
            serial_number="TEST-12345",
            manufacturer="Test Mfg",
            model="Test Model",
            is_active=True
        )

    @pytest.fixture
    def inspection_run(self, customer, equipment):
        """Create test inspection run."""
        return InspectionRun.objects.create(
            customer=customer,
            asset_type='EQUIPMENT',
            asset_id=equipment.id,
            template_key='test_template',
            status='IN_PROGRESS',
            started_at=timezone.now(),
            template_snapshot={
                'template': {'template_key': 'test'},
                'procedure': {
                    'steps': [
                        {
                            'step_key': 'step1',
                            'blocking_fail': True,
                            'auto_defect_on': [
                                {
                                    'when': {'path': 'field1', 'equals': True},
                                    'defect': {'title': 'Blocking defect'}
                                }
                            ]
                        },
                        {
                            'step_key': 'step2',
                            'blocking_fail': False
                        }
                    ]
                }
            },
            step_data={}
        )

    def test_pass_no_defects(self, inspection_run):
        """Test PASS outcome with no defects."""
        result = OutcomeCalculator.calculate_outcome(inspection_run, [])

        assert result['outcome'] == 'PASS'
        assert result['summary']['total_defects'] == 0
        assert result['summary']['equipment_safe_for_operation'] is True
        assert result['summary']['requires_repairs'] is False

    def test_pass_only_minor_defects(self, inspection_run):
        """Test PASS outcome with only MINOR/ADVISORY defects."""
        defects = [
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step1',
                severity='MINOR',
                title='Minor issue',
                description='Minor issue found',
                defect_identity='test1'
            ),
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step2',
                severity='ADVISORY',
                title='Advisory notice',
                description='Advisory',
                defect_identity='test2'
            )
        ]

        result = OutcomeCalculator.calculate_outcome(inspection_run, defects)

        assert result['outcome'] == 'PASS'
        assert result['summary']['total_defects'] == 2
        assert result['summary']['defects_by_severity']['MINOR'] == 1
        assert result['summary']['defects_by_severity']['ADVISORY'] == 1
        assert result['summary']['equipment_safe_for_operation'] is True

    def test_pass_with_repairs_major_defects(self, inspection_run):
        """Test PASS_WITH_REPAIRS outcome with MAJOR defects."""
        defects = [
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step1',
                severity='MAJOR',
                title='Major issue',
                description='Requires repair',
                defect_identity='test1'
            ),
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step2',
                severity='MINOR',
                title='Minor issue',
                description='Minor',
                defect_identity='test2'
            )
        ]

        result = OutcomeCalculator.calculate_outcome(inspection_run, defects)

        assert result['outcome'] == 'PASS_WITH_REPAIRS'
        assert result['summary']['total_defects'] == 2
        assert result['summary']['defects_by_severity']['MAJOR'] == 1
        assert result['summary']['major_defects_found'] is True
        assert result['summary']['equipment_safe_for_operation'] is True
        assert result['summary']['requires_repairs'] is True

    def test_fail_critical_defects(self, inspection_run):
        """Test FAIL outcome with CRITICAL defects."""
        defects = [
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step1',
                severity='CRITICAL',
                title='Critical issue',
                description='Equipment unsafe',
                defect_identity='test1'
            )
        ]

        result = OutcomeCalculator.calculate_outcome(inspection_run, defects)

        assert result['outcome'] == 'FAIL'
        assert result['summary']['critical_defects_found'] is True
        assert result['summary']['equipment_safe_for_operation'] is False
        assert result['summary']['requires_immediate_action'] is True
        assert result['summary']['requires_repairs'] is True

    def test_fail_blocking_failure(self, inspection_run):
        """Test FAIL outcome with blocking step failure."""
        # Set step data to trigger blocking failure
        inspection_run.step_data = {
            'step1': {'field1': True}  # Triggers auto_defect_on condition
        }
        inspection_run.save()

        result = OutcomeCalculator.calculate_outcome(inspection_run, [])

        assert result['outcome'] == 'FAIL'
        assert len(result['summary']['blocking_failures']) == 1
        assert 'step1' in result['summary']['blocking_failures']
        assert result['summary']['equipment_safe_for_operation'] is False

    def test_blocking_failure_with_any_field_in_condition(self, inspection_run):
        """Test blocking failure detection with any_field_in condition."""
        inspection_run.template_snapshot['procedure']['steps'][0]['auto_defect_on'] = [
            {
                'when': {'any_field_in': ['EXCESSIVE', 'REQUIRES_REPLACEMENT']},
                'defect': {'title': 'Critical wear'}
            }
        ]
        inspection_run.step_data = {
            'step1': {
                'field1': 'NONE',
                'field2': 'EXCESSIVE'  # Triggers condition
            }
        }
        inspection_run.save()

        result = OutcomeCalculator.calculate_outcome(inspection_run, [])

        assert result['outcome'] == 'FAIL'
        assert 'step1' in result['summary']['blocking_failures']

    def test_no_blocking_failure_when_condition_not_met(self, inspection_run):
        """Test no blocking failure when conditions not met."""
        inspection_run.step_data = {
            'step1': {'field1': False},  # Does not trigger condition
            'step2': {'field2': 'PASS'}
        }
        inspection_run.save()

        result = OutcomeCalculator.calculate_outcome(inspection_run, [])

        assert result['outcome'] == 'PASS'
        assert len(result['summary']['blocking_failures']) == 0

    def test_mixed_severity_defects(self, inspection_run):
        """Test outcome with mixed severity defects."""
        defects = [
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step1',
                severity='CRITICAL',
                title='Critical',
                description='Critical',
                defect_identity='test1'
            ),
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step2',
                severity='MAJOR',
                title='Major',
                description='Major',
                defect_identity='test2'
            ),
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step3',
                severity='MINOR',
                title='Minor',
                description='Minor',
                defect_identity='test3'
            ),
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step4',
                severity='ADVISORY',
                title='Advisory',
                description='Advisory',
                defect_identity='test4'
            )
        ]

        result = OutcomeCalculator.calculate_outcome(inspection_run, defects)

        assert result['outcome'] == 'FAIL'  # CRITICAL takes precedence
        assert result['summary']['total_defects'] == 4
        assert result['summary']['defects_by_severity']['CRITICAL'] == 1
        assert result['summary']['defects_by_severity']['MAJOR'] == 1
        assert result['summary']['defects_by_severity']['MINOR'] == 1
        assert result['summary']['defects_by_severity']['ADVISORY'] == 1

    def test_get_outcome_display(self):
        """Test outcome display strings."""
        assert 'safe for operation' in OutcomeCalculator.get_outcome_display('PASS').lower()
        assert 'repairs required' in OutcomeCalculator.get_outcome_display('PASS_WITH_REPAIRS').lower()
        assert 'unsafe' in OutcomeCalculator.get_outcome_display('FAIL').lower()

    def test_outcome_summary_structure(self, inspection_run):
        """Test that outcome summary has all required fields."""
        defects = [
            InspectionDefect(
                inspection_run=inspection_run,
                step_key='step1',
                severity='MAJOR',
                title='Test',
                description='Test',
                defect_identity='test1'
            )
        ]

        result = OutcomeCalculator.calculate_outcome(inspection_run, defects)
        summary = result['summary']

        # Check all required summary fields exist
        assert 'total_defects' in summary
        assert 'defects_by_severity' in summary
        assert 'blocking_failures' in summary
        assert 'critical_defects_found' in summary
        assert 'major_defects_found' in summary
        assert 'equipment_safe_for_operation' in summary
        assert 'requires_immediate_action' in summary
        assert 'requires_repairs' in summary

        # Check defects_by_severity has all severity levels
        assert 'CRITICAL' in summary['defects_by_severity']
        assert 'MAJOR' in summary['defects_by_severity']
        assert 'MINOR' in summary['defects_by_severity']
        assert 'ADVISORY' in summary['defects_by_severity']
