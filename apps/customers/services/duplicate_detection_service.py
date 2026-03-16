"""
Duplicate Detection Service

Fuzzy matching service to detect potential duplicate customers using PostgreSQL trigrams.
Prevents accidental duplicate customer creation with weighted similarity scoring.
"""
import logging
import math
from typing import List, Dict, Optional
from django.db.models import Q, F, Value, FloatField
from django.contrib.postgres.search import TrigramSimilarity
from django.utils import timezone

logger = logging.getLogger(__name__)


class DuplicateDetectionService:
    """
    Service for detecting potential duplicate customers using fuzzy text matching.

    Uses PostgreSQL pg_trgm extension for similarity scoring with configurable weights:
    - Name similarity (primary): 50%
    - Legal name similarity: 30%
    - USDOT/MC# exact match: 10%
    - Address similarity: 10%

    Results are boosted by popularity (selection_count) to surface frequently-used customers.
    """

    # Configurable thresholds and weights
    DEFAULT_THRESHOLD = 0.3  # Minimum similarity score (0.0-1.0)
    NAME_WEIGHT = 0.5        # Primary business name
    LEGAL_NAME_WEIGHT = 0.3  # Legal registered name
    REGULATORY_WEIGHT = 0.1  # USDOT/MC# exact match
    ADDRESS_WEIGHT = 0.1     # Physical address

    def __init__(self, similarity_threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize duplicate detection service.

        Args:
            similarity_threshold: Minimum similarity score to consider a match (0.0-1.0)
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        self.threshold = similarity_threshold

    def find_duplicates(
        self,
        name: str,
        legal_name: Optional[str] = None,
        usdot_number: Optional[str] = None,
        mc_number: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        max_results: int = 10,
        exclude_customer_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Find potential duplicate customers based on provided information.

        Args:
            name: Business name (required)
            legal_name: Legal registered name (optional)
            usdot_number: USDOT number (optional)
            mc_number: MC number (optional)
            city: City (optional)
            state: State code (optional)
            max_results: Maximum number of results to return
            exclude_customer_id: Customer ID to exclude from results (for update scenarios)

        Returns:
            List of dicts with customer data and match scores, ordered by relevance
        """
        from apps.customers.models import Customer

        if not name or not name.strip():
            return []

        # Start with active customers only
        queryset = Customer.objects.filter(is_active=True)

        # Exclude specific customer if provided (for update scenarios)
        if exclude_customer_id:
            queryset = queryset.exclude(id=exclude_customer_id)

        # Calculate name similarity (required)
        queryset = queryset.annotate(
            name_similarity=TrigramSimilarity('name', name)
        )

        # Calculate legal name similarity if provided
        if legal_name and legal_name.strip():
            queryset = queryset.annotate(
                legal_name_similarity=TrigramSimilarity('legal_name', legal_name)
            )
        else:
            queryset = queryset.annotate(
                legal_name_similarity=Value(0.0, output_field=FloatField())
            )

        # Calculate city similarity if provided (for address matching)
        if city and city.strip():
            queryset = queryset.annotate(
                city_similarity=TrigramSimilarity('city', city)
            )
        else:
            queryset = queryset.annotate(
                city_similarity=Value(0.0, output_field=FloatField())
            )

        # Build filter for potential matches
        # At least name similarity above threshold OR exact regulatory match
        filters = Q(name_similarity__gte=self.threshold)

        # Add exact match filters for regulatory IDs (very strong signal)
        if usdot_number and usdot_number.strip():
            filters |= Q(usdot_number__iexact=usdot_number.strip())
        if mc_number and mc_number.strip():
            filters |= Q(mc_number__iexact=mc_number.strip())

        queryset = queryset.filter(filters)

        # Select related fields for serialization
        queryset = queryset.select_related('primary_contact')

        # Fetch candidates
        candidates = list(queryset[:100])  # Limit initial fetch for performance

        # Calculate composite scores in Python (more flexible than SQL for complex scoring)
        results = []
        for customer in candidates:
            score_data = self._calculate_composite_score(
                customer=customer,
                name_sim=customer.name_similarity,
                legal_name_sim=customer.legal_name_similarity,
                city_sim=customer.city_similarity,
                usdot_match=(
                    usdot_number
                    and customer.usdot_number
                    and customer.usdot_number.upper() == usdot_number.upper()
                ),
                mc_match=(
                    mc_number
                    and customer.mc_number
                    and customer.mc_number.upper() == mc_number.upper()
                ),
                state_match=(state and customer.state and customer.state.upper() == state.upper())
            )

            # Only include if above threshold
            if score_data['total_score'] >= self.threshold:
                results.append({
                    'customer': customer,
                    'score': score_data['total_score'],
                    'confidence': self._score_to_confidence(score_data['total_score']),
                    'match_details': score_data,
                })

        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]

    def _calculate_composite_score(
        self,
        customer,
        name_sim: float,
        legal_name_sim: float,
        city_sim: float,
        usdot_match: bool,
        mc_match: bool,
        state_match: bool
    ) -> Dict:
        """
        Calculate composite similarity score with multiple factors.

        Returns dict with breakdown of score components.
        """
        # Base weighted score
        base_score = (
            name_sim * self.NAME_WEIGHT +
            legal_name_sim * self.LEGAL_NAME_WEIGHT
        )

        # Regulatory ID exact match (strong signal)
        regulatory_score = 0.0
        if usdot_match or mc_match:
            regulatory_score = 1.0 * self.REGULATORY_WEIGHT

        # Address similarity
        address_score = 0.0
        if city_sim > 0 or state_match:
            city_component = city_sim * 0.7
            state_component = 1.0 if state_match else 0.0
            address_score = (city_component + state_component * 0.3) * self.ADDRESS_WEIGHT

        # Combine scores
        raw_score = base_score + regulatory_score + address_score

        # Apply popularity boost (logarithmic to prevent over-weighting)
        # Customers selected more frequently get a small boost
        popularity_multiplier = 1.0
        if customer.selection_count > 0:
            # 1.0 to ~1.15 multiplier based on selection count
            popularity_multiplier = 1.0 + (math.log10(customer.selection_count + 1) * 0.05)

        total_score = min(raw_score * popularity_multiplier, 1.0)  # Cap at 1.0

        return {
            'total_score': round(total_score, 3),
            'base_score': round(base_score, 3),
            'name_similarity': round(name_sim, 3),
            'legal_name_similarity': round(legal_name_sim, 3),
            'regulatory_match': usdot_match or mc_match,
            'usdot_match': usdot_match,
            'mc_match': mc_match,
            'address_score': round(address_score, 3),
            'city_similarity': round(city_sim, 3),
            'state_match': state_match,
            'popularity_multiplier': round(popularity_multiplier, 3),
            'selection_count': customer.selection_count,
        }

    def _score_to_confidence(self, score: float) -> str:
        """
        Convert numerical score to human-readable confidence level.

        Args:
            score: Similarity score (0.0-1.0)

        Returns:
            Confidence level: "VERY_HIGH", "HIGH", "MEDIUM", or "LOW"
        """
        if score >= 0.8:
            return "VERY_HIGH"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def increment_selection_count(self, customer_id: str) -> None:
        """
        Increment selection count for popularity tracking.

        Should be called when a customer is selected from duplicate matches
        or when customer is accessed in general operations.

        Args:
            customer_id: UUID of customer
        """
        from apps.customers.models import Customer

        try:
            Customer.objects.filter(id=customer_id).update(
                selection_count=F('selection_count') + 1,
                last_selected_at=timezone.now()
            )
            logger.debug(f"Incremented selection count for customer {customer_id}")
        except Exception as e:
            logger.error(f"Failed to increment selection count for customer {customer_id}: {e}")
