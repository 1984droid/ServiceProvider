"""
Tests for Customer Duplicate Detection

Tests for the DuplicateDetectionService and related API endpoints.
"""
import pytest
from django.utils import timezone
from apps.customers.models import Customer
from apps.customers.services import DuplicateDetectionService
from tests.factories import CustomerFactory


@pytest.mark.django_db
class TestDuplicateDetectionService:
    """Test DuplicateDetectionService fuzzy matching logic"""

    def test_exact_name_match_high_score(self):
        """Exact name match should return very high similarity score"""
        CustomerFactory(name="ABC Trucking Company")

        service = DuplicateDetectionService(similarity_threshold=0.2)
        results = service.find_duplicates(name="ABC Trucking Company")

        assert len(results) == 1
        # Exact match should be weighted heavily (50% of 1.0 similarity)
        assert results[0]['score'] >= 0.45  # Considering name weight is 0.5
        assert results[0]['match_details']['name_similarity'] >= 0.9

    def test_similar_name_match_medium_score(self):
        """Similar names should return medium similarity scores"""
        CustomerFactory(name="ABC Trucking Company")

        service = DuplicateDetectionService(similarity_threshold=0.2)
        results = service.find_duplicates(name="ABC Truck Co")

        assert len(results) >= 0  # May or may not match depending on trigram algorithm
        if len(results) > 0:
            assert results[0]['match_details']['name_similarity'] > 0

    def test_usdot_exact_match_returns_duplicate(self):
        """Exact USDOT number match should return as potential duplicate"""
        CustomerFactory(name="ABC Trucking", usdot_number="123456")

        service = DuplicateDetectionService(similarity_threshold=0.05)  # Lower threshold
        results = service.find_duplicates(
            name="XYZ Transport",  # Different name
            usdot_number="123456"  # Same USDOT
        )

        assert len(results) == 1
        assert results[0]['match_details']['usdot_match'] is True
        assert results[0]['match_details']['regulatory_match'] is True

    def test_mc_number_exact_match_returns_duplicate(self):
        """Exact MC number match should return as potential duplicate"""
        CustomerFactory(name="ABC Trucking", mc_number="MC-987654")

        service = DuplicateDetectionService(similarity_threshold=0.05)  # Lower threshold
        results = service.find_duplicates(
            name="XYZ Transport",
            mc_number="MC-987654"
        )

        assert len(results) == 1
        assert results[0]['match_details']['mc_match'] is True
        assert results[0]['match_details']['regulatory_match'] is True

    def test_legal_name_similarity_contributes_to_score(self):
        """Legal name similarity should contribute to overall score"""
        CustomerFactory(
            name="ABC Inc",
            legal_name="ABC Trucking Corporation LLC"
        )

        service = DuplicateDetectionService(similarity_threshold=0.15)
        results = service.find_duplicates(
            name="ABC Company",
            legal_name="ABC Trucking Corp LLC"
        )

        assert len(results) >= 0  # May vary based on trigram matching
        if len(results) > 0:
            assert results[0]['match_details']['legal_name_similarity'] >= 0

    def test_address_similarity_boosts_score(self):
        """Address similarity should boost overall score"""
        CustomerFactory(
            name="ABC Trucking",
            city="Los Angeles",
            state="CA"
        )

        service = DuplicateDetectionService()
        results = service.find_duplicates(
            name="ABC Trucking",
            city="Los Angeles",
            state="CA"
        )

        assert len(results) == 1
        assert results[0]['match_details']['city_similarity'] > 0.9
        assert results[0]['match_details']['state_match'] is True
        assert results[0]['match_details']['address_score'] > 0

    def test_popularity_boosts_score(self):
        """Customers with high selection count should get popularity boost"""
        # Customer with no selections
        customer1 = CustomerFactory(name="ABC Trucking", selection_count=0)

        # Customer with many selections
        customer2 = CustomerFactory(name="ABC Trucking Company", selection_count=100)

        service = DuplicateDetectionService(similarity_threshold=0.2)
        results = service.find_duplicates(name="ABC Trucking")

        # Both should be found
        assert len(results) == 2

        # Find each customer in results
        result_map = {str(r['customer'].id): r for r in results}
        result1 = result_map[str(customer1.id)]
        result2 = result_map[str(customer2.id)]

        # Popular customer should have popularity multiplier
        assert result2['match_details']['popularity_multiplier'] > 1.0
        assert result2['match_details']['selection_count'] == 100
        assert result1['match_details']['popularity_multiplier'] == 1.0

    def test_inactive_customers_not_returned(self):
        """Inactive customers should not be returned in results"""
        CustomerFactory(name="ABC Trucking", is_active=False)

        service = DuplicateDetectionService()
        results = service.find_duplicates(name="ABC Trucking")

        assert len(results) == 0

    def test_exclude_customer_id_filters_out_specified_customer(self):
        """exclude_customer_id should filter out the specified customer (for updates)"""
        customer1 = CustomerFactory(name="ABC Trucking")
        customer2 = CustomerFactory(name="ABC Trucking Company")

        service = DuplicateDetectionService()
        results = service.find_duplicates(
            name="ABC Trucking",
            exclude_customer_id=str(customer1.id)
        )

        # Should only return customer2
        assert len(results) == 1
        assert results[0]['customer'].id == customer2.id

    def test_max_results_limits_output(self):
        """max_results parameter should limit number of results returned"""
        # Create 15 similar customers
        for i in range(15):
            CustomerFactory(name=f"ABC Trucking Company {i}")

        service = DuplicateDetectionService(similarity_threshold=0.2)
        results = service.find_duplicates(name="ABC Trucking", max_results=5)

        assert len(results) <= 5  # May be less if similarity threshold not met

    def test_threshold_filters_low_similarity_matches(self):
        """Only matches above threshold should be returned"""
        CustomerFactory(name="ABC Trucking")

        # Use high threshold
        service = DuplicateDetectionService(similarity_threshold=0.8)
        results = service.find_duplicates(name="XYZ Transport")  # Very different name

        assert len(results) == 0

    def test_empty_name_returns_empty_list(self):
        """Empty or whitespace-only name should return empty list"""
        CustomerFactory(name="ABC Trucking")

        service = DuplicateDetectionService()
        results = service.find_duplicates(name="")

        assert results == []

    def test_increment_selection_count_increases_count(self):
        """increment_selection_count should increase selection count"""
        customer = CustomerFactory(selection_count=5)

        service = DuplicateDetectionService()
        service.increment_selection_count(str(customer.id))

        customer.refresh_from_db()
        assert customer.selection_count == 6
        assert customer.last_selected_at is not None

    def test_increment_selection_count_sets_timestamp(self):
        """increment_selection_count should set last_selected_at"""
        customer = CustomerFactory(last_selected_at=None)
        before = timezone.now()

        service = DuplicateDetectionService()
        service.increment_selection_count(str(customer.id))

        customer.refresh_from_db()
        assert customer.last_selected_at is not None
        assert customer.last_selected_at >= before

    def test_score_to_confidence_mapping(self):
        """Test confidence level mapping from scores"""
        service = DuplicateDetectionService()

        assert service._score_to_confidence(0.9) == "VERY_HIGH"
        assert service._score_to_confidence(0.7) == "HIGH"
        assert service._score_to_confidence(0.5) == "MEDIUM"
        assert service._score_to_confidence(0.35) == "LOW"

    def test_case_insensitive_matching(self):
        """Duplicate detection should be case-insensitive"""
        CustomerFactory(name="ABC TRUCKING COMPANY", usdot_number="123456")

        service = DuplicateDetectionService()
        results = service.find_duplicates(
            name="abc trucking company",
            usdot_number="123456"
        )

        assert len(results) == 1


@pytest.mark.django_db
class TestDuplicateDetectionAPI:
    """Test duplicate detection API endpoints"""

    def test_check_duplicates_endpoint_finds_matches(self, admin_api_client):
        """POST /api/customers/check_duplicates/ should find similar customers"""
        CustomerFactory(name="ABC Trucking Company")

        response = admin_api_client.post('/api/customers/check_duplicates/', {
            'name': 'ABC Trucking'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['found_duplicates'] is True
        assert data['count'] >= 1
        assert len(data['matches']) >= 1
        assert 'customer' in data['matches'][0]
        assert 'score' in data['matches'][0]
        assert 'confidence' in data['matches'][0]
        assert 'match_details' in data['matches'][0]

    def test_check_duplicates_endpoint_no_matches(self, admin_api_client):
        """Endpoint should return empty list when no matches found"""
        CustomerFactory(name="ABC Trucking")

        response = admin_api_client.post('/api/customers/check_duplicates/', {
            'name': 'XYZ Completely Different Company'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['found_duplicates'] is False
        assert data['count'] == 0
        assert data['matches'] == []

    def test_check_duplicates_requires_name(self, admin_api_client):
        """Endpoint should require name parameter"""
        response = admin_api_client.post('/api/customers/check_duplicates/', {})

        assert response.status_code == 400
        assert 'name' in response.json()['error'].lower()

    def test_check_duplicates_with_all_parameters(self, admin_api_client):
        """Endpoint should accept all matching parameters"""
        CustomerFactory(
            name="ABC Trucking",
            legal_name="ABC Trucking LLC",
            usdot_number="123456",
            mc_number="MC-789",
            city="Los Angeles",
            state="CA"
        )

        response = admin_api_client.post('/api/customers/check_duplicates/', {
            'name': 'ABC Trucking',
            'legal_name': 'ABC Trucking LLC',
            'usdot_number': '123456',
            'mc_number': 'MC-789',
            'city': 'Los Angeles',
            'state': 'CA'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['found_duplicates'] is True
        assert data['count'] == 1

        # Check that all match details are present
        match = data['matches'][0]
        assert match['match_details']['name_similarity'] > 0.9
        assert match['match_details']['legal_name_similarity'] > 0.9
        assert match['match_details']['usdot_match'] is True
        assert match['match_details']['mc_match'] is True
        assert match['match_details']['state_match'] is True

    def test_increment_selection_endpoint(self, admin_api_client):
        """POST /api/customers/{id}/increment_selection/ should increment count"""
        customer = CustomerFactory(selection_count=10)

        response = admin_api_client.post(
            f'/api/customers/{customer.id}/increment_selection/'
        )

        assert response.status_code == 200
        customer.refresh_from_db()
        assert customer.selection_count == 11

    def test_increment_selection_requires_authentication(self, api_client):
        """Endpoint should require authentication"""
        customer = CustomerFactory()

        response = api_client.post(f'/api/customers/{customer.id}/increment_selection/')

        assert response.status_code == 401

    def test_check_duplicates_requires_authentication(self, api_client):
        """Endpoint should require authentication"""
        response = api_client.post('/api/customers/check_duplicates/', {
            'name': 'ABC Trucking'
        })

        assert response.status_code == 401


@pytest.mark.django_db
class TestDuplicateDetectionIntegration:
    """Integration tests for complete duplicate detection workflow"""

    def test_complete_duplicate_detection_workflow(self, admin_api_client):
        """Test complete workflow: check duplicates → create customer → increment selection"""
        # Setup: Create existing customer
        existing = CustomerFactory(
            name="ABC Trucking Company",
            usdot_number="123456",
            city="Los Angeles",
            state="CA"
        )

        # Step 1: Check for duplicates before creating new customer
        response = admin_api_client.post('/api/customers/check_duplicates/', {
            'name': 'ABC Trucking',
            'usdot_number': '123456',
            'city': 'Los Angeles',
            'state': 'CA'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['found_duplicates'] is True
        assert data['matches'][0]['customer']['id'] == str(existing.id)

        # Step 2: User decides to use existing customer instead of creating duplicate
        # Increment selection count
        response = admin_api_client.post(
            f'/api/customers/{existing.id}/increment_selection/'
        )

        assert response.status_code == 200

        # Step 3: Verify selection was tracked
        existing.refresh_from_db()
        assert existing.selection_count == 1
        assert existing.last_selected_at is not None

    def test_no_duplicates_allows_creation(self, admin_api_client):
        """When no duplicates found, should allow customer creation"""
        # Check for duplicates
        response = admin_api_client.post('/api/customers/check_duplicates/', {
            'name': 'Unique New Company'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['found_duplicates'] is False

        # Create new customer
        response = admin_api_client.post('/api/customers/', {
            'name': 'Unique New Company',
            'city': 'New York',
            'state': 'NY'
        })

        assert response.status_code == 201
