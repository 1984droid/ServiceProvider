"""
Work Order Views

REST API views for work order management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.work_orders.serializers import (
    WorkOrderSerializer,
    WorkOrderCreateSerializer,
    WorkOrderLineSerializer,
    WorkOrderLineCreateSerializer,
    DefectToWorkOrderSerializer,
    InspectionToWorkOrdersSerializer,
    VocabularySerializer,
    VocabularySuggestionSerializer,
)
from apps.work_orders.services.vocabulary_service import VocabularyService
from apps.inspections.services.defect_to_work_order_service import DefectToWorkOrderService
from apps.inspections.models import InspectionDefect, InspectionRun


class WorkOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkOrder management.

    Endpoints:
    - GET /work-orders/ - List work orders
    - POST /work-orders/ - Create work order
    - GET /work-orders/{id}/ - Get work order detail
    - PATCH /work-orders/{id}/ - Update work order
    - DELETE /work-orders/{id}/ - Delete work order
    - POST /work-orders/from_defect/ - Create work order from defect
    - POST /work-orders/from_inspection/ - Create work orders from inspection
    - GET /work-orders/available_assets/ - Get available assets for customer
    - POST /work-orders/{id}/request_approval/ - Request approval for work order
    - POST /work-orders/{id}/approve/ - Approve work order
    - POST /work-orders/{id}/reject/ - Reject work order
    - POST /work-orders/{id}/start/ - Start work order
    - POST /work-orders/{id}/complete/ - Complete work order

    Permissions:
    - Must be authenticated
    - Uses Django model permissions (view, add, change, delete)
    """

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = WorkOrder.objects.all().select_related(
        'customer',
        'department',
        'assigned_to',
        'approved_by'
    ).prefetch_related('lines')
    serializer_class = WorkOrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'status',
        'priority',
        'approval_status',
        'source_type',
        'customer',
        'department',
        'asset_type',
        'is_active',
    ]
    search_fields = ['work_order_number', 'title', 'description', 'notes']
    ordering_fields = ['created_at', 'scheduled_date', 'due_date', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return WorkOrderCreateSerializer
        return WorkOrderSerializer

    @action(detail=False, methods=['post'])
    def from_defect(self, request):
        """
        Create work order from a single defect.

        POST /api/work-orders/from_defect/
        Body: {
            "defect_id": "uuid",
            "department_id": "uuid" (optional),
            "auto_approve": false (optional)
        }
        """
        serializer = DefectToWorkOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        defect = get_object_or_404(InspectionDefect, id=serializer.validated_data['defect_id'])
        department_id = serializer.validated_data.get('department_id')
        auto_approve = serializer.validated_data.get('auto_approve', False)

        try:
            work_order = DefectToWorkOrderService.generate_work_order_from_defect(
                defect=defect,
                department_id=department_id,
                auto_approve=auto_approve
            )

            return Response(
                WorkOrderSerializer(work_order).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def from_inspection(self, request):
        """
        Create work orders from all defects in an inspection.

        POST /api/work-orders/from_inspection/
        Body: {
            "inspection_id": "uuid",
            "group_by_location": true (optional),
            "min_severity": "MAJOR" (optional),
            "department_id": "uuid" (optional),
            "auto_approve": false (optional)
        }
        """
        serializer = InspectionToWorkOrdersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inspection = get_object_or_404(InspectionRun, id=serializer.validated_data['inspection_id'])
        group_by_location = serializer.validated_data.get('group_by_location', True)
        min_severity = serializer.validated_data.get('min_severity')
        department_id = serializer.validated_data.get('department_id')
        auto_approve = serializer.validated_data.get('auto_approve', False)

        work_orders = DefectToWorkOrderService.generate_work_orders_from_inspection(
            inspection=inspection,
            group_by_location=group_by_location,
            min_severity=min_severity,
            department_id=department_id,
            auto_approve=auto_approve
        )

        return Response(
            {
                'count': len(work_orders),
                'work_orders': WorkOrderSerializer(work_orders, many=True).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def available_assets(self, request):
        """
        Get available assets for a customer filtered by asset type.

        GET /api/work-orders/available_assets/?customer={uuid}&asset_type={VEHICLE|EQUIPMENT}
        """
        customer_id = request.query_params.get('customer')
        asset_type = request.query_params.get('asset_type')

        if not customer_id:
            return Response(
                {'error': 'customer parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not asset_type or asset_type not in ['VEHICLE', 'EQUIPMENT']:
            return Response(
                {'error': 'asset_type must be either VEHICLE or EQUIPMENT'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.customers.models import Customer
        customer = get_object_or_404(Customer, id=customer_id)

        if asset_type == 'VEHICLE':
            from apps.assets.models import Vehicle
            from apps.assets.serializers import VehicleSerializer

            assets = Vehicle.objects.filter(
                customer=customer,
                is_active=True
            ).order_by('unit_number', '-year')

            serializer = VehicleSerializer(assets, many=True)
        else:  # EQUIPMENT
            from apps.assets.models import Equipment
            from apps.assets.serializers import EquipmentSerializer

            assets = Equipment.objects.filter(
                customer=customer,
                is_active=True
            ).order_by('serial_number')

            serializer = EquipmentSerializer(assets, many=True)

        return Response({
            'count': len(assets),
            'assets': serializer.data
        })

    @action(detail=True, methods=['post'])
    def request_approval(self, request, pk=None):
        """
        Request approval for a work order.

        POST /api/work-orders/{id}/request_approval/
        """
        work_order = self.get_object()

        if work_order.approval_status != 'DRAFT':
            return Response(
                {'error': f'Cannot request approval from {work_order.approval_status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not work_order.description:
            return Response(
                {'error': 'Work order must have a description'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if work_order.lines.count() == 0:
            return Response(
                {'error': 'Work order must have at least one line item'},
                status=status.HTTP_400_BAD_REQUEST
            )

        work_order.approval_status = 'PENDING_APPROVAL'
        work_order.save()

        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a work order.

        POST /api/work-orders/{id}/approve/
        Body: {
            "approved_by": "employee_uuid"
        }
        """
        work_order = self.get_object()

        if work_order.approval_status == 'APPROVED':
            return Response(
                {'error': 'Work order already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approved_by_id = request.data.get('approved_by')
        if not approved_by_id:
            return Response(
                {'error': 'approved_by is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.organization.models import Employee
        approved_by = get_object_or_404(Employee, id=approved_by_id)

        work_order.approval_status = 'APPROVED'
        work_order.approved_by = approved_by
        from django.utils import timezone
        work_order.approved_at = timezone.now()
        work_order.save()

        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a work order.

        POST /api/work-orders/{id}/reject/
        Body: {
            "rejected_reason": "string"
        }
        """
        work_order = self.get_object()

        if work_order.approval_status == 'REJECTED':
            return Response(
                {'error': 'Work order already rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rejected_reason = request.data.get('rejected_reason', '')

        work_order.approval_status = 'REJECTED'
        work_order.rejected_reason = rejected_reason
        work_order.save()

        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a work order.

        POST /api/work-orders/{id}/start/
        """
        work_order = self.get_object()

        if work_order.status == 'IN_PROGRESS':
            return Response(
                {'error': 'Work order already in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if work_order.approval_status != 'APPROVED':
            return Response(
                {'error': 'Work order must be approved before starting'},
                status=status.HTTP_400_BAD_REQUEST
            )

        work_order.status = 'IN_PROGRESS'
        if not work_order.started_at:
            from django.utils import timezone
            work_order.started_at = timezone.now()
        work_order.save()

        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete a work order.

        POST /api/work-orders/{id}/complete/
        """
        work_order = self.get_object()

        if work_order.status == 'COMPLETED':
            return Response(
                {'error': 'Work order already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check all lines are completed
        incomplete_lines = work_order.lines.exclude(status='COMPLETED').count()
        if incomplete_lines > 0:
            return Response(
                {'error': f'{incomplete_lines} line item(s) not yet completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        work_order.status = 'COMPLETED'
        from django.utils import timezone
        work_order.completed_at = timezone.now()
        work_order.save()

        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=['get'])
    def defects(self, request, pk=None):
        """
        Get defects associated with this work order.

        GET /api/work-orders/{id}/defects/
        """
        work_order = self.get_object()

        if work_order.source_type != 'INSPECTION_DEFECT':
            return Response(
                {'error': 'Work order not created from inspection defect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get defects
        from apps.inspections.serializers import InspectionDefectSerializer

        if work_order.source_id:
            # Check if source is defect or inspection
            try:
                defect = InspectionDefect.objects.get(id=work_order.source_id)
                defects = [defect]
            except InspectionDefect.DoesNotExist:
                # Source is inspection
                inspection = get_object_or_404(InspectionRun, id=work_order.source_id)
                defects = list(inspection.defects.filter(status='WORK_ORDER_CREATED'))
        else:
            defects = []

        return Response({
            'count': len(defects),
            'defects': InspectionDefectSerializer(defects, many=True).data
        })


class WorkOrderLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkOrderLine management.

    Endpoints:
    - GET /work-order-lines/ - List work order lines
    - POST /work-order-lines/ - Create work order line
    - GET /work-order-lines/{id}/ - Get work order line detail
    - PATCH /work-order-lines/{id}/ - Update work order line
    - DELETE /work-order-lines/{id}/ - Delete work order line
    - POST /work-order-lines/{id}/complete/ - Complete line
    """

    queryset = WorkOrderLine.objects.all().select_related(
        'work_order',
        'assigned_to',
        'completed_by'
    )
    serializer_class = WorkOrderLineSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['work_order', 'status', 'verb', 'noun', 'service_location']
    search_fields = ['verb', 'noun', 'service_location', 'description', 'notes']
    ordering_fields = ['line_number', 'status', 'created_at']
    ordering = ['line_number']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return WorkOrderLineCreateSerializer
        return WorkOrderLineSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete a work order line.

        POST /api/work-order-lines/{id}/complete/
        Body: {
            "completed_by": "employee_uuid",
            "actual_hours": 2.5 (optional)
        }
        """
        line = self.get_object()

        if line.status == 'COMPLETED':
            return Response(
                {'error': 'Line already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        completed_by_id = request.data.get('completed_by')
        if not completed_by_id:
            return Response(
                {'error': 'completed_by is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.organization.models import Employee
        completed_by = get_object_or_404(Employee, id=completed_by_id)

        line.status = 'COMPLETED'
        line.completed_by = completed_by
        from django.utils import timezone
        line.completed_at = timezone.now()

        if 'actual_hours' in request.data:
            line.actual_hours = request.data['actual_hours']

        line.save()

        return Response(WorkOrderLineSerializer(line).data)


class VocabularyViewSet(viewsets.ViewSet):
    """
    ViewSet for work order vocabulary management.

    Endpoints:
    - GET /vocabulary/ - Get all vocabulary
    - GET /vocabulary/verbs/ - Get all verbs
    - GET /vocabulary/nouns/ - Get all nouns
    - GET /vocabulary/service_locations/ - Get all service locations
    - POST /vocabulary/suggest/ - Get vocabulary suggestions from description
    """

    @action(detail=False, methods=['get'])
    def index(self, request):
        """
        Get all vocabulary.

        GET /api/vocabulary/
        """
        vocab = VocabularyService.load_vocabulary()
        return Response(vocab)

    @action(detail=False, methods=['get'])
    def verbs(self, request):
        """
        Get all verbs.

        GET /api/vocabulary/verbs/
        """
        verbs = VocabularyService.get_verbs()
        return Response({'verbs': verbs})

    @action(detail=False, methods=['get'])
    def nouns(self, request):
        """
        Get all nouns, optionally filtered by category.

        GET /api/vocabulary/nouns/?category=Hydraulic
        """
        category = request.query_params.get('category')
        nouns = VocabularyService.get_nouns(category=category)
        return Response({'nouns': nouns})

    @action(detail=False, methods=['get'])
    def service_locations(self, request):
        """
        Get all service locations.

        GET /api/vocabulary/service_locations/
        """
        locations = VocabularyService.get_service_locations()
        return Response({'service_locations': locations})

    @action(detail=False, methods=['post'])
    def suggest(self, request):
        """
        Get vocabulary suggestions from description.

        POST /api/vocabulary/suggest/
        Body: {"description": "Replace hydraulic hose on boom"}
        """
        serializer = VocabularySuggestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data['description']
        suggestions = VocabularyService.suggest_vocabulary(description)

        return Response(suggestions)
