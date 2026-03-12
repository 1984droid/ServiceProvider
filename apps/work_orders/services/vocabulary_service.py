"""
Work Order Vocabulary Service

Manages work order vocabulary (verbs, nouns, service locations) from JSON catalogs.
"""

import json
import os
from typing import Dict, List, Any, Optional
from django.conf import settings


class VocabularyService:
    """
    Service for loading and managing work order vocabulary.

    Vocabulary Structure:
    - Verbs: Actions (Replace, Inspect, Repair, etc.)
    - Nouns: Components/parts (Hydraulic Hose, Boom Cylinder, etc.)
    - Service Locations: Where work is performed (Boom Assembly, Chassis, etc.)
    - Noun Categories: Groupings for nouns (Hydraulic, Electrical, etc.)
    - Location Categories: Groupings for locations

    Data Source:
    - asset_templates_v2_3/work_order_vocabulary/*.json
    """

    _vocabulary_cache = None
    _base_path = os.path.join(settings.BASE_DIR, 'asset_templates_v2_3', 'work_order_vocabulary')

    @classmethod
    def load_vocabulary(cls, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load vocabulary from JSON files with caching.

        Args:
            force_reload: Force reload from files (bypass cache)

        Returns:
            Dict with verbs, nouns, service_locations, etc.
        """
        if cls._vocabulary_cache and not force_reload:
            return cls._vocabulary_cache

        vocabulary = {}

        # Load verbs
        verbs_path = os.path.join(cls._base_path, 'verbs.json')
        if os.path.exists(verbs_path):
            with open(verbs_path, 'r') as f:
                data = json.load(f)
                # Handle both wrapped (dict with 'verbs' key) and unwrapped (list) formats
                vocabulary['verbs'] = data.get('verbs', []) if isinstance(data, dict) else data
        else:
            vocabulary['verbs'] = []

        # Load nouns
        nouns_path = os.path.join(cls._base_path, 'nouns.json')
        if os.path.exists(nouns_path):
            with open(nouns_path, 'r') as f:
                data = json.load(f)
                vocabulary['nouns'] = data.get('nouns', []) if isinstance(data, dict) else data
        else:
            vocabulary['nouns'] = []

        # Load service locations
        locations_path = os.path.join(cls._base_path, 'service_locations.json')
        if os.path.exists(locations_path):
            with open(locations_path, 'r') as f:
                data = json.load(f)
                vocabulary['service_locations'] = data.get('service_locations', []) if isinstance(data, dict) else data
        else:
            vocabulary['service_locations'] = []

        # Load noun categories
        noun_cat_path = os.path.join(cls._base_path, 'noun_categories.json')
        if os.path.exists(noun_cat_path):
            with open(noun_cat_path, 'r') as f:
                data = json.load(f)
                vocabulary['noun_categories'] = data.get('noun_categories', []) if isinstance(data, dict) else data
        else:
            vocabulary['noun_categories'] = []

        # Load location categories
        loc_cat_path = os.path.join(cls._base_path, 'location_categories.json')
        if os.path.exists(loc_cat_path):
            with open(loc_cat_path, 'r') as f:
                data = json.load(f)
                vocabulary['location_categories'] = data.get('location_categories', []) if isinstance(data, dict) else data
        else:
            vocabulary['location_categories'] = []

        cls._vocabulary_cache = vocabulary
        return vocabulary

    @classmethod
    def get_verbs(cls) -> List[Dict]:
        """
        Get all verbs.

        Returns:
            List of verb dictionaries
        """
        vocab = cls.load_vocabulary()
        return vocab.get('verbs', [])

    @classmethod
    def get_nouns(cls, category: Optional[str] = None) -> List[Dict]:
        """
        Get nouns, optionally filtered by category.

        Args:
            category: Category to filter by (e.g., 'Hydraulic', 'Electrical')

        Returns:
            List of noun dictionaries
        """
        vocab = cls.load_vocabulary()
        nouns = vocab.get('nouns', [])

        if category:
            # Filter by category if specified
            return [n for n in nouns if n.get('category') == category]

        return nouns

    @classmethod
    def get_service_locations(cls) -> List[Dict]:
        """
        Get all service locations.

        Returns:
            List of service location dictionaries
        """
        vocab = cls.load_vocabulary()
        return vocab.get('service_locations', [])

    @classmethod
    def get_noun_categories(cls) -> List[Dict]:
        """
        Get all noun categories.

        Returns:
            List of noun category dictionaries
        """
        vocab = cls.load_vocabulary()
        return vocab.get('noun_categories', [])

    @classmethod
    def get_location_categories(cls) -> List[Dict]:
        """
        Get all location categories.

        Returns:
            List of location category dictionaries
        """
        vocab = cls.load_vocabulary()
        return vocab.get('location_categories', [])

    @classmethod
    def validate_line_vocabulary(
        cls,
        verb: str,
        noun: str,
        location: str
    ) -> bool:
        """
        Validate that verb/noun/location combination exists in vocabulary.

        Args:
            verb: Verb to validate
            noun: Noun to validate
            location: Service location to validate

        Returns:
            True if all exist in vocabulary, False otherwise
        """
        vocab = cls.load_vocabulary()

        # Check verb exists (use 'label' field)
        verbs = [v.get('label', v.get('verb', v.get('name', ''))) for v in vocab.get('verbs', [])]
        if verb not in verbs:
            return False

        # Check noun exists (use 'label' field)
        nouns = [n.get('label', n.get('noun', n.get('name', ''))) for n in vocab.get('nouns', [])]
        if noun not in nouns:
            return False

        # Check location exists (use 'label' field)
        locations = [l.get('label', l.get('location', l.get('name', ''))) for l in vocab.get('service_locations', [])]
        if location not in locations:
            return False

        return True

    @classmethod
    def suggest_vocabulary(
        cls,
        description: str
    ) -> Dict[str, List[str]]:
        """
        Suggest verb/noun/location based on description text.

        Uses simple keyword matching to suggest vocabulary.

        Args:
            description: Free-text description

        Returns:
            Dict with suggested verbs, nouns, and locations
        """
        vocab = cls.load_vocabulary()
        description_lower = description.lower()

        suggestions = {
            'verbs': [],
            'nouns': [],
            'locations': []
        }

        # Suggest verbs
        for verb_obj in vocab.get('verbs', []):
            verb = verb_obj.get('label', verb_obj.get('verb', verb_obj.get('name', '')))
            if verb and verb.lower() in description_lower:
                suggestions['verbs'].append(verb)

        # Suggest nouns
        for noun_obj in vocab.get('nouns', []):
            noun = noun_obj.get('label', noun_obj.get('noun', noun_obj.get('name', '')))
            if noun and noun.lower() in description_lower:
                suggestions['nouns'].append(noun)

        # Suggest locations
        for loc_obj in vocab.get('service_locations', []):
            location = loc_obj.get('label', loc_obj.get('location', loc_obj.get('name', '')))
            if location and location.lower() in description_lower:
                suggestions['locations'].append(location)

        return suggestions

    @classmethod
    def find_verb(cls, verb_name: str) -> Optional[Dict]:
        """
        Find verb by name (case-insensitive).

        Args:
            verb_name: Verb to find

        Returns:
            Verb dictionary or None
        """
        verbs = cls.get_verbs()
        verb_lower = verb_name.lower()

        for verb_obj in verbs:
            verb = verb_obj.get('label', verb_obj.get('verb', verb_obj.get('name', '')))
            if verb and verb.lower() == verb_lower:
                return verb_obj

        return None

    @classmethod
    def find_noun(cls, noun_name: str) -> Optional[Dict]:
        """
        Find noun by name (case-insensitive).

        Args:
            noun_name: Noun to find

        Returns:
            Noun dictionary or None
        """
        nouns = cls.get_nouns()
        noun_lower = noun_name.lower()

        for noun_obj in nouns:
            noun = noun_obj.get('label', noun_obj.get('noun', noun_obj.get('name', '')))
            if noun and noun.lower() == noun_lower:
                return noun_obj

        return None

    @classmethod
    def find_service_location(cls, location_name: str) -> Optional[Dict]:
        """
        Find service location by name (case-insensitive).

        Args:
            location_name: Location to find

        Returns:
            Location dictionary or None
        """
        locations = cls.get_service_locations()
        location_lower = location_name.lower()

        for loc_obj in locations:
            location = loc_obj.get('label', loc_obj.get('location', loc_obj.get('name', '')))
            if location and location.lower() == location_lower:
                return loc_obj

        return None
