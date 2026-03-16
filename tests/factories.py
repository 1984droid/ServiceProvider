"""
Factory classes for creating test model instances.

Uses factory_boy pattern for consistent, flexible test data generation.
All default values come from tests.config - NO HARDCODED DATA!
"""

import factory
from factory.django import DjangoModelFactory

from apps.customers.models import Customer, Contact, USDOTProfile
from apps.assets.models import Vehicle, Equipment, VINDecodeData
from apps.inspections.models import InspectionRun, InspectionDefect
from apps.work_orders.models import WorkOrder, WorkOrderDefect
from apps.organization.models import Company, Department, Employee
from tests.config import (
    get_test_data,
    get_next_test_vin,
    get_next_test_serial,
)
from django.utils import timezone
from datetime import datetime


def parse_test_datetime(dt_string):
    """Parse ISO datetime string from test config and ensure it's timezone-aware."""
    dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


# ============================================================================
# Customer Factories
# ============================================================================

class CustomerFactory(DjangoModelFactory):
    """Factory for creating Customer instances."""

    class Meta:
        model = Customer

    name = factory.LazyFunction(lambda: get_test_data('customer', 'default')['name'])
    legal_name = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('legal_name'))
    address_line1 = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('address_line1'))
    address_line2 = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('address_line2', ''))
    city = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('city'))
    state = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('state'))
    postal_code = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('postal_code'))
    country = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('country', 'US'))
    is_active = True

    # USDOT/MC numbers are empty by default (use with_usdot variant)
    usdot_number = ''
    mc_number = ''

    @classmethod
    def minimal(cls, **kwargs):
        """Create customer with minimal required fields."""
        data = get_test_data('customer', 'minimal')
        return cls(**{**data, **kwargs})

    @classmethod
    def with_usdot(cls, **kwargs):
        """Create customer with USDOT and MC numbers."""
        data = get_test_data('customer', 'with_usdot')
        # Make USDOT unique per call
        if 'usdot_number' not in kwargs:
            import random
            data['usdot_number'] = str(int(data['usdot_number']) + random.randint(1, 10000))
        return cls(**{**data, **kwargs})


class ContactFactory(DjangoModelFactory):
    """Factory for creating Contact instances."""

    class Meta:
        model = Contact

    customer = factory.SubFactory(CustomerFactory)
    first_name = factory.LazyFunction(lambda: get_test_data('contact', 'default')['first_name'])
    last_name = factory.LazyFunction(lambda: get_test_data('contact', 'default')['last_name'])
    title = factory.LazyFunction(lambda: get_test_data('contact', 'default').get('title'))
    email = factory.LazyFunction(lambda: get_test_data('contact', 'default')['email'])
    phone = factory.LazyFunction(lambda: get_test_data('contact', 'default').get('phone'))
    mobile = factory.LazyFunction(lambda: get_test_data('contact', 'default').get('mobile'))
    is_active = True
    is_automated = False
    receive_invoices = factory.LazyFunction(lambda: get_test_data('contact', 'default').get('receive_invoices', False))
    receive_service_updates = factory.LazyFunction(lambda: get_test_data('contact', 'default').get('receive_service_updates', False))

    @classmethod
    def minimal(cls, **kwargs):
        """Create contact with minimal required fields."""
        data = get_test_data('contact', 'minimal')
        # Make email unique
        import random
        data['email'] = f"contact{random.randint(1000, 9999)}@example.com"
        return cls(**{**data, **kwargs})

    @classmethod
    def automated(cls, **kwargs):
        """Create automated contact."""
        data = get_test_data('contact', 'automated')
        # Make email unique
        import random
        data['email'] = f"api{random.randint(1000, 9999)}@example.com"
        return cls(**{**data, **kwargs})


class USDOTProfileFactory(DjangoModelFactory):
    """Factory for creating USDOTProfile instances."""

    class Meta:
        model = USDOTProfile

    customer = factory.SubFactory(CustomerFactory)
    usdot_number = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default')['usdot_number'])
    mc_number = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('mc_number'))
    legal_name = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('legal_name'))
    dba_name = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('dba_name'))
    physical_address = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('physical_address'))
    physical_city = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('physical_city'))
    physical_state = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('physical_state'))
    physical_zip = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('physical_zip'))
    phone = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('phone'))
    email = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('email'))
    safety_rating = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('safety_rating'))
    total_power_units = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('total_power_units'))
    total_drivers = factory.LazyFunction(lambda: get_test_data('usdot_profile', 'default').get('total_drivers'))


# ============================================================================
# Asset Factories
# ============================================================================

class VehicleFactory(DjangoModelFactory):
    """Factory for creating Vehicle instances."""

    class Meta:
        model = Vehicle

    customer = factory.SubFactory(CustomerFactory)
    vin = factory.Sequence(lambda n: f"1HGCM82633A{100000 + n:06d}")
    unit_number = factory.LazyFunction(lambda: get_test_data('vehicle', 'default')['unit_number'])
    year = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('year'))
    make = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('make'))
    model = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('model'))
    license_plate = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('license_plate'))
    is_active = True
    odometer_miles = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('odometer_miles'))
    engine_hours = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('engine_hours'))
    capabilities = factory.LazyFunction(lambda: get_test_data('vehicle', 'default').get('capabilities', []))

    @classmethod
    def minimal(cls, **kwargs):
        """Create vehicle with minimal required fields (just VIN)."""
        data = get_test_data('vehicle', 'minimal')
        # Don't override VIN - let Sequence handle it
        data.pop('vin', None)
        return cls(**{**data, **kwargs})

    @classmethod
    def insulated_boom(cls, **kwargs):
        """Create vehicle with insulated boom tags."""
        data = get_test_data('vehicle', 'insulated_boom')
        # Don't override VIN - let Sequence handle it
        data.pop('vin', None)
        return cls(**{**data, **kwargs})


class VINDecodeDataFactory(DjangoModelFactory):
    """Factory for creating VINDecodeData instances."""

    class Meta:
        model = VINDecodeData

    vehicle = factory.SubFactory(VehicleFactory)
    vin = factory.LazyAttribute(lambda obj: obj.vehicle.vin)
    model_year = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['model_year'])
    make = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['make'])
    model = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['model'])
    manufacturer = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['manufacturer'])
    vehicle_type = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['vehicle_type'])
    body_class = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['body_class'])
    engine_model = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['engine_model'])
    engine_cylinders = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['engine_cylinders'])
    displacement_liters = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['displacement_liters'])
    fuel_type_primary = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['fuel_type_primary'])
    gvwr = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['gvwr'])
    gvwr_min_lbs = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['gvwr_min_lbs'])
    gvwr_max_lbs = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['gvwr_max_lbs'])
    error_code = factory.LazyFunction(lambda: get_test_data('vin_decode', 'default')['error_code'])
    raw_response = factory.LazyFunction(lambda: {})

    @classmethod
    def error_decode(cls, **kwargs):
        """Create decode data with error."""
        data = get_test_data('vin_decode', 'error')
        return cls(**{**data, **kwargs})


class EquipmentFactory(DjangoModelFactory):
    """Factory for creating Equipment instances."""

    class Meta:
        model = Equipment

    customer = factory.SubFactory(CustomerFactory)
    serial_number = factory.Sequence(lambda n: f"SN-TEST-{1000 + n}")
    asset_number = factory.LazyFunction(lambda: get_test_data('equipment', 'default')['asset_number'])
    equipment_type = factory.LazyFunction(lambda: get_test_data('equipment', 'default')['equipment_type'])
    manufacturer = factory.LazyFunction(lambda: get_test_data('equipment', 'default').get('manufacturer'))
    model = factory.LazyFunction(lambda: get_test_data('equipment', 'default').get('model'))
    year = factory.LazyFunction(lambda: get_test_data('equipment', 'default').get('year'))
    is_active = True
    capabilities = factory.LazyFunction(lambda: get_test_data('equipment', 'default').get('capabilities', []))

    @classmethod
    def minimal(cls, **kwargs):
        """Create equipment with minimal required fields."""
        data = get_test_data('equipment', 'minimal')
        # Don't override serial_number - let Sequence handle it
        data.pop('serial_number', None)
        return cls(**{**data, **kwargs})

    @classmethod
    def insulated_aerial(cls, **kwargs):
        """Create insulated aerial device with full equipment_data."""
        data = get_test_data('equipment', 'insulated_aerial')
        # Don't override serial_number - let Sequence handle it
        data.pop('serial_number', None)
        return cls(**{**data, **kwargs})


# ============================================================================
# Inspection Factories
# ============================================================================

class InspectionRunFactory(DjangoModelFactory):
    """Factory for creating InspectionRun instances."""

    class Meta:
        model = InspectionRun

    customer = factory.SubFactory(CustomerFactory)
    asset_type = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['asset_type'])
    asset_id = factory.LazyAttribute(lambda obj: EquipmentFactory(customer=obj.customer).id)
    template_key = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['template_key'])
    program_key = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['program_key'])
    status = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['status'])
    started_at = factory.LazyFunction(lambda: parse_test_datetime(get_test_data('inspection_run', 'default')['started_at']))
    finalized_at = None
    inspector_name = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['inspector_name'])
    inspector_signature = None
    template_snapshot = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['template_snapshot'])
    step_data = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['step_data'])
    notes = factory.LazyFunction(lambda: get_test_data('inspection_run', 'default')['notes'])

    @classmethod
    def in_progress(cls, **kwargs):
        """Create in-progress inspection run."""
        data = get_test_data('inspection_run', 'in_progress')
        data['started_at'] = parse_test_datetime(data['started_at'])
        return cls(**{**data, **kwargs})

    @classmethod
    def completed(cls, **kwargs):
        """Create completed inspection run."""
        data = get_test_data('inspection_run', 'completed')
        data['started_at'] = parse_test_datetime(data['started_at'])
        data['finalized_at'] = parse_test_datetime(data['finalized_at'])
        return cls(**{**data, **kwargs})

    @classmethod
    def for_vehicle(cls, **kwargs):
        """Create inspection run for a vehicle."""
        vehicle = kwargs.pop('vehicle', None)
        if not vehicle:
            customer = kwargs.get('customer') or CustomerFactory()
            vehicle = VehicleFactory(customer=customer)

        return cls(
            asset_type='VEHICLE',
            asset_id=vehicle.id,
            customer=vehicle.customer,
            **kwargs
        )

    @classmethod
    def for_equipment(cls, **kwargs):
        """Create inspection run for equipment."""
        equipment = kwargs.pop('equipment', None)
        if not equipment:
            customer = kwargs.get('customer') or CustomerFactory()
            equipment = EquipmentFactory(customer=customer)

        return cls(
            asset_type='EQUIPMENT',
            asset_id=equipment.id,
            customer=equipment.customer,
            **kwargs
        )


class InspectionDefectFactory(DjangoModelFactory):
    """Factory for creating InspectionDefect instances."""

    class Meta:
        model = InspectionDefect

    inspection_run = factory.SubFactory(InspectionRunFactory)
    module_key = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['module_key'])
    step_key = factory.Sequence(lambda n: f"{get_test_data('inspection_defect', 'critical')['step_key']}_{n}")
    rule_id = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['rule_id'])
    defect_identity = factory.LazyAttribute(
        lambda obj: InspectionDefect.generate_defect_identity(
            obj.inspection_run.id,
            obj.module_key,
            obj.step_key,
            obj.rule_id
        )
    )
    severity = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['severity'])
    status = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['status'])
    title = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['title'])
    description = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['description'])
    defect_details = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['defect_details'])
    evaluation_trace = factory.LazyFunction(lambda: get_test_data('inspection_defect', 'critical')['evaluation_trace'])

    @classmethod
    def major(cls, **kwargs):
        """Create major severity defect."""
        data = get_test_data('inspection_defect', 'major')
        return cls(**{**data, **kwargs})

    @classmethod
    def minor(cls, **kwargs):
        """Create minor severity defect."""
        data = get_test_data('inspection_defect', 'minor')
        return cls(**{**data, **kwargs})

    @classmethod
    def critical(cls, **kwargs):
        """Create critical severity defect."""
        data = get_test_data('inspection_defect', 'critical')
        return cls(**{**data, **kwargs})


# ============================================================================
# Work Order Factories
# ============================================================================

class WorkOrderFactory(DjangoModelFactory):
    """Factory for creating WorkOrder instances."""

    class Meta:
        model = WorkOrder

    # work_order_number is auto-generated by model
    work_order_number = None
    customer = factory.SubFactory(CustomerFactory)
    asset_type = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['asset_type'])
    asset_id = factory.LazyAttribute(lambda obj: EquipmentFactory(customer=obj.customer).id)
    status = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['status'])
    priority = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['priority'])
    source_type = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['source_type'])
    source_id = None
    description = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['description'])
    scheduled_date = None
    assigned_to = None
    started_at = None
    completed_at = None
    odometer_at_service = None
    engine_hours_at_service = None
    notes = factory.LazyFunction(lambda: get_test_data('work_order', 'default')['notes'])

    @classmethod
    def scheduled(cls, **kwargs):
        """Create scheduled work order."""
        data = get_test_data('work_order', 'scheduled')
        if 'scheduled_date' in data and isinstance(data['scheduled_date'], str):
            data['scheduled_date'] = datetime.fromisoformat(data['scheduled_date']).date()
        return cls(**{**data, **kwargs})

    @classmethod
    def completed(cls, **kwargs):
        """Create completed work order."""
        data = get_test_data('work_order', 'completed')
        if 'scheduled_date' in data and isinstance(data['scheduled_date'], str):
            data['scheduled_date'] = datetime.fromisoformat(data['scheduled_date']).date()
        if 'started_at' in data and isinstance(data['started_at'], str):
            data['started_at'] = parse_test_datetime(data['started_at'])
        if 'completed_at' in data and isinstance(data['completed_at'], str):
            data['completed_at'] = parse_test_datetime(data['completed_at'])
        return cls(**{**data, **kwargs})

    @classmethod
    def customer_request(cls, **kwargs):
        """Create customer request work order."""
        data = get_test_data('work_order', 'customer_request')
        return cls(**{**data, **kwargs})

    @classmethod
    def from_inspection(cls, inspection_run=None, **kwargs):
        """Create work order from an inspection."""
        if not inspection_run:
            inspection_run = InspectionRunFactory()

        return cls(
            customer=inspection_run.customer,
            asset_type=inspection_run.asset_type,
            asset_id=inspection_run.asset_id,
            source_type='INSPECTION_DEFECT',
            source_id=inspection_run.id,
            **kwargs
        )

    @classmethod
    def for_vehicle(cls, **kwargs):
        """Create work order for a vehicle."""
        vehicle = kwargs.pop('vehicle', None)
        if not vehicle:
            customer = kwargs.get('customer') or CustomerFactory()
            vehicle = VehicleFactory(customer=customer)

        return cls(
            asset_type='VEHICLE',
            asset_id=vehicle.id,
            customer=vehicle.customer,
            **kwargs
        )

    @classmethod
    def for_equipment(cls, **kwargs):
        """Create work order for equipment."""
        equipment = kwargs.pop('equipment', None)
        if not equipment:
            customer = kwargs.get('customer') or CustomerFactory()
            equipment = EquipmentFactory(customer=customer)

        return cls(
            asset_type='EQUIPMENT',
            asset_id=equipment.id,
            customer=equipment.customer,
            **kwargs
        )


class WorkOrderDefectFactory(DjangoModelFactory):
    """
    Factory for creating WorkOrderDefect junction instances.

    IMPORTANT: By default, this creates independent work_order and defect with DIFFERENT customers,
    which will fail validation. Use create_for_work_order() or pass matching objects.
    """

    class Meta:
        model = WorkOrderDefect

    work_order = factory.SubFactory(WorkOrderFactory)
    defect = factory.SubFactory(InspectionDefectFactory)

    @classmethod
    def create_for_work_order(cls, work_order=None, defect=None, **kwargs):
        """Create WorkOrderDefect with matching customer and asset."""
        if work_order is None and defect is None:
            # Create both
            work_order = WorkOrderFactory()
            customer = work_order.customer
            inspection_run = InspectionRunFactory(
                customer=customer,
                asset_type=work_order.asset_type,
                asset_id=work_order.asset_id
            )
            defect = InspectionDefectFactory(inspection_run=inspection_run)
        elif work_order is None:
            # Create work_order for existing defect
            work_order = WorkOrderFactory(
                customer=defect.inspection_run.customer,
                asset_type=defect.inspection_run.asset_type,
                asset_id=defect.inspection_run.asset_id
            )
        elif defect is None:
            # Create defect for existing work_order
            customer = work_order.customer
            inspection_run = InspectionRunFactory(
                customer=customer,
                asset_type=work_order.asset_type,
                asset_id=work_order.asset_id
            )
            defect = InspectionDefectFactory(inspection_run=inspection_run)
        # else: both provided, use them as-is

        return cls(work_order=work_order, defect=defect, **kwargs)


# ============================================================================
# ORGANIZATION FACTORIES
# ============================================================================

class CompanyFactory(DjangoModelFactory):
    """Factory for creating Company instances."""

    class Meta:
        model = Company

    name = factory.LazyFunction(lambda: get_test_data('company', 'default')['name'])
    dba_name = factory.LazyFunction(lambda: get_test_data('company', 'default')['dba_name'])
    phone = factory.LazyFunction(lambda: get_test_data('company', 'default')['phone'])
    email = factory.LazyFunction(lambda: get_test_data('company', 'default')['email'])
    website = factory.LazyFunction(lambda: get_test_data('company', 'default')['website'])
    address_line1 = factory.LazyFunction(lambda: get_test_data('company', 'default')['address_line1'])
    address_line2 = factory.LazyFunction(lambda: get_test_data('company', 'default')['address_line2'])
    city = factory.LazyFunction(lambda: get_test_data('company', 'default')['city'])
    state = factory.LazyFunction(lambda: get_test_data('company', 'default')['state'])
    zip_code = factory.LazyFunction(lambda: get_test_data('company', 'default')['zip_code'])
    tax_id = factory.LazyFunction(lambda: get_test_data('company', 'default')['tax_id'])
    usdot_number = factory.LazyFunction(lambda: get_test_data('company', 'default')['usdot_number'])
    settings = factory.LazyFunction(lambda: get_test_data('company', 'default')['settings'])

    @classmethod
    def minimal(cls, **kwargs):
        """Create company with minimal required fields."""
        data = get_test_data('company', 'minimal')
        # Clear all fields and only set minimal ones
        return cls(
            name=data['name'],
            dba_name='',
            phone='',
            email='',
            website='',
            address_line1='',
            address_line2='',
            city='',
            state='',
            zip_code='',
            tax_id='',
            usdot_number='',
            settings={},
            **kwargs
        )


class DepartmentFactory(DjangoModelFactory):
    """Factory for creating Department instances."""

    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"{get_test_data('department', 'default')['name']} {n}")
    code = factory.Sequence(lambda n: f"D{n:03d}")  # Unique codes
    description = factory.LazyFunction(lambda: get_test_data('department', 'default')['description'])
    is_active = factory.LazyFunction(lambda: get_test_data('department', 'default')['is_active'])
    allows_floating = factory.LazyFunction(lambda: get_test_data('department', 'default')['allows_floating'])
    manager = None  # Set after employees are created if needed

    @classmethod
    def inspection(cls, **kwargs):
        """Create inspection department."""
        data = get_test_data('department', 'inspection')
        data.pop('code', None)  # Let Sequence handle it
        return cls(**{**data, **kwargs})

    @classmethod
    def parts(cls, **kwargs):
        """Create parts department."""
        data = get_test_data('department', 'parts')
        data.pop('code', None)  # Let Sequence handle it
        return cls(**{**data, **kwargs})

    @classmethod
    def minimal(cls, **kwargs):
        """Create department with minimal required fields."""
        data = get_test_data('department', 'minimal')
        data.pop('code', None)  # Let Sequence handle it
        return cls(**{**data, **kwargs})


class EmployeeFactory(DjangoModelFactory):
    """Factory for creating Employee instances."""

    class Meta:
        model = Employee

    base_department = factory.SubFactory(DepartmentFactory)
    employee_number = factory.Sequence(lambda n: f"E{n:04d}")
    first_name = factory.LazyFunction(lambda: get_test_data('employee', 'default')['first_name'])
    last_name = factory.LazyFunction(lambda: get_test_data('employee', 'default')['last_name'])
    email = factory.LazyFunction(lambda: get_test_data('employee', 'default')['email'])
    phone = factory.LazyFunction(lambda: get_test_data('employee', 'default')['phone'])
    title = factory.LazyFunction(lambda: get_test_data('employee', 'default')['title'])
    is_active = factory.LazyFunction(lambda: get_test_data('employee', 'default')['is_active'])
    certifications = factory.LazyFunction(lambda: get_test_data('employee', 'default')['certifications'])
    skills = factory.LazyFunction(lambda: get_test_data('employee', 'default')['skills'])
    settings = factory.LazyFunction(lambda: get_test_data('employee', 'default')['settings'])
    user = None  # Optional
    hire_date = None
    termination_date = None

    @classmethod
    def inspector(cls, **kwargs):
        """Create inspector employee."""
        data = get_test_data('employee', 'inspector')
        data.pop('employee_number', None)  # Let Sequence handle it
        return cls(**{**data, **kwargs})

    @classmethod
    def minimal(cls, **kwargs):
        """Create employee with minimal required fields."""
        data = get_test_data('employee', 'minimal')
        data.pop('employee_number', None)  # Let Sequence handle it
        return cls(**{**data, **kwargs})
