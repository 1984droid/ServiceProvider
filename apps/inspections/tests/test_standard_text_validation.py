"""
Tests for ANSI Standard Text Validation

Validates that:
1. All templates have valid standard text references
2. standard_text.json has valid structure
3. Template references match available excerpts
"""

import json
from pathlib import Path
from django.test import TestCase
from apps.inspections.schemas.template_schema import (
    InspectionTemplate,
    StandardTextReference
)


class StandardTextValidationTest(TestCase):
    """Validate standard text integration across all templates."""

    @classmethod
    def setUpClass(cls):
        """Load all templates and standard text once for all tests."""
        super().setUpClass()

        # Load standard text
        cls.standard_text_path = Path('static/inspection_references/ansi_a92_2_2021/standard_text.json')
        with open(cls.standard_text_path, 'r', encoding='utf-8') as f:
            cls.standard_text_data = json.load(f)

        # Load all ANSI templates
        cls.templates_dir = Path('apps/inspections/templates/inspection_templates/ansi_a92_2_2021')
        cls.template_files = {
            'frequent_inspection': 'frequent_inspection.json',
            'periodic_inspection': 'periodic_inspection.json',
            'major_structural_inspection': 'major_structural_inspection.json',
            'dielectric_test_periodic': 'dielectric_test_periodic.json',
            'load_test_only': 'load_test_only.json'
        }

        cls.templates = {}
        for key, filename in cls.template_files.items():
            template_path = cls.templates_dir / filename
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                cls.templates[key] = InspectionTemplate(**template_data)

    def test_standard_text_json_structure(self):
        """Test that standard_text.json has valid structure."""
        # Check top-level fields
        self.assertIn('standard', self.standard_text_data)
        self.assertEqual(self.standard_text_data['standard'], 'ANSI A92.2-2021')

        self.assertIn('common_excerpts', self.standard_text_data)
        self.assertIsInstance(self.standard_text_data['common_excerpts'], dict)

        # Check we have excerpts
        excerpts = self.standard_text_data['common_excerpts']
        self.assertGreater(len(excerpts), 0, "No excerpts found in standard_text.json")

        # Validate each excerpt structure
        for key, excerpt in excerpts.items():
            with self.subTest(excerpt_key=key):
                self.assertIn('section', excerpt, f"Missing 'section' in excerpt '{key}'")
                self.assertIn('excerpt', excerpt, f"Missing 'excerpt' in excerpt '{key}'")

                # Validate types
                self.assertIsInstance(excerpt['section'], str)
                self.assertIsInstance(excerpt['excerpt'], str)

                # Validate not empty
                self.assertTrue(excerpt['section'].strip(), f"Empty section in excerpt '{key}'")
                self.assertTrue(excerpt['excerpt'].strip(), f"Empty excerpt in excerpt '{key}'")

    def test_standard_text_has_excerpts(self):
        """Test that we have standard text excerpts."""
        excerpts = self.standard_text_data['common_excerpts']
        self.assertGreater(len(excerpts), 0, "Should have at least one excerpt")
        # Informational: current count
        print(f"Found {len(excerpts)} standard text excerpts")

    def test_all_templates_load_successfully(self):
        """Test that all templates load and validate."""
        # Dynamically count templates from files
        expected_count = len(self.template_files)
        self.assertEqual(len(self.templates), expected_count,
                        f"Expected {expected_count} ANSI templates")

        for template_key, template in self.templates.items():
            with self.subTest(template=template_key):
                self.assertIsInstance(template, InspectionTemplate)
                self.assertIsNotNone(template.template)

    def test_all_template_steps_have_standard_text(self):
        """Test that all non-SETUP steps have standard_text."""
        total_steps = 0
        setup_steps = 0
        steps_with_standard_text = 0
        steps_without_standard_text = []

        for template_key, template in self.templates.items():
            for step in template.procedure.steps:
                total_steps += 1

                # SETUP steps may not have standard_text
                if hasattr(step, 'type') and step.type == 'SETUP':
                    setup_steps += 1
                    continue

                if step.standard_text:
                    steps_with_standard_text += 1
                else:
                    steps_without_standard_text.append({
                        'template': template_key,
                        'step': step.step_key
                    })

        # Assert good coverage (accounting for SETUP steps)
        non_setup_steps = total_steps - setup_steps
        self.assertGreater(total_steps, 0, "Should have at least some steps")
        self.assertGreater(non_setup_steps, 0, "Should have at least some non-SETUP steps")

        # All non-SETUP steps should have standard_text
        self.assertEqual(
            steps_with_standard_text,
            non_setup_steps,
            f"Expected all {non_setup_steps} non-SETUP steps to have standard_text. "
            f"Total steps: {total_steps}, SETUP steps: {setup_steps}, "
            f"Missing: {steps_without_standard_text}"
        )

    def test_standard_text_references_are_valid(self):
        """Test that all StandardTextReference objects are valid."""
        for template_key, template in self.templates.items():
            for step in template.procedure.steps:
                if step.standard_text:
                    with self.subTest(
                        template=template_key,
                        step=step.step_key
                    ):
                        std_text = step.standard_text

                        # Validate it's the right type
                        self.assertIsInstance(std_text, StandardTextReference)

                        # Validate section is not empty
                        self.assertTrue(
                            std_text.section.strip(),
                            f"Empty section in {template_key}/{step.step_key}"
                        )

                        # Validate excerpt is not empty
                        self.assertTrue(
                            std_text.excerpt.strip(),
                            f"Empty excerpt in {template_key}/{step.step_key}"
                        )

                        # Validate excerpt is reasonable length (not just a placeholder)
                        self.assertGreater(
                            len(std_text.excerpt),
                            20,
                            f"Excerpt too short in {template_key}/{step.step_key}"
                        )

    def test_template_sections_match_available_excerpts(self):
        """Test that template sections can be found in standard_text.json."""
        # Build section lookup from standard_text.json
        available_sections = set()
        for excerpt in self.standard_text_data['common_excerpts'].values():
            available_sections.add(excerpt['section'])

        unmatched_sections = []

        for template_key, template in self.templates.items():
            for step in template.procedure.steps:
                if step.standard_text:
                    section = step.standard_text.section

                    # Check if this section exists in our standard_text.json
                    if section not in available_sections:
                        unmatched_sections.append({
                            'template': template_key,
                            'step': step.step_key,
                            'section': section
                        })

        # All sections should match
        self.assertEqual(
            len(unmatched_sections),
            0,
            f"Found sections in templates not in standard_text.json: {unmatched_sections}"
        )

    def test_frequent_inspection_coverage(self):
        """Test frequent inspection template has good coverage."""
        template = self.templates['frequent_inspection']

        step_count = len(template.procedure.steps)
        steps_with_std_text = sum(
            1 for step in template.procedure.steps
            if step.standard_text
        )

        self.assertGreater(step_count, 0, "Frequent inspection should have steps")
        # At least 70% coverage (accounting for SETUP steps)
        coverage = steps_with_std_text / step_count if step_count > 0 else 0
        self.assertGreater(coverage, 0.7,
                          f"Should have >70% coverage. Found {steps_with_std_text}/{step_count} = {coverage:.1%}")

    def test_periodic_inspection_coverage(self):
        """Test periodic inspection template has good coverage."""
        template = self.templates['periodic_inspection']

        step_count = len(template.procedure.steps)
        steps_with_std_text = sum(
            1 for step in template.procedure.steps
            if step.standard_text
        )

        self.assertGreater(step_count, 0, "Periodic inspection should have steps")
        coverage = steps_with_std_text / step_count if step_count > 0 else 0
        self.assertGreater(coverage, 0.7,
                          f"Should have >70% coverage. Found {steps_with_std_text}/{step_count} = {coverage:.1%}")

    def test_major_structural_inspection_coverage(self):
        """Test major structural inspection template has good coverage."""
        template = self.templates['major_structural_inspection']

        step_count = len(template.procedure.steps)
        steps_with_std_text = sum(
            1 for step in template.procedure.steps
            if step.standard_text
        )

        self.assertGreater(step_count, 0, "Major structural should have steps")
        coverage = steps_with_std_text / step_count if step_count > 0 else 0
        self.assertGreater(coverage, 0.7,
                          f"Should have >70% coverage. Found {steps_with_std_text}/{step_count} = {coverage:.1%}")

    def test_dielectric_test_coverage(self):
        """Test dielectric test template has good coverage."""
        template = self.templates['dielectric_test_periodic']

        step_count = len(template.procedure.steps)
        steps_with_std_text = sum(
            1 for step in template.procedure.steps
            if step.standard_text
        )

        self.assertGreater(step_count, 0, "Dielectric test should have steps")
        coverage = steps_with_std_text / step_count if step_count > 0 else 0
        self.assertGreater(coverage, 0.7,
                          f"Should have >70% coverage. Found {steps_with_std_text}/{step_count} = {coverage:.1%}")

    def test_load_test_coverage(self):
        """Test load test template has good coverage."""
        template = self.templates['load_test_only']

        step_count = len(template.procedure.steps)
        steps_with_std_text = sum(
            1 for step in template.procedure.steps
            if step.standard_text
        )

        self.assertGreater(step_count, 0, "Load test should have steps")
        coverage = steps_with_std_text / step_count if step_count > 0 else 0
        self.assertGreater(coverage, 0.7,
                          f"Should have >70% coverage. Found {steps_with_std_text}/{step_count} = {coverage:.1%}")

    def test_no_duplicate_sections_in_standard_text(self):
        """Test that standard_text.json has no duplicate sections."""
        sections = []
        for excerpt in self.standard_text_data['common_excerpts'].values():
            sections.append(excerpt['section'])

        # Check for duplicates
        duplicates = [s for s in sections if sections.count(s) > 1]
        unique_duplicates = list(set(duplicates))

        self.assertEqual(
            len(unique_duplicates),
            0,
            f"Found duplicate sections in standard_text.json: {unique_duplicates}"
        )

    def test_standard_text_excerpt_quality(self):
        """Test that excerpts are reasonable quality (not too short/long)."""
        for key, excerpt_data in self.standard_text_data['common_excerpts'].items():
            with self.subTest(excerpt_key=key):
                excerpt = excerpt_data['excerpt']

                # Not too short (at least 20 chars)
                self.assertGreater(
                    len(excerpt),
                    20,
                    f"Excerpt '{key}' too short: {len(excerpt)} chars"
                )

                # Not too long (under 500 chars for readability)
                self.assertLess(
                    len(excerpt),
                    500,
                    f"Excerpt '{key}' too long: {len(excerpt)} chars"
                )

                # Doesn't end with ellipsis (should be complete sentences)
                self.assertFalse(
                    excerpt.endswith('...'),
                    f"Excerpt '{key}' ends with ellipsis - should be complete"
                )
