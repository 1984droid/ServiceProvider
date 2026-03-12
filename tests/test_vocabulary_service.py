"""
Tests for VocabularyService (Phase 5)

Tests vocabulary loading, validation, and suggestion functionality.
"""

from django.test import TestCase
from apps.work_orders.services.vocabulary_service import VocabularyService


class VocabularyServiceTest(TestCase):
    """Test VocabularyService functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Force reload vocabulary before each test
        VocabularyService._vocabulary_cache = None

    def test_load_vocabulary(self):
        """Test loading vocabulary from JSON files."""
        vocab = VocabularyService.load_vocabulary()

        self.assertIsInstance(vocab, dict)
        self.assertIn('verbs', vocab)
        self.assertIn('nouns', vocab)
        self.assertIn('service_locations', vocab)

    def test_vocabulary_caching(self):
        """Test vocabulary is cached after first load."""
        vocab1 = VocabularyService.load_vocabulary()
        vocab2 = VocabularyService.load_vocabulary()

        # Should return same cached instance
        self.assertIs(vocab1, vocab2)

    def test_force_reload(self):
        """Test force reload bypasses cache."""
        vocab1 = VocabularyService.load_vocabulary()
        vocab2 = VocabularyService.load_vocabulary(force_reload=True)

        # Should return new instance
        self.assertIsNot(vocab1, vocab2)

    def test_get_verbs(self):
        """Test get_verbs returns list."""
        verbs = VocabularyService.get_verbs()

        self.assertIsInstance(verbs, list)

    def test_get_nouns(self):
        """Test get_nouns returns list."""
        nouns = VocabularyService.get_nouns()

        self.assertIsInstance(nouns, list)

    def test_get_nouns_with_category_filter(self):
        """Test get_nouns with category filter."""
        all_nouns = VocabularyService.get_nouns()

        if all_nouns:
            # Get first noun's category
            first_category = all_nouns[0].get('category')

            if first_category:
                filtered = VocabularyService.get_nouns(category=first_category)

                # All filtered nouns should have matching category
                for noun in filtered:
                    self.assertEqual(noun.get('category'), first_category)

    def test_get_service_locations(self):
        """Test get_service_locations returns list."""
        locations = VocabularyService.get_service_locations()

        self.assertIsInstance(locations, list)

    def test_get_noun_categories(self):
        """Test get_noun_categories returns list."""
        categories = VocabularyService.get_noun_categories()

        self.assertIsInstance(categories, list)

    def test_get_location_categories(self):
        """Test get_location_categories returns list."""
        categories = VocabularyService.get_location_categories()

        self.assertIsInstance(categories, list)

    def test_suggest_vocabulary(self):
        """Test vocabulary suggestion from description."""
        description = "Replace hydraulic hose on boom assembly"
        suggestions = VocabularyService.suggest_vocabulary(description)

        self.assertIsInstance(suggestions, dict)
        self.assertIn('verbs', suggestions)
        self.assertIn('nouns', suggestions)
        self.assertIn('locations', suggestions)

    def test_suggest_vocabulary_empty_description(self):
        """Test vocabulary suggestion with empty description."""
        description = ""
        suggestions = VocabularyService.suggest_vocabulary(description)

        # Should return empty suggestions
        self.assertEqual(suggestions['verbs'], [])
        self.assertEqual(suggestions['nouns'], [])
        self.assertEqual(suggestions['locations'], [])

    def test_find_verb(self):
        """Test find_verb by name."""
        verbs = VocabularyService.get_verbs()

        if verbs:
            verb_name = verbs[0].get('verb', verbs[0].get('name'))

            if verb_name:
                result = VocabularyService.find_verb(verb_name)
                self.assertIsNotNone(result)

    def test_find_verb_case_insensitive(self):
        """Test find_verb is case-insensitive."""
        verbs = VocabularyService.get_verbs()

        if verbs:
            verb_name = verbs[0].get('verb', verbs[0].get('name'))

            if verb_name:
                # Test lowercase
                result = VocabularyService.find_verb(verb_name.lower())
                self.assertIsNotNone(result)

                # Test uppercase
                result = VocabularyService.find_verb(verb_name.upper())
                self.assertIsNotNone(result)

    def test_find_verb_not_found(self):
        """Test find_verb returns None for non-existent verb."""
        result = VocabularyService.find_verb("NonExistentVerb12345")
        self.assertIsNone(result)

    def test_find_noun(self):
        """Test find_noun by name."""
        nouns = VocabularyService.get_nouns()

        if nouns:
            noun_name = nouns[0].get('noun', nouns[0].get('name'))

            if noun_name:
                result = VocabularyService.find_noun(noun_name)
                self.assertIsNotNone(result)

    def test_find_noun_case_insensitive(self):
        """Test find_noun is case-insensitive."""
        nouns = VocabularyService.get_nouns()

        if nouns:
            noun_name = nouns[0].get('noun', nouns[0].get('name'))

            if noun_name:
                # Test lowercase
                result = VocabularyService.find_noun(noun_name.lower())
                self.assertIsNotNone(result)

    def test_find_noun_not_found(self):
        """Test find_noun returns None for non-existent noun."""
        result = VocabularyService.find_noun("NonExistentNoun12345")
        self.assertIsNone(result)

    def test_find_service_location(self):
        """Test find_service_location by name."""
        locations = VocabularyService.get_service_locations()

        if locations:
            location_name = locations[0].get('location', locations[0].get('name'))

            if location_name:
                result = VocabularyService.find_service_location(location_name)
                self.assertIsNotNone(result)

    def test_find_service_location_case_insensitive(self):
        """Test find_service_location is case-insensitive."""
        locations = VocabularyService.get_service_locations()

        if locations:
            location_name = locations[0].get('location', locations[0].get('name'))

            if location_name:
                # Test lowercase
                result = VocabularyService.find_service_location(location_name.lower())
                self.assertIsNotNone(result)

    def test_find_service_location_not_found(self):
        """Test find_service_location returns None for non-existent location."""
        result = VocabularyService.find_service_location("NonExistentLocation12345")
        self.assertIsNone(result)

    def test_validate_line_vocabulary_missing_files(self):
        """Test validate_line_vocabulary when vocabulary files don't exist."""
        # This should handle gracefully even with empty vocabulary
        result = VocabularyService.validate_line_vocabulary(
            verb="Test",
            noun="Component",
            location="General"
        )

        self.assertIsInstance(result, bool)
