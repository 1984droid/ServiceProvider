"""
Pytest configuration and fixtures.

This file provides reusable fixtures for all tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.config import TEST_USERS
from tests.factories import (
    CustomerFactory,
    ContactFactory,
    VehicleFactory,
    EquipmentFactory,
    VINDecodeDataFactory,
    USDOTProfileFactory,
)

User = get_user_model()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def admin_user(db):
    """Create admin user for testing."""
    user_data = TEST_USERS['admin'].copy()
    return User.objects.create_user(**user_data)


@pytest.fixture
def regular_user(db):
    """Create regular user for testing."""
    user_data = TEST_USERS['regular'].copy()
    return User.objects.create_user(**user_data)


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def admin_api_client(admin_user):
    """API client authenticated as admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def user_api_client(regular_user):
    """API client authenticated as regular user."""
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client


# ============================================================================
# Model Fixtures - Single Instances
# ============================================================================

@pytest.fixture
def customer(db):
    """Create a default customer."""
    return CustomerFactory()


@pytest.fixture
def customer_minimal(db):
    """Create a minimal customer."""
    return CustomerFactory.minimal()


@pytest.fixture
def customer_with_usdot(db):
    """Create a customer with USDOT number."""
    return CustomerFactory.with_usdot()


@pytest.fixture
def contact(db, customer):
    """Create a default contact for customer."""
    return ContactFactory(customer=customer)


@pytest.fixture
def contact_automated(db, customer):
    """Create an automated contact."""
    return ContactFactory.automated(customer=customer)


@pytest.fixture
def vehicle(db, customer):
    """Create a default vehicle."""
    return VehicleFactory(customer=customer)


@pytest.fixture
def vehicle_with_decode(db, customer):
    """Create a vehicle with VIN decode data."""
    vehicle = VehicleFactory(customer=customer)
    VINDecodeDataFactory(vehicle=vehicle, vin=vehicle.vin)
    return vehicle


@pytest.fixture
def equipment(db, customer):
    """Create default equipment."""
    return EquipmentFactory(customer=customer)


@pytest.fixture
def equipment_aerial(db, customer):
    """Create aerial device equipment with full data."""
    return EquipmentFactory.insulated_aerial(customer=customer)


@pytest.fixture
def mounted_equipment(db, customer, vehicle):
    """Create equipment mounted on vehicle."""
    return EquipmentFactory(customer=customer, mounted_on_vehicle=vehicle)


@pytest.fixture
def usdot_profile(db, customer):
    """Create USDOT profile for customer."""
    return USDOTProfileFactory(customer=customer)


# ============================================================================
# Model Fixtures - Collections
# ============================================================================

@pytest.fixture
def customer_with_contacts(db, customer):
    """Create customer with multiple contacts, one primary."""
    contacts = ContactFactory.create_batch(3, customer=customer)
    customer.primary_contact = contacts[0]
    customer.save()
    return customer


@pytest.fixture
def customer_with_fleet(db, customer):
    """Create customer with vehicles and equipment."""
    vehicles = VehicleFactory.create_batch(3, customer=customer)
    equipment = EquipmentFactory.create_batch(5, customer=customer)

    # Mount some equipment on vehicles
    equipment[0].mounted_on_vehicle = vehicles[0]
    equipment[0].save()
    equipment[1].mounted_on_vehicle = vehicles[0]
    equipment[1].save()

    return customer


@pytest.fixture
def complete_customer(db):
    """
    Create a complete customer setup:
    - Customer with USDOT profile
    - Primary contact + additional contacts
    - Vehicles with VIN decode
    - Equipment (some mounted)
    """
    customer = CustomerFactory.with_usdot()

    # Contacts
    contacts = ContactFactory.create_batch(3, customer=customer)
    customer.primary_contact = contacts[0]
    customer.save()

    # USDOT Profile
    USDOTProfileFactory(customer=customer, usdot_number=customer.usdot_number)

    # Vehicles with decode
    vehicles = VehicleFactory.create_batch(2, customer=customer)
    for vehicle in vehicles:
        VINDecodeDataFactory(vehicle=vehicle, vin=vehicle.vin)

    # Equipment (some mounted)
    equipment = EquipmentFactory.create_batch(3, customer=customer)
    equipment[0].mounted_on_vehicle = vehicles[0]
    equipment[0].save()

    return customer


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture
def clean_db(db):
    """
    Ensure database is clean before and after test.
    Use this for tests that need guaranteed isolation.
    """
    from apps.customers.models import Customer, Contact, USDOTProfile
    from apps.assets.models import Vehicle, Equipment, VINDecodeData

    # Clean before
    VINDecodeData.objects.all().delete()
    Equipment.objects.all().delete()
    Vehicle.objects.all().delete()
    USDOTProfile.objects.all().delete()
    Contact.objects.all().delete()
    Customer.objects.all().delete()

    yield

    # Clean after
    VINDecodeData.objects.all().delete()
    Equipment.objects.all().delete()
    Vehicle.objects.all().delete()
    USDOTProfile.objects.all().delete()
    Contact.objects.all().delete()
    Customer.objects.all().delete()


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def vin_tracker():
    """Track VINs used in a test to avoid duplicates."""
    used_vins = set()

    def track(vin):
        if vin in used_vins:
            raise ValueError(f"VIN {vin} already used in this test")
        used_vins.add(vin)
        return vin

    return track


@pytest.fixture
def serial_tracker():
    """Track serial numbers used in a test to avoid duplicates."""
    used_serials = set()

    def track(serial):
        if serial in used_serials:
            raise ValueError(f"Serial {serial} already used in this test")
        used_serials.add(serial)
        return serial

    return track
