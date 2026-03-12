"""
DRF ViewSets for Asset Management

Provides REST API endpoints for:
- Vehicle CRUD with VIN lookup and filtering
- Equipment CRUD with tag-based filtering and data management
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .models import Vehicle, Equipment, VINDecodeData
from .serializers import (
    VehicleListSerializer,
    VehicleDetailSerializer,
    EquipmentListSerializer,
    EquipmentDetailSerializer,
    EquipmentDataUpdateSerializer,
    VINDecodeDataSerializer,
)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle management

    Endpoints:
    - GET /api/vehicles/ - List all vehicles (paginated)
    - POST /api/vehicles/ - Create new vehicle
    - GET /api/vehicles/{id}/ - Retrieve vehicle details
    - PUT/PATCH /api/vehicles/{id}/ - Update vehicle
    - DELETE /api/vehicles/{id}/ - Delete vehicle (soft delete recommended)

    Filtering:
    - ?is_active=true/false
    - ?customer={customer_id}
    - ?make=Ford
    - ?year=2020

    Search:
    - ?search=vin+or+unit+number

    Ordering:
    - ?ordering=unit_number
    - ?ordering=-year
    """
    queryset = Vehicle.objects.all().select_related('customer').prefetch_related('equipment')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'customer', 'make', 'year']
    search_fields = ['vin', 'unit_number', 'make', 'model', 'license_plate', 'customer__name']
    ordering_fields = ['unit_number', 'year', 'make', 'model', 'created_at']
    ordering = ['unit_number']

    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleDetailSerializer

    def get_queryset(self):
        """
        Optionally filter by:
        - has_equipment: vehicles with/without mounted equipment
        - tags: filter by specific tags
        - year_min/year_max: filter by year range
        """
        queryset = super().get_queryset()

        # Filter by equipment presence
        has_equipment = self.request.query_params.get('has_equipment')
        if has_equipment is not None:
            queryset = queryset.annotate(equipment_count=Count('equipment'))
            if has_equipment.lower() == 'true':
                queryset = queryset.filter(equipment_count__gt=0)
            else:
                queryset = queryset.filter(equipment_count=0)

        # Filter by tags (any match)
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [t.strip().upper() for t in tags.split(',')]
            # PostgreSQL JSONField contains query
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])

        # Filter by year range
        year_min = self.request.query_params.get('year_min')
        if year_min:
            try:
                queryset = queryset.filter(year__gte=int(year_min))
            except ValueError:
                pass

        year_max = self.request.query_params.get('year_max')
        if year_max:
            try:
                queryset = queryset.filter(year__lte=int(year_max))
            except ValueError:
                pass

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

    @action(detail=False, methods=['get'])
    def lookup_by_vin(self, request):
        """
        Lookup vehicle by VIN
        GET /api/vehicles/lookup_by_vin/?vin=1HGCM82633A123456
        """
        vin = request.query_params.get('vin')
        if not vin:
            return Response(
                {'error': 'vin parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean VIN
        clean_vin = vin.upper().strip()

        try:
            vehicle = Vehicle.objects.get(vin=clean_vin)
            serializer = VehicleDetailSerializer(vehicle)
            return Response(serializer.data)
        except Vehicle.DoesNotExist:
            return Response(
                {'error': f'Vehicle with VIN {clean_vin} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def lookup_by_unit(self, request):
        """
        Lookup vehicle by unit number
        GET /api/vehicles/lookup_by_unit/?unit_number=T123&customer={customer_id}
        """
        unit_number = request.query_params.get('unit_number')
        customer_id = request.query_params.get('customer')

        if not unit_number:
            return Response(
                {'error': 'unit_number parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build query
        query = Q(unit_number__iexact=unit_number)
        if customer_id:
            query &= Q(customer_id=customer_id)

        vehicles = Vehicle.objects.filter(query)

        if not vehicles.exists():
            return Response(
                {'error': f'Vehicle with unit number {unit_number} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if vehicles.count() > 1 and not customer_id:
            return Response(
                {
                    'error': f'Multiple vehicles found with unit number {unit_number}. Please specify customer parameter.',
                    'count': vehicles.count()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle = vehicles.first()
        serializer = VehicleDetailSerializer(vehicle)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def equipment(self, request, pk=None):
        """
        Get all equipment mounted on this vehicle
        GET /api/vehicles/{id}/equipment/
        """
        vehicle = self.get_object()
        equipment = vehicle.equipment.all().order_by('-is_active', 'equipment_type')

        # Apply filtering
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            equipment = equipment.filter(is_active=is_active.lower() == 'true')

        serializer = EquipmentListSerializer(equipment, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def decode_vin(self, request, pk=None):
        """
        Decode VIN using external service (NHTSA or similar)
        POST /api/vehicles/{id}/decode_vin/

        This would integrate with NHTSA VIN decoder API
        For now, returns placeholder structure
        """
        vehicle = self.get_object()

        # TODO: Implement actual VIN decode via NHTSA API
        # https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{VIN}?format=json

        # Placeholder response
        decode_data = {
            'vin': vehicle.vin,
            'decoded': False,
            'message': 'VIN decode integration not yet implemented',
            # Example structure:
            # 'year': 2020,
            # 'make': 'Ford',
            # 'model': 'F-350',
            # 'body_class': 'Truck',
            # 'engine_model': 'Power Stroke',
            # 'fuel_type': 'Diesel',
        }

        # Save decode data to vehicle
        vehicle.vin_decode_data = decode_data
        vehicle.save(update_fields=['vin_decode_data', 'updated_at'])

        return Response(decode_data)


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Equipment management

    Endpoints:
    - GET /api/equipment/ - List all equipment (paginated)
    - POST /api/equipment/ - Create new equipment
    - GET /api/equipment/{id}/ - Retrieve equipment details
    - PUT/PATCH /api/equipment/{id}/ - Update equipment
    - DELETE /api/equipment/{id}/ - Delete equipment (soft delete recommended)

    Filtering:
    - ?is_active=true/false
    - ?customer={customer_id}
    - ?equipment_type=AERIAL
    - ?mounted_on_vehicle={vehicle_id}

    Search:
    - ?search=serial+number

    Ordering:
    - ?ordering=asset_number
    - ?ordering=-created_at
    """
    queryset = Equipment.objects.all().select_related('customer', 'mounted_on_vehicle')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'customer', 'equipment_type', 'mounted_on_vehicle']
    search_fields = ['serial_number', 'asset_number', 'manufacturer', 'model', 'customer__name']
    ordering_fields = ['asset_number', 'serial_number', 'equipment_type', 'created_at']
    ordering = ['asset_number']

    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return EquipmentListSerializer
        return EquipmentDetailSerializer

    def get_queryset(self):
        """
        Optionally filter by:
        - tags: filter by specific tags
        - mounted: filter mounted/unmounted equipment
        - has_data: filter equipment with/without equipment_data
        """
        queryset = super().get_queryset()

        # Filter by tags (any match)
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [t.strip().upper() for t in tags.split(',')]
            # PostgreSQL JSONField contains query
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])

        # Filter by mounted status
        mounted = self.request.query_params.get('mounted')
        if mounted is not None:
            if mounted.lower() == 'true':
                queryset = queryset.exclude(mounted_on_vehicle__isnull=True)
            else:
                queryset = queryset.filter(mounted_on_vehicle__isnull=True)

        # Filter by equipment_data presence
        has_data = self.request.query_params.get('has_data')
        if has_data is not None:
            if has_data.lower() == 'true':
                queryset = queryset.exclude(Q(equipment_data__isnull=True) | Q(equipment_data={}))
            else:
                queryset = queryset.filter(Q(equipment_data__isnull=True) | Q(equipment_data={}))

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

    @action(detail=False, methods=['get'])
    def lookup_by_serial(self, request):
        """
        Lookup equipment by serial number
        GET /api/equipment/lookup_by_serial/?serial_number=ABC123
        """
        serial_number = request.query_params.get('serial_number')
        if not serial_number:
            return Response(
                {'error': 'serial_number parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean serial number
        clean_sn = serial_number.upper().strip()

        try:
            equipment = Equipment.objects.get(serial_number=clean_sn)
            serializer = EquipmentDetailSerializer(equipment)
            return Response(serializer.data)
        except Equipment.DoesNotExist:
            return Response(
                {'error': f'Equipment with serial number {clean_sn} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def mount(self, request, pk=None):
        """
        Mount equipment on a vehicle
        POST /api/equipment/{id}/mount/
        Body: {"vehicle_id": "uuid"}
        """
        equipment = self.get_object()
        vehicle_id = request.data.get('vehicle_id')

        if not vehicle_id:
            return Response(
                {'error': 'vehicle_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)

            # Validate same customer
            if vehicle.customer_id != equipment.customer_id:
                return Response(
                    {'error': 'Vehicle and equipment must belong to the same customer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            equipment.mounted_on_vehicle = vehicle
            equipment.save(update_fields=['mounted_on_vehicle', 'updated_at'])

            serializer = self.get_serializer(equipment)
            return Response(serializer.data)

        except Vehicle.DoesNotExist:
            return Response(
                {'error': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def unmount(self, request, pk=None):
        """
        Unmount equipment from vehicle
        POST /api/equipment/{id}/unmount/
        """
        equipment = self.get_object()

        if not equipment.mounted_on_vehicle:
            return Response(
                {'error': 'Equipment is not mounted on any vehicle'},
                status=status.HTTP_400_BAD_REQUEST
            )

        equipment.mounted_on_vehicle = None
        equipment.save(update_fields=['mounted_on_vehicle', 'updated_at'])

        serializer = self.get_serializer(equipment)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'patch'])
    def update_data(self, request, pk=None):
        """
        Update equipment_data field with tag-specific data
        POST /api/equipment/{id}/update_data/
        Body: {
            "data_type": "placard",
            "data": {
                "max_platform_height": 45,
                "max_working_height": 51,
                "platform_capacity": 500
            }
        }
        """
        equipment = self.get_object()
        serializer = EquipmentDataUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(equipment)

            # Return updated equipment
            equipment_serializer = EquipmentDetailSerializer(equipment)
            return Response(equipment_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def required_data_fields(self, request, pk=None):
        """
        Get list of required data fields based on equipment tags
        GET /api/equipment/{id}/required_data_fields/

        Returns structure describing what data needs to be collected
        based on the equipment's tags
        """
        equipment = self.get_object()
        tags = equipment.tags or []

        required_fields = {}

        # Define required fields per tag
        TAG_DATA_REQUIREMENTS = {
            'AERIAL_DEVICE': {
                'placard': {
                    'max_platform_height': 'number',
                    'max_working_height': 'number',
                    'platform_capacity': 'number',
                    'max_wind_speed': 'number',
                }
            },
            'INSULATED_BOOM': {
                'dielectric': {
                    'insulation_rating_kv': 'number',
                    'last_test_date': 'date',
                    'next_test_due': 'date',
                    'test_certificate_number': 'string',
                }
            },
            'DIELECTRIC': {
                'dielectric': {
                    'insulation_rating_kv': 'number',
                    'last_test_date': 'date',
                    'next_test_due': 'date',
                    'test_certificate_number': 'string',
                }
            },
        }

        # Build required fields based on tags
        for tag in tags:
            if tag in TAG_DATA_REQUIREMENTS:
                for data_type, fields in TAG_DATA_REQUIREMENTS[tag].items():
                    if data_type not in required_fields:
                        required_fields[data_type] = {}
                    required_fields[data_type].update(fields)

        return Response({
            'equipment_id': equipment.id,
            'tags': tags,
            'required_fields': required_fields,
            'current_data': equipment.equipment_data or {}
        })


class VINDecodeDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VIN Decode Data management

    Endpoints:
    - GET /api/vin-decode-data/ - List all decode records
    - POST /api/vin-decode-data/ - Create decode record (after NHTSA API call)
    - GET /api/vin-decode-data/{id}/ - Retrieve decode details
    - PUT/PATCH /api/vin-decode-data/{id}/ - Update decode record
    - DELETE /api/vin-decode-data/{id}/ - Delete decode record

    Filtering:
    - ?vehicle={vehicle_id}
    - ?make=Ford
    - ?model_year=2020

    Search:
    - ?search=vin+or+make
    """
    queryset = VINDecodeData.objects.all().select_related('vehicle', 'vehicle__customer')
    serializer_class = VINDecodeDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle', 'make', 'model_year', 'fuel_type_primary']
    search_fields = ['vin', 'make', 'model', 'manufacturer', 'vehicle__unit_number']
    ordering_fields = ['decoded_at', 'model_year', 'make']
    ordering = ['-decoded_at']

    @action(detail=False, methods=['get'])
    def lookup_by_vin(self, request):
        """
        Lookup decode data by VIN
        GET /api/vin-decode-data/lookup_by_vin/?vin=1HGCM82633A123456
        """
        vin = request.query_params.get('vin')
        if not vin:
            return Response(
                {'error': 'vin parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean VIN
        clean_vin = vin.upper().strip()

        try:
            decode_data = VINDecodeData.objects.get(vin=clean_vin)
            serializer = self.get_serializer(decode_data)
            return Response(serializer.data)
        except VINDecodeData.DoesNotExist:
            return Response(
                {'error': f'VIN decode data for {clean_vin} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def decode_vin(self, request):
        """
        Decode a VIN using NHTSA vPIC API and create/update decode record
        POST /api/vin-decode-data/decode_vin/
        Body: {"vin": "1HGCM82633A123456", "vehicle_id": "uuid" (optional)}

        If vehicle_id provided, links decode to that vehicle
        Otherwise, just stores decode data without vehicle linkage
        """
        vin = request.data.get('vin')
        vehicle_id = request.data.get('vehicle_id')

        if not vin:
            return Response(
                {'error': 'vin parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clean VIN
        clean_vin = vin.upper().strip()

        # TODO: Implement actual NHTSA API integration
        # https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{VIN}?format=json

        # Placeholder response structure
        decode_result = {
            'vin': clean_vin,
            'decoded': False,
            'message': 'NHTSA VIN decode integration not yet implemented',
            'note': 'This is a placeholder. Actual implementation will call NHTSA vPIC API.',
            # Example of what real decode would return:
            # 'model_year': 2020,
            # 'make': 'Honda',
            # 'model': 'Accord',
            # 'manufacturer': 'HONDA',
            # 'vehicle_type': 'Passenger Car',
            # 'body_class': 'Sedan/Saloon',
            # 'engine_model': 'K20C3',
            # 'fuel_type_primary': 'Gasoline',
        }

        return Response(decode_result, status=status.HTTP_501_NOT_IMPLEMENTED)
