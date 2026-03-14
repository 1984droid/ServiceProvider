# Team Management & User-Person Architecture Plan

## Current Architecture Analysis

### Existing Models

1. **Django User** - Authentication/login accounts
   - Username, email, password, permissions
   - NO personal info (first_name, last_name only)

2. **Employee** (apps/organization/models.py)
   - Internal team members
   - Has `user = OneToOneField(User)` (optional)
   - Contains: name, phone, email, department, certifications, etc.
   - Can exist WITHOUT a user account (not all employees need login)

3. **Contact** (apps/customers/models.py)
   - Customer contacts (external people)
   - Currently NO user field
   - Contains: name, phone, email, customer relationship, correspondence prefs

## ✅ Design Principle: Every User MUST Attach to a Person

**Rule:** A Django User account cannot exist in isolation - it must be linked to either:
- An **Employee** (internal team member), OR
- A **Contact** (customer portal user)

**Never:** A standalone User without a person attached

---

## Implementation Plan

### Phase 1: Add User Link to Contact Model

**Goal:** Enable customer portal access for contacts

```python
# apps/customers/models.py - Contact model

user = models.OneToOneField(
    'auth.User',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='contact',
    help_text="Portal user account (if contact has portal access)"
)

# Add portal access flag
has_portal_access = models.BooleanField(
    default=False,
    help_text="Whether contact has portal access"
)
```

**Benefits:**
- Customers can log in to view their inspections, invoices, work orders
- Maintains separation between internal/external users
- One Contact = One User (optional)

---

### Phase 2: Enforce User-Person Relationship

**At User Creation:**

```python
# Custom user creation - must specify person_type and person_id
{
  "username": "jsmith",
  "password": "...",
  "person_type": "employee",  # or "contact"
  "person_id": "uuid-of-employee-or-contact"
}
```

**Validation:**
- Every User must have EITHER `employee` OR `contact` relationship
- Cannot have both
- Cannot have neither

**User Profile Endpoint:**
```python
# GET /api/auth/me/
{
  "id": "...",
  "username": "jsmith",
  "email": "john.smith@company.com",
  "person_type": "employee",  # or "contact"
  "employee": {
    "id": "...",
    "full_name": "John Smith",
    "employee_number": "EMP001",
    "department": "Service",
    "certifications": [...]
  },
  # OR
  "contact": {
    "id": "...",
    "full_name": "Jane Doe",
    "customer": {
      "id": "...",
      "name": "ABC Corp"
    },
    "has_portal_access": true
  }
}
```

---

### Phase 3: Team Management Backend

**New Endpoints:**

```
# Employee Management
GET    /api/organization/employees/          # List all employees
POST   /api/organization/employees/          # Create employee
GET    /api/organization/employees/{id}/     # Employee detail
PATCH  /api/organization/employees/{id}/     # Update employee
DELETE /api/organization/employees/{id}/     # Deactivate employee

POST   /api/organization/employees/{id}/create_user/     # Create login for employee
DELETE /api/organization/employees/{id}/remove_user/     # Remove login access

# Contact Portal Management
GET    /api/customers/contacts/              # List contacts (with portal access filter)
PATCH  /api/customers/contacts/{id}/grant_portal_access/   # Create portal login
PATCH  /api/customers/contacts/{id}/revoke_portal_access/  # Remove portal login

# Team Overview (for managers)
GET    /api/organization/team/               # All employees with user access status
GET    /api/customers/portal_users/          # All contacts with portal access
```

**Permissions:**
- Admin/Manager: Full access to team management
- Employee: Can view team members, cannot manage
- Contact: Cannot access team management

---

### Phase 4: Team Management Frontend

**Navigation Structure:**
```
Management
├── Customers
└── Team (NEW)
    ├── Employees
    │   ├── List (name, department, has login, certifications)
    │   ├── Create/Edit Employee
    │   └── Manage User Access (create/remove login)
    └── Portal Users (customer contacts with portal access)
        ├── List
        └── Manage Access
```

**Employee List Page Features:**
- Table: Name, Employee #, Department, Title, Has Login, Active
- Filters: Department, Has Login (Yes/No), Active Status
- Actions: Create Employee, Edit, Grant/Revoke Login
- Bulk actions: Import employees, Export list

**Employee Detail/Edit:**
```
Basic Info:
- First Name, Last Name
- Employee Number
- Email, Phone
- Department, Title
- Hire Date

Certifications:
- Add Certification
  - Standard (dropdown: ANSI A92.2, A92.5, etc.)
  - Cert Number
  - Expiry Date
  - Issued By
- List existing certifications with expiry warnings

User Access:
- Has User Account: [Yes/No]
- If Yes:
  - Username: [display]
  - Last Login: [timestamp]
  - [Revoke Access] button
- If No:
  - [Grant Portal Access] button
  - Creates User with auto-generated username/password
```

**Contact Portal Management:**
- In Customer Detail → Contacts tab
- Add "Portal Access" column
- Toggle portal access per contact
- When granted: auto-creates User account, sends welcome email

---

### Phase 5: Authentication & Authorization

**Login Flow:**

1. User enters username/password
2. System authenticates
3. Determines person_type (employee or contact)
4. Loads appropriate profile
5. Redirects to appropriate dashboard:
   - Employee → Main dashboard (full access)
   - Contact → Customer portal (limited to their customer's data)

**Permission Classes:**

```python
class IsEmployee(BasePermission):
    """User must be linked to an Employee."""
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee') and request.user.employee is not None

class IsContact(BasePermission):
    """User must be linked to a Contact."""
    def has_permission(self, request, view):
        return hasattr(request.user, 'contact') and request.user.contact is not None

class CanAccessCustomerData(BasePermission):
    """Contact can only access their own customer's data."""
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'contact'):
            return obj.customer_id == request.user.contact.customer_id
        return True  # Employees have access to all
```

**Views Protection:**
```python
# Employees only
class InspectionViewSet:
    permission_classes = [IsAuthenticated, IsEmployee]

# Contacts can view their own data
class CustomerInspectionViewSet:
    permission_classes = [IsAuthenticated, IsContact, CanAccessCustomerData]
```

---

## Implementation Priority

### ✅ Immediate (Week 1)
1. Add `user` field to Contact model
2. Add `has_portal_access` to Contact
3. Migration
4. Update UserProfileSerializer to include person_type
5. Create team management endpoints (basic CRUD)

### 🔄 Short-term (Week 2)
6. Build Employee List page (frontend)
7. Build Employee Create/Edit forms
8. Implement Grant/Revoke User Access
9. Add certification management UI

### 📋 Medium-term (Week 3-4)
10. Build Contact Portal Access management
11. Create customer portal dashboard (limited view)
12. Implement permission classes for data isolation
13. Add user invitation/welcome emails

### 🎯 Future Enhancements
- Team scheduling/availability
- Certification expiry notifications
- Skill-based work assignment
- Time tracking integration
- Performance metrics per employee
- Customer portal features (view inspections, request service, pay invoices)

---

## Data Migration Strategy

**Existing Users:**
All current users are already linked to Employees (from setup), so:
1. Add Contact.user field (no data migration needed initially)
2. Future contacts can be granted portal access as needed

**No Breaking Changes:**
- Employee.user remains optional (not all employees need login)
- Contact.user remains optional (not all contacts need portal)
- Existing Employee-User links continue working

---

## Security Considerations

1. **Password Requirements:** Enforce strong passwords for all user types
2. **Session Management:** Different session timeouts for employee vs contact
3. **2FA:** Optional for employees, required for contacts accessing sensitive data
4. **Audit Log:** Track all user access grants/revocations
5. **Data Isolation:** Contacts can ONLY see their customer's data
6. **IP Restrictions:** Optional IP whitelist for customer portal access

---

## User Experience

**For Employees:**
- Single dashboard with full system access
- See all customers, inspections, work orders
- Manage team members (if admin)

**For Contacts (Customer Portal):**
- Limited dashboard showing only their data
- View inspections for their equipment
- View work orders and invoices
- Request new service
- Update contact preferences
- No access to other customers' data

---

## Benefits

✅ **Clear Separation:** Internal team vs external customers
✅ **Flexibility:** Not all employees/contacts need login
✅ **Security:** Data isolation between customers
✅ **Scalability:** Easy to add more person types (vendors, subcontractors)
✅ **Audit Trail:** Know who has access and when
✅ **Customer Self-Service:** Reduce support burden with portal
✅ **Compliance:** Control who can see what data

---

## Next Steps

1. **Review this plan** - Does it align with business requirements?
2. **Approve data model changes** - Contact.user field addition
3. **Prioritize features** - Which phase to start with?
4. **UI mockups** - Review employee management screens
5. **Begin implementation** - Start with backend models and migrations
