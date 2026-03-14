"""
DRF ViewSets for Customer Management

Provides REST API endpoints for:
- Customer CRUD with filtering, search, and ordering
- Contact CRUD with customer-specific filtering
- USDOTProfile management
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .models import Customer, Contact, USDOTProfile
from .serializers import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateSerializer,
    ContactListSerializer,
    ContactDetailSerializer,
    USDOTProfileSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer management

    Endpoints:
    - GET /api/customers/ - List all customers (paginated)
    - POST /api/customers/ - Create new customer
    - GET /api/customers/{id}/ - Retrieve customer details
    - PUT/PATCH /api/customers/{id}/ - Update customer
    - DELETE /api/customers/{id}/ - Delete customer (soft delete via is_active=False recommended)

    Filtering:
    - ?is_active=true/false
    - ?state=CA
    - ?has_usdot=true/false
    - ?has_mc=true/false

    Search:
    - ?search=company+name

    Ordering:
    - ?ordering=name
    - ?ordering=-created_at

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Customer.objects.all().select_related('primary_contact').prefetch_related('contacts')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'state']
    search_fields = ['name', 'legal_name', 'usdot_number', 'mc_number', 'city']
    ordering_fields = ['name', 'created_at', 'city', 'state']
    ordering = ['name']

    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'create':
            return CustomerCreateSerializer
        return CustomerDetailSerializer

    def perform_create(self, serializer):
        """
        Create customer and link to existing USDOTProfile if available.
        """
        customer = serializer.save()

        # Link to existing USDOTProfile if customer has USDOT number
        if customer.usdot_number:
            clean_usdot = ''.join(c for c in customer.usdot_number if c.isalnum())
            try:
                profile = USDOTProfile.objects.get(usdot_number=clean_usdot, customer__isnull=True)
                profile.customer = customer
                profile.save(update_fields=['customer', 'updated_at'])
            except USDOTProfile.DoesNotExist:
                pass  # No profile exists, that's okay
            except USDOTProfile.MultipleObjectsReturned:
                # If multiple unlinked profiles exist, link the most recent one
                profile = USDOTProfile.objects.filter(
                    usdot_number=clean_usdot,
                    customer__isnull=True
                ).order_by('-lookup_date').first()
                if profile:
                    profile.customer = customer
                    profile.save(update_fields=['customer', 'updated_at'])

    def get_queryset(self):
        """
        Optionally filter by custom query params:
        - has_usdot: filter customers with/without USDOT number
        - has_mc: filter customers with/without MC number
        - has_contacts: filter customers with/without contacts
        """
        queryset = super().get_queryset()

        # Filter by USDOT presence
        has_usdot = self.request.query_params.get('has_usdot')
        if has_usdot is not None:
            if has_usdot.lower() == 'true':
                queryset = queryset.exclude(Q(usdot_number__isnull=True) | Q(usdot_number=''))
            else:
                queryset = queryset.filter(Q(usdot_number__isnull=True) | Q(usdot_number=''))

        # Filter by MC number presence
        has_mc = self.request.query_params.get('has_mc')
        if has_mc is not None:
            if has_mc.lower() == 'true':
                queryset = queryset.exclude(Q(mc_number__isnull=True) | Q(mc_number=''))
            else:
                queryset = queryset.filter(Q(mc_number__isnull=True) | Q(mc_number=''))

        # Filter by contact presence
        has_contacts = self.request.query_params.get('has_contacts')
        if has_contacts is not None:
            queryset = queryset.annotate(contact_count=Count('contacts'))
            if has_contacts.lower() == 'true':
                queryset = queryset.filter(contact_count__gt=0)
            else:
                queryset = queryset.filter(contact_count=0)

        return queryset

    def perform_destroy(self, instance):
        """
        Soft delete: set is_active=False instead of hard delete
        To hard delete, use force_delete query param
        """
        force_delete = self.request.query_params.get('force_delete', 'false').lower() == 'true'

        if force_delete:
            instance.delete()
        else:
            instance.is_active = False
            instance.save(update_fields=['is_active', 'updated_at'])

    @action(detail=True, methods=['post'])
    def set_primary_contact(self, request, pk=None):
        """
        Set primary contact for customer
        POST /api/customers/{id}/set_primary_contact/
        Body: {"contact_id": "uuid"}
        """
        customer = self.get_object()
        contact_id = request.data.get('contact_id')

        if not contact_id:
            return Response(
                {'error': 'contact_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            contact = Contact.objects.get(id=contact_id, customer=customer)
            customer.primary_contact = contact
            customer.save(update_fields=['primary_contact', 'updated_at'])

            serializer = self.get_serializer(customer)
            return Response(serializer.data)

        except Contact.DoesNotExist:
            return Response(
                {'error': 'Contact not found or does not belong to this customer'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """
        Get all contacts for a customer
        GET /api/customers/{id}/contacts/
        """
        customer = self.get_object()
        contacts = customer.contacts.all().order_by('-is_active', 'last_name', 'first_name')

        # Apply filtering
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            contacts = contacts.filter(is_active=is_active.lower() == 'true')

        serializer = ContactListSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_by_usdot(self, request):
        """
        Search customer by USDOT number
        GET /api/customers/search_by_usdot/?usdot=123456
        """
        usdot = request.query_params.get('usdot')
        if not usdot:
            return Response(
                {'error': 'usdot parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean USDOT number
        clean_usdot = ''.join(c for c in usdot if c.isalnum())

        try:
            customer = Customer.objects.get(usdot_number=clean_usdot)
            serializer = CustomerDetailSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(
                {'error': f'Customer with USDOT {clean_usdot} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Customer.MultipleObjectsReturned:
            return Response(
                {'error': f'Multiple customers found with USDOT {clean_usdot}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contact management

    Endpoints:
    - GET /api/contacts/ - List all contacts (paginated)
    - POST /api/contacts/ - Create new contact
    - GET /api/contacts/{id}/ - Retrieve contact details
    - PUT/PATCH /api/contacts/{id}/ - Update contact
    - DELETE /api/contacts/{id}/ - Delete contact

    Filtering:
    - ?is_active=true/false
    - ?is_automated=true/false
    - ?customer={customer_id}

    Search:
    - ?search=john+doe

    Ordering:
    - ?ordering=last_name
    - ?ordering=-created_at

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Contact.objects.all().select_related('customer')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_automated', 'customer']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'customer__name']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'email']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        """Use lightweight serializer for list, full for detail"""
        if self.action == 'list':
            return ContactListSerializer
        return ContactDetailSerializer

    def get_queryset(self):
        """
        Optionally filter by:
        - primary: show only primary contacts
        - has_email: filter contacts with/without email
        """
        queryset = super().get_queryset()

        # Filter for primary contacts only
        show_primary = self.request.query_params.get('primary')
        if show_primary and show_primary.lower() == 'true':
            # Get all customer IDs where this contact is primary
            from django.db.models import OuterRef, Exists
            primary_contacts = Customer.objects.filter(
                primary_contact_id=OuterRef('id')
            )
            queryset = queryset.annotate(
                is_primary_contact=Exists(primary_contacts)
            ).filter(is_primary_contact=True)

        # Filter by email presence
        has_email = self.request.query_params.get('has_email')
        if has_email is not None:
            if has_email.lower() == 'true':
                queryset = queryset.exclude(Q(email__isnull=True) | Q(email=''))
            else:
                queryset = queryset.filter(Q(email__isnull=True) | Q(email=''))

        return queryset

    @action(detail=True, methods=['post'])
    def make_primary(self, request, pk=None):
        """
        Make this contact the primary contact for its customer
        POST /api/contacts/{id}/make_primary/
        """
        contact = self.get_object()
        customer = contact.customer

        customer.primary_contact = contact
        customer.save(update_fields=['primary_contact', 'updated_at'])

        serializer = self.get_serializer(contact)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_user(self, request, pk=None):
        """
        Create a user account for this contact (customer portal access).

        Request body:
            username (optional): If not provided, auto-generates from email or contact name
            password (optional): If not provided, generates random password
            send_email (optional, default=True): Whether to send welcome email

        Returns user account info and temporary password if generated.
        """
        from django.contrib.auth import get_user_model
        from django.db import transaction
        import secrets
        import string

        User = get_user_model()
        contact = self.get_object()

        # Check if contact already has a user
        if contact.user:
            return Response(
                {'error': 'Contact already has a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or generate username
        username = request.data.get('username')
        if not username:
            # Auto-generate from email or contact name
            if contact.email:
                username = contact.email.split('@')[0]
            else:
                username = f"{contact.first_name.lower()}{contact.last_name.lower()}"

            # Ensure uniqueness
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': f'Username "{username}" already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or generate password
        password = request.data.get('password')
        temp_password = None
        if not password:
            # Generate random password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(12))
            temp_password = password

        # Create user and link to contact
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                email=contact.email or '',
                first_name=contact.first_name,
                last_name=contact.last_name,
            )

            contact.user = user
            contact.save(update_fields=['user', 'updated_at'])

        response_data = {
            'message': f'User account created for {contact.full_name}',
            'contact_id': str(contact.id),
            'username': username,
        }

        if temp_password:
            response_data['temporary_password'] = temp_password
            response_data['password_note'] = 'This password is shown only once. Please save it securely.'

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def revoke_user(self, request, pk=None):
        """
        Revoke user account access for this contact (customer portal access).

        This deactivates the user account but preserves the contact record.
        The user link is removed so a new account could be created later if needed.

        Request body:
            delete_user (optional, default=False): If true, deletes the user account entirely
        """
        from django.contrib.auth import get_user_model
        from django.db import transaction

        User = get_user_model()
        contact = self.get_object()

        if not contact.user:
            return Response(
                {'error': 'Contact does not have a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = contact.user
        delete_user = request.data.get('delete_user', False)

        with transaction.atomic():
            if delete_user:
                # Completely delete the user account
                username = user.username
                contact.user = None
                contact.save(update_fields=['user', 'updated_at'])
                user.delete()

                return Response({
                    'message': f'User account "{username}" has been deleted',
                    'contact_id': str(contact.id),
                })
            else:
                # Deactivate user and unlink from contact
                user.is_active = False
                user.save(update_fields=['is_active'])

                contact.user = None
                contact.save(update_fields=['user', 'updated_at'])

                return Response({
                    'message': f'User account "{user.username}" has been revoked (deactivated and unlinked)',
                    'contact_id': str(contact.id),
                })


class USDOTProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for USDOT Profile management

    Endpoints:
    - GET /api/usdot-profiles/ - List all profiles
    - POST /api/usdot-profiles/ - Create new profile (after FMCSA lookup)
    - GET /api/usdot-profiles/{id}/ - Retrieve profile
    - PUT/PATCH /api/usdot-profiles/{id}/ - Update profile
    - DELETE /api/usdot-profiles/{id}/ - Delete profile

    Filtering:
    - ?customer={customer_id}
    - ?safety_rating=SATISFACTORY

    Search:
    - ?search=legal+name

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = USDOTProfile.objects.all().select_related('customer')
    serializer_class = USDOTProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'safety_rating']
    search_fields = ['usdot_number', 'mc_number', 'legal_name', 'dba_name']
    ordering_fields = ['created_at', 'legal_name', 'safety_rating_date']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def lookup_by_usdot(self, request):
        """
        Lookup USDOT profile by USDOT number.
        Checks cache first, then fetches from FMCSA API if not found.
        GET /api/usdot-profiles/lookup_by_usdot/?usdot=123456&force_refresh=false&customer_id=uuid
        """
        from apps.customers.services import FMCSAService
        import requests

        usdot = request.query_params.get('usdot')
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        customer_id = request.query_params.get('customer_id')

        if not usdot:
            return Response(
                {'error': 'usdot parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = FMCSAService()
            profile = service.lookup_by_usdot(usdot, force_refresh=force_refresh)

            # If customer_id is provided, link the profile to the customer
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id)
                    profile.customer = customer
                    profile.save(update_fields=['customer', 'updated_at'])
                except Customer.DoesNotExist:
                    return Response(
                        {'error': f'Customer with id {customer_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except requests.HTTPError as e:
            return Response(
                {'error': 'FMCSA API error', 'details': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': 'Unexpected error during USDOT lookup', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def copy_to_customer(self, request, pk=None):
        """
        Copy USDOT profile data to customer record
        POST /api/usdot-profiles/{id}/copy_to_customer/
        Body: {"fields": ["legal_name", "phone", ...]} (optional, copies all if not specified)
        """
        profile = self.get_object()
        customer = profile.customer
        fields_to_copy = request.data.get('fields', None)

        # Define field mappings from profile to customer
        field_map = {
            'legal_name': 'legal_name',
            'phone': 'phone',  # Note: Customer model doesn't have phone in current schema
            'physical_address_line1': 'address_line1',
            'physical_address_line2': 'address_line2',
            'physical_city': 'city',
            'physical_state': 'state',
            'physical_postal_code': 'postal_code',
        }

        # If no specific fields requested, copy all available
        if fields_to_copy is None:
            fields_to_copy = list(field_map.keys())

        # Copy fields
        updated_fields = []
        for profile_field, customer_field in field_map.items():
            if profile_field in fields_to_copy:
                profile_value = getattr(profile, profile_field, None)
                if profile_value and hasattr(customer, customer_field):
                    setattr(customer, customer_field, profile_value)
                    updated_fields.append(customer_field)

        # Save customer if any fields were updated
        if updated_fields:
            updated_fields.append('updated_at')
            customer.save(update_fields=updated_fields)

        from apps.customers.serializers import CustomerDetailSerializer
        serializer = CustomerDetailSerializer(customer)
        return Response({
            'customer': serializer.data,
            'fields_copied': updated_fields
        })
