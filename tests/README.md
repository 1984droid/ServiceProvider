# Test Suite Documentation

## Overview

This test suite follows a **configuration-driven testing pattern** where **NO VALUES ARE HARDCODED** in test files. All test data, validation rules, error messages, and constraints are centralized in `tests/config.py`.

## Architecture

### Core Principles

1. **Single Source of Truth**: All test data lives in `tests/config.py`
2. **Factory Pattern**: Use factories (not direct model creation) for consistency
3. **Fixture-Based**: Leverage pytest fixtures for common test setups
4. **Scalable**: Add new fields/models by updating config only

### Directory Structure

```
tests/
├── __init__.py              # Package marker
├── README.md                # This file
├── config.py                # ALL test data and configuration
├── conftest.py              # Pytest fixtures
├── factories.py             # Factory classes for model creation
├── test_customer_models.py  # Customer/Contact/USDOTProfile tests
└── test_asset_models.py     # Vehicle/Equipment/VINDecodeData tests
```

## Key Files

### tests/config.py

**Purpose**: Central configuration for ALL test data.

**Contains**:
- `CUSTOMER_DATA` - Customer test data with variants (default, minimal, with_usdot)
- `CONTACT_DATA` - Contact test data with variants
- `VEHICLE_DATA` - Vehicle test data with variants
- `EQUIPMENT_DATA` - Equipment test data with variants
- `VIN_DECODE_DATA` - VIN decode test data
- `USDOT_PROFILE_DATA` - USDOT profile test data
- `VALID_CHOICES` - All choice field options (states, equipment types, etc.)
- `TEST_VINS` - List of valid test VINs
- `TEST_SERIAL_NUMBERS` - List of valid test serial numbers
- `API_CONFIG` - API endpoint configuration
- `VALIDATION_RULES` - Model validation rules
- `CONSTRAINTS` - Field constraints (max lengths, min/max values)
- `TEST_USERS` - Test user credentials
- `ERROR_MESSAGES` - Expected error messages

**Helper Functions**:
```python
get_test_data(model_name, variant='default')  # Get test data for a model
get_next_test_vin()                           # Get next unique test VIN
get_next_test_serial()                        # Get next unique serial number
```

### tests/conftest.py

**Purpose**: Pytest configuration and reusable fixtures.

**Fixture Categories**:

1. **User Fixtures**:
   - `admin_user` - Superuser for testing
   - `regular_user` - Regular user for testing

2. **API Client Fixtures**:
   - `api_client` - Unauthenticated DRF client
   - `admin_api_client` - Authenticated admin client
   - `user_api_client` - Authenticated regular user client

3. **Model Fixtures**:
   - `customer` - Single customer (default variant)
   - `customer_minimal` - Minimal customer
   - `contact` - Single contact
   - `vehicle` - Single vehicle
   - `equipment` - Single equipment

4. **Collection Fixtures**:
   - `customer_with_contacts` - Customer with 3 contacts, one primary
   - `customer_with_fleet` - Customer with vehicles and equipment
   - `complete_customer` - Fully populated customer (contacts, vehicles, equipment, USDOT)

5. **Utility Fixtures**:
   - `vin_tracker` - Prevent duplicate VINs in a test
   - `serial_tracker` - Prevent duplicate serials in a test

### tests/factories.py

**Purpose**: Factory classes using factory_boy pattern.

**Pattern**:
```python
class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    # ALL values from config - NO HARDCODING
    name = factory.LazyFunction(lambda: get_test_data('customer', 'default')['name'])
    city = factory.LazyFunction(lambda: get_test_data('customer', 'default').get('city'))

    @classmethod
    def minimal(cls, **kwargs):
        """Create customer with minimal required fields."""
        data = get_test_data('customer', 'minimal')
        return cls(**{**data, **kwargs})
```

**Available Factories**:
- `CustomerFactory` - Variants: `minimal()`, `with_usdot()`
- `ContactFactory` - Variants: `minimal()`, `automated()`
- `USDOTProfileFactory`
- `VehicleFactory` - Variants: `minimal()`, `insulated_boom()`
- `EquipmentFactory` - Variants: `minimal()`, `insulated_aerial()`
- `VINDecodeDataFactory` - Variants: `error_decode()`

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_customer_models.py
pytest tests/test_asset_models.py
```

### Run Specific Test Class

```bash
pytest tests/test_customer_models.py::TestCustomerModel
```

### Run Specific Test

```bash
pytest tests/test_customer_models.py::TestCustomerModel::test_customer_creation_default
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=apps --cov-report=html
```

## Writing New Tests

### Example: Test Using Fixture

```python
import pytest
from tests.config import get_test_data

@pytest.mark.django_db
def test_customer_creation(customer):
    """Test customer creation using fixture."""
    default_data = get_test_data('customer', 'default')
    assert customer.name == default_data['name']
    assert customer.is_active is True
```

### Example: Test Using Factory

```python
import pytest
from tests.factories import CustomerFactory
from tests.config import get_test_data

@pytest.mark.django_db
def test_customer_minimal():
    """Test minimal customer creation."""
    customer = CustomerFactory.minimal()
    minimal_data = get_test_data('customer', 'minimal')
    assert customer.name == minimal_data['name']
```

### Example: Test Validation

```python
import pytest
from django.core.exceptions import ValidationError
from tests.factories import VehicleFactory
from tests.config import CONSTRAINTS

@pytest.mark.django_db
def test_vin_length():
    """Test VIN length validation."""
    exact_length = CONSTRAINTS['vehicle']['vin']['exact_length']

    with pytest.raises(ValidationError):
        vehicle = VehicleFactory(vin='SHORT')
        vehicle.full_clean()
```

### Example: Test Relationship

```python
import pytest
from tests.factories import VehicleFactory, EquipmentFactory

@pytest.mark.django_db
def test_vehicle_equipment_relationship():
    """Test vehicle can have mounted equipment."""
    vehicle = VehicleFactory()
    equipment = EquipmentFactory(mounted_on_vehicle=vehicle)
    assert equipment in vehicle.equipment.all()
```

## Adding New Test Data

When adding new fields or models:

1. **Update tests/config.py**:
   ```python
   NEW_MODEL_DATA = {
       'default': {
           'field1': 'value1',
           'field2': 'value2',
       },
       'minimal': {
           'field1': 'value1',
       },
   }
   ```

2. **Update data_map in get_test_data()**:
   ```python
   data_map = {
       'customer': CUSTOMER_DATA,
       'new_model': NEW_MODEL_DATA,  # Add here
   }
   ```

3. **Create Factory in tests/factories.py**:
   ```python
   class NewModelFactory(DjangoModelFactory):
       class Meta:
           model = NewModel

       field1 = factory.LazyFunction(lambda: get_test_data('new_model', 'default')['field1'])
   ```

4. **Add Fixture in tests/conftest.py** (if needed):
   ```python
   @pytest.fixture
   def new_model(db):
       return NewModelFactory()
   ```

5. **Write Tests**:
   ```python
   def test_new_model_creation(new_model):
       default_data = get_test_data('new_model', 'default')
       assert new_model.field1 == default_data['field1']
   ```

## Best Practices

### DO:
✅ Use fixtures for common test setups
✅ Use factories for creating test data
✅ Pull ALL values from `tests/config.py`
✅ Use `get_test_data()` to access config
✅ Use constraints from `CONSTRAINTS` dict
✅ Use `@pytest.mark.django_db` for database tests
✅ Test both success and failure cases
✅ Test model validation and constraints

### DON'T:
❌ Hardcode test data in test files
❌ Create models directly (use factories)
❌ Duplicate test data across files
❌ Hardcode error messages (use ERROR_MESSAGES)
❌ Hardcode constraints (use CONSTRAINTS)
❌ Skip validation tests
❌ Test implementation details

## Configuration-Driven Philosophy

**Problem**: Hardcoded test data becomes stale and scattered.

**Solution**: Single source of truth in `tests/config.py`.

### Before (Bad):
```python
def test_customer():
    customer = Customer.objects.create(
        name='Acme Corp',  # HARDCODED
        city='Springfield',  # HARDCODED
    )
```

### After (Good):
```python
def test_customer():
    customer = CustomerFactory()
    default_data = get_test_data('customer', 'default')
    assert customer.name == default_data['name']
```

**Benefits**:
- Update one place when data structure changes
- Consistent test data across all tests
- Easy to add variants (minimal, special cases)
- Self-documenting what fields are required
- Tests grow naturally with application

## Test Coverage Goals

- **Models**: 100% of model logic, validation, relationships
- **APIs**: All endpoints, status codes, permissions
- **Business Logic**: All service layer functions
- **Edge Cases**: Boundary conditions, error handling

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pytest --cov=apps --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

Ensure Django settings are configured:
```bash
export DJANGO_SETTINGS_MODULE=config.settings
```

Or use pytest.ini:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
```

### Database Errors

Tests use `@pytest.mark.django_db` to enable database access. Make sure:
1. Marker is present on test functions
2. Test database can be created
3. Migrations are up to date

### Factory Errors

If factories fail:
1. Check config data is complete
2. Verify all required fields have values
3. Check for unique constraint violations

## Next Steps

1. Add API endpoint tests
2. Add integration tests
3. Add performance tests
4. Configure CI/CD pipeline
5. Add coverage reporting
