"""
Tests for Customer, Contact, and USDOTProfile models.

All test data comes from tests.config - NO HARDCODED VALUES!
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.customers.models import Customer, Contact, USDOTProfile
from tests.config import (
    get_test_data,
    ERROR_MESSAGES,
    CONSTRAINTS,
    VALID_CHOICES,
)
from tests.factories import CustomerFactory, ContactFactory, USDOTProfileFactory


# ============================================================================
# Customer Model Tests
# ============================================================================

@pytest.mark.django_db
class TestCustomerModel:
    """Test Customer model creation, validation, and relationships."""

    def test_customer_creation_default(self, customer):
        """Test basic customer creation with default data."""
        default_data = get_test_data('customer', 'default')
        assert customer.name == default_data['name']
        assert customer.legal_name == default_data['legal_name']
        assert customer.city == default_data['city']
        assert customer.state == default_data['state']
        assert customer.is_active is True

    def test_customer_creation_minimal(self):
        """Test customer creation with minimal required fields."""
        customer = CustomerFactory.minimal()
        minimal_data = get_test_data('customer', 'minimal')
        assert customer.name == minimal_data['name']
        assert customer.is_active is True

    def test_customer_creation_with_usdot(self):
        """Test customer creation with USDOT/MC numbers."""
        customer = CustomerFactory.with_usdot()
        assert customer.usdot_number is not None
        assert customer.mc_number is not None

    def test_customer_str_representation(self, customer):
        """Test string representation."""
        assert str(customer) == customer.name

    def test_customer_name_required(self):
        """Test that name field is required."""
        with pytest.raises(ValidationError):
            customer = Customer()
            customer.full_clean()

    def test_customer_name_max_length(self):
        """Test name field max length constraint."""
        max_length = CONSTRAINTS['customer']['name']['max_length']
        long_name = 'A' * (max_length + 1)
        with pytest.raises(ValidationError):
            customer = CustomerFactory(name=long_name)
            customer.full_clean()

    def test_customer_state_choices(self):
        """Test state field validates against choices."""
        valid_states = VALID_CHOICES['states']
        customer = CustomerFactory(state=valid_states[0])
        customer.full_clean()  # Should not raise

        with pytest.raises(ValidationError):
            customer = CustomerFactory(state='XX')
            customer.full_clean()

    def test_customer_primary_contact_relationship(self, customer_with_contacts):
        """Test primary contact relationship."""
        assert customer_with_contacts.primary_contact is not None
        assert customer_with_contacts.primary_contact.customer == customer_with_contacts

    def test_customer_contacts_count(self, customer_with_contacts):
        """Test contact count for customer."""
        assert customer_with_contacts.contacts.count() >= 3

    def test_customer_vehicles_relationship(self, customer_with_fleet):
        """Test customer has vehicles."""
        assert customer_with_fleet.vehicles.count() > 0

    def test_customer_equipment_relationship(self, customer_with_fleet):
        """Test customer has equipment."""
        assert customer_with_fleet.equipment.count() > 0


# ============================================================================
# Contact Model Tests
# ============================================================================

@pytest.mark.django_db
class TestContactModel:
    """Test Contact model creation, validation, and relationships."""

    def test_contact_creation_default(self, contact):
        """Test basic contact creation with default data."""
        default_data = get_test_data('contact', 'default')
        assert contact.first_name == default_data['first_name']
        assert contact.last_name == default_data['last_name']
        assert contact.email == default_data['email']
        assert contact.is_active is True
        assert contact.is_automated is False

    def test_contact_creation_minimal(self):
        """Test contact creation with minimal required fields."""
        contact = ContactFactory.minimal()
        minimal_data = get_test_data('contact', 'minimal')
        assert contact.first_name == minimal_data['first_name']
        assert contact.last_name == minimal_data['last_name']
        assert contact.email is not None

    def test_contact_creation_automated(self):
        """Test automated contact creation."""
        contact = ContactFactory.automated()
        automated_data = get_test_data('contact', 'automated')
        assert contact.is_automated is True
        assert contact.first_name == automated_data['first_name']

    def test_contact_str_representation(self, contact):
        """Test string representation."""
        expected = f"{contact.first_name} {contact.last_name} ({contact.customer.name})"
        assert str(contact) == expected

    def test_contact_full_name_property(self, contact):
        """Test full_name property."""
        expected = f"{contact.first_name} {contact.last_name}"
        assert contact.full_name == expected

    def test_contact_is_primary_property(self, customer_with_contacts):
        """Test is_primary property."""
        primary = customer_with_contacts.primary_contact
        assert primary.is_primary is True

        # Other contacts should not be primary
        other_contacts = customer_with_contacts.contacts.exclude(id=primary.id)
        for contact in other_contacts:
            assert contact.is_primary is False

    def test_contact_customer_required(self):
        """Test that customer field is required."""
        minimal_data = get_test_data('contact', 'minimal')
        with pytest.raises(ValidationError):
            Contact.objects.create(
                **minimal_data
                # Missing customer FK
            )

    def test_contact_correspondence_preferences(self):
        """Test correspondence preference fields."""
        contact = ContactFactory(
            receive_invoices=True,
            receive_service_updates=True,
            receive_inspection_reports=True
        )
        assert contact.receive_invoices is True
        assert contact.receive_service_updates is True
        assert contact.receive_inspection_reports is True


# ============================================================================
# USDOTProfile Model Tests
# ============================================================================

@pytest.mark.django_db
class TestUSDOTProfileModel:
    """Test USDOTProfile model creation and validation."""

    def test_usdot_profile_creation(self, customer):
        """Test USDOT profile creation."""
        profile = USDOTProfileFactory(customer=customer)
        default_data = get_test_data('usdot_profile', 'default')
        assert profile.usdot_number == default_data['usdot_number']
        assert profile.legal_name == default_data['legal_name']

    def test_usdot_profile_str_representation(self, customer):
        """Test string representation."""
        profile = USDOTProfileFactory(customer=customer)
        assert str(profile) == f"USDOT Profile: {profile.usdot_number} ({profile.legal_name or 'Unknown'})"

    def test_usdot_profile_one_per_customer(self, customer):
        """Test one-to-one relationship with customer."""
        USDOTProfileFactory(customer=customer)

        with pytest.raises(IntegrityError):
            USDOTProfileFactory(customer=customer)

    def test_usdot_number_required(self, customer):
        """Test USDOT number is required."""
        with pytest.raises(ValidationError):
            profile = USDOTProfile(customer=customer)
            profile.full_clean()

