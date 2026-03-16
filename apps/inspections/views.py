"""
Inspection API Views

ViewSets for inspection templates and inspection execution.
"""

from datetime import datetime
from django.http import HttpResponse
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.core.exceptions import ValidationError as DjangoValidationError
import rest_framework.parsers

from apps.authentication.permissions import (
    CanEditOwnInspection,
    CannotEditFinalizedInspection,
    IsAdmin,
)

from .models import InspectionRun, InspectionDefect
from .services.template_service import (
    TemplateService,
    TemplateNotFoundError,
    TemplateValidationError
)
from .services.template_filter_service import TemplateFilterService
from .services.runtime_service import (
    InspectionRuntime,
    InspectionRuntimeError,
    InspectionAlreadyFinalizedException,
    InspectionNotReadyException
)
from .serializers import (
    InspectionRunListSerializer,
    InspectionRunDetailSerializer,
    CreateInspectionSerializer,
    SaveStepResponseSerializer,
    FinalizeInspectionSerializer,
    InspectionDefectSerializer
)


class TemplateViewSet(viewsets.ViewSet):
    """
    ViewSet for inspection templates.

    Templates are read-only and served from JSON files.
    No create/update/delete operations allowed.

    Endpoints:
    - GET /api/templates/ - List all templates
    - GET /api/templates/{key}/ - Get specific template
    - GET /api/templates/{key}/step/ - Get specific step
    - GET /api/templates/for_equipment/ - Get templates for equipment
    - GET /api/templates/published/ - Get only published templates
    - GET /api/templates/by_standard/ - Get templates by standard

    Permissions:
    - Authenticated users can view templates
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all available templates.

        Returns:
            200: List of template summaries
        """
        try:
            templates = TemplateService.list_all_templates()
            return Response({
                'count': len(templates),
                'templates': templates
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to list templates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Get a specific template by key.

        Args:
            pk: Template key

        Returns:
            200: Full template dict
            404: Template not found
            400: Template validation error
        """
        try:
            template = TemplateService.load_template(pk)
            return Response(template)
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except TemplateValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def published(self, request):
        """
        Get only published (production-ready) templates.

        Returns:
            200: List of published templates
        """
        try:
            templates = TemplateService.get_published_templates()
            return Response({
                'count': len(templates),
                'templates': templates
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to get published templates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_standard(self, request):
        """
        Get templates by standard code.

        Query params:
            standard_code: e.g., 'ANSI/SAIA A92.2'

        Returns:
            200: List of templates for standard
            400: Missing standard_code
        """
        standard_code = request.query_params.get('standard_code')
        if not standard_code:
            return Response(
                {'error': 'standard_code query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            templates = TemplateService.get_templates_by_standard(standard_code)
            return Response({
                'standard_code': standard_code,
                'count': len(templates),
                'templates': templates
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to get templates by standard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def for_equipment(self, request):
        """
        Get templates applicable to specific equipment.

        Query params:
            equipment_id: UUID of equipment

        Returns:
            200: List of applicable templates with readiness status
            400: Missing equipment_id
            404: Equipment not found
        """
        from apps.assets.models import Equipment

        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {'error': 'equipment_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            equipment = Equipment.objects.get(id=equipment_id)
        except Equipment.DoesNotExist:
            return Response(
                {'error': f'Equipment with id {equipment_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            templates = TemplateService.get_applicable_templates(equipment)
            return Response({
                'equipment_id': str(equipment.id),
                'equipment_serial': equipment.serial_number,
                'equipment_type': equipment.equipment_type,
                'equipment_capabilities': equipment.capabilities,
                'count': len(templates),
                'templates': templates
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to get applicable templates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def for_asset(self, request):
        """
        Get templates applicable to a specific asset (vehicle or equipment).

        Uses the new TemplateFilterService with standards-based filtering.

        Query params:
            asset_type: 'vehicle' or 'equipment'
            asset_id: UUID of the asset

        Returns:
            200: List of applicable templates
            400: Missing or invalid parameters
            404: Asset not found
        """
        from apps.assets.models import Vehicle, Equipment

        asset_type = request.query_params.get('asset_type', '').lower()
        asset_id = request.query_params.get('asset_id')

        if not asset_type:
            return Response(
                {'error': 'asset_type query parameter required (vehicle or equipment)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not asset_id:
            return Response(
                {'error': 'asset_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if asset_type not in ['vehicle', 'equipment']:
            return Response(
                {'error': 'asset_type must be "vehicle" or "equipment"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if asset_type == 'vehicle':
                asset = Vehicle.objects.get(id=asset_id)
                asset_dict = {
                    'id': str(asset.id),
                    'body_type': asset.body_type,
                    'capabilities': asset.capabilities,
                }
                templates = TemplateFilterService.get_applicable_templates_for_vehicle(asset_dict)
                asset_info = {
                    'asset_type': 'vehicle',
                    'asset_id': str(asset.id),
                    'unit_number': asset.unit_number,
                    'body_type': asset.body_type,
                    'capabilities': asset.capabilities,
                }
            else:  # equipment
                asset = Equipment.objects.get(id=asset_id)
                asset_dict = {
                    'id': str(asset.id),
                    'equipment_type': asset.equipment_type,
                    'capabilities': asset.capabilities,
                }
                templates = TemplateFilterService.get_applicable_templates_for_equipment(asset_dict)
                asset_info = {
                    'asset_type': 'equipment',
                    'asset_id': str(asset.id),
                    'serial_number': asset.serial_number,
                    'equipment_type': asset.equipment_type,
                    'capabilities': asset.capabilities,
                }

            return Response({
                **asset_info,
                'count': len(templates),
                'templates': templates
            })

        except (Vehicle.DoesNotExist, Equipment.DoesNotExist):
            return Response(
                {'error': f'{asset_type.capitalize()} with id {asset_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get applicable templates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def step(self, request, pk=None):
        """
        Get a specific step from a template.

        Args:
            pk: Template key

        Query params:
            step_key: Step identifier

        Returns:
            200: Step dict
            400: Missing step_key
            404: Template or step not found
        """
        step_key = request.query_params.get('step_key')
        if not step_key:
            return Response(
                {'error': 'step_key query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            step = TemplateService.get_template_step(pk, step_key)
            if not step:
                return Response(
                    {'error': f'Step {step_key} not found in template {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(step)
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get step: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def required_steps(self, request, pk=None):
        """
        Get all required steps for a template.

        Args:
            pk: Template key

        Returns:
            200: List of required steps
            404: Template not found
        """
        try:
            steps = TemplateService.get_required_steps(pk)
            return Response({
                'template_key': pk,
                'count': len(steps),
                'required_steps': steps
            })
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get required steps: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def enums(self, request, pk=None):
        """
        Get all enum definitions for a template.

        Args:
            pk: Template key

        Returns:
            200: Dict of enum name to values
            404: Template not found
        """
        try:
            enums = TemplateService.get_template_enums(pk)
            return Response({
                'template_key': pk,
                'enums': enums
            })
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get enums: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def enum_values(self, request, pk=None):
        """
        Get values for a specific enum in a template.

        Args:
            pk: Template key

        Query params:
            enum_name: Name of enum

        Returns:
            200: List of enum values
            400: Missing enum_name
            404: Template or enum not found
        """
        enum_name = request.query_params.get('enum_name')
        if not enum_name:
            return Response(
                {'error': 'enum_name query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            values = TemplateService.get_enum_values(pk, enum_name)
            if values is None:
                return Response(
                    {'error': f'Enum {enum_name} not found in template {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response({
                'template_key': pk,
                'enum_name': enum_name,
                'values': values
            })
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get enum values: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reload(self, request, pk=None):
        """
        Force reload a template from disk (clear cache).

        Args:
            pk: Template key

        Returns:
            200: Reloaded template
            404: Template not found
            403: Forbidden in production
        """
        # Only allow in development
        from django.conf import settings
        if not settings.DEBUG:
            return Response(
                {'error': 'Template reload not allowed in production'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            template = TemplateService.reload_template(pk)
            return Response({
                'message': f'Template {pk} reloaded successfully',
                'template': template
            })
        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to reload template: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InspectionRunViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inspection run execution.

    Endpoints:
    - POST /api/inspections/ - Create new inspection
    - GET /api/inspections/ - List inspections (filterable)
    - GET /api/inspections/{id}/ - Get inspection details
    - PATCH /api/inspections/{id}/save_step/ - Save step response
    - GET /api/inspections/{id}/completion/ - Get completion status
    - GET /api/inspections/{id}/review/ - Get inspection review (read-only with defects)
    - POST /api/inspections/{id}/finalize/ - Finalize inspection
    - GET /api/inspections/{id}/step/{step_key}/ - Get step response
    - DELETE /api/inspections/{id}/clear_step/ - Clear step response
    - GET /api/inspections/{id}/next_step/ - Get next incomplete step

    Permissions:
    - Must be authenticated
    - Can view: Users with inspections.view_inspectionrun permission
    - Can create: Inspectors and dispatchers
    - Can edit own: Inspectors can edit inspections they created (until finalized)
    - Cannot edit finalized: Only super admins can reopen finalized inspections
    - Can delete: Admins only (and only non-finalized inspections)
    """

    permission_classes = [IsAuthenticated, CanEditOwnInspection, CannotEditFinalizedInspection]
    queryset = InspectionRun.objects.all().select_related('customer').prefetch_related('defects')

    def get_permissions(self):
        """
        Customize permissions per action.
        """
        if self.action == 'destroy':
            # Only admins can delete inspections
            return [IsAuthenticated(), IsAdmin(), CannotEditFinalizedInspection()]
        elif self.action in ['list', 'retrieve', 'export_pdf', 'defects', 'completion']:
            # Read-only actions require authentication only
            return [IsAuthenticated()]
        else:
            # Create, update, finalize require custom permissions
            return [IsAuthenticated(), CanEditOwnInspection(), CannotEditFinalizedInspection()]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return InspectionRunListSerializer
        elif self.action == 'create':
            return CreateInspectionSerializer
        return InspectionRunDetailSerializer

    def list(self, request):
        """
        List inspection runs with filtering.

        Query params:
            customer_id: Filter by customer
            asset_type: Filter by asset type (VEHICLE/EQUIPMENT)
            asset_id: Filter by specific asset
            status: Filter by status (DRAFT/IN_PROGRESS/COMPLETED)
            template_key: Filter by template
        """
        queryset = self.get_queryset()

        # Apply filters
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        asset_type = request.query_params.get('asset_type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)

        asset_id = request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)

        inspection_status = request.query_params.get('status')
        if inspection_status:
            queryset = queryset.filter(status=inspection_status)

        template_key = request.query_params.get('template_key')
        if template_key:
            queryset = queryset.filter(template_key=template_key)

        serializer = InspectionRunListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'inspections': serializer.data
        })

    def create(self, request):
        """
        Create new inspection run.

        Request body:
            template_key: Template to use
            asset_type: VEHICLE or EQUIPMENT
            asset_id: UUID of asset
            inspector_name: Name of inspector (optional)

        Returns:
            201: Created inspection
            400: Validation error
            404: Template or asset not found
        """
        serializer = CreateInspectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Default inspector_name to logged-in user's full name if not provided
            inspector_name = serializer.validated_data.get('inspector_name')
            if not inspector_name and request.user.is_authenticated:
                inspector_name = f"{request.user.first_name} {request.user.last_name}".strip()
                if not inspector_name:  # Fallback to username if no first/last name
                    inspector_name = request.user.username

            inspection = InspectionRuntime.create_inspection(
                template_key=serializer.validated_data['template_key'],
                asset=serializer.validated_data['asset'],
                inspector_name=inspector_name or ''
            )

            # Auto-populate certification info from user's employee record
            if request.user.is_authenticated and hasattr(request.user, 'employee'):
                employee = request.user.employee
                if employee and employee.certifications:
                    # Get the standard code from the template
                    template_standard = inspection.template_snapshot.get('template', {}).get('standard', {}).get('code')

                    if template_standard:
                        # Find matching certification
                        # Certifications expected format: [{"standard": "ANSI/SAIA A92.2", "cert_number": "...", "expiry": "..."}]
                        matching_cert = None
                        for cert in employee.certifications:
                            if isinstance(cert, dict) and cert.get('standard') == template_standard:
                                matching_cert = cert
                                break

                        # Store certification info in inspection metadata
                        if matching_cert:
                            if not inspection.metadata:
                                inspection.metadata = {}
                            inspection.metadata['inspector_certification'] = {
                                'standard': matching_cert.get('standard'),
                                'cert_number': matching_cert.get('cert_number'),
                                'expiry_date': matching_cert.get('expiry'),
                                'inspector_name': inspector_name
                            }
                            inspection.save()

            detail_serializer = InspectionRunDetailSerializer(inspection)
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except TemplateNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create inspection: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Get detailed inspection run."""
        try:
            inspection = self.get_queryset().get(pk=pk)
            serializer = InspectionRunDetailSerializer(inspection)
            return Response(serializer.data)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'])
    def save_step(self, request, pk=None):
        """
        Save step response.

        Request body:
            step_key: Step identifier
            field_data: Dict of field responses
            validate: Whether to validate (default: true)

        Returns:
            200: Step saved successfully
            400: Validation error
            403: Inspection is finalized
            404: Inspection or step not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SaveStepResponseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validation_result = InspectionRuntime.save_step_response(
                inspection_run=inspection,
                step_key=serializer.validated_data['step_key'],
                field_data=serializer.validated_data['field_data'],
                validate=serializer.validated_data.get('validate', True)
            )

            # Reload to get updated data
            inspection.refresh_from_db()
            detail_serializer = InspectionRunDetailSerializer(inspection)

            return Response({
                'message': 'Step saved successfully',
                'validation': {
                    'valid': validation_result.valid,
                    'errors': validation_result.all_errors
                },
                'inspection': detail_serializer.data
            })

        except InspectionAlreadyFinalizedException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to save step: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def completion(self, request, pk=None):
        """
        Get completion status.

        Returns:
            200: Completion status
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
            completion_status = InspectionRuntime.calculate_completion_status(inspection)
            return Response(completion_status.to_dict())
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """
        Finalize inspection (make immutable).

        Request body:
            signature_data: Optional signature data
            force: Force finalize even if incomplete (default: false)

        Returns:
            200: Inspection finalized
            400: Validation error
            403: Already finalized or not ready
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FinalizeInspectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            InspectionRuntime.finalize_inspection(
                inspection_run=inspection,
                signature_data=serializer.validated_data.get('signature_data'),
                force=serializer.validated_data.get('force', False)
            )

            # Reload to get updated data
            inspection.refresh_from_db()
            detail_serializer = InspectionRunDetailSerializer(inspection)

            return Response({
                'message': 'Inspection finalized successfully',
                'inspection': detail_serializer.data
            })

        except InspectionAlreadyFinalizedException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except InspectionNotReadyException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to finalize inspection: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='step/(?P<step_key>[^/.]+)')
    def get_step(self, request, pk=None, step_key=None):
        """
        Get saved response for a specific step.

        Args:
            pk: Inspection ID
            step_key: Step identifier

        Returns:
            200: Step response data
            404: Inspection or step not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
            step_response = InspectionRuntime.get_step_response(inspection, step_key)

            if step_response is None:
                return Response(
                    {'error': f'No response found for step {step_key}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'step_key': step_key,
                'response': step_response
            })

        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def clear_step(self, request, pk=None):
        """
        Clear a step's response data.

        Query params:
            step_key: Step to clear

        Returns:
            200: Step cleared
            400: Missing step_key
            403: Inspection is finalized
            404: Inspection not found
        """
        step_key = request.query_params.get('step_key')
        if not step_key:
            return Response(
                {'error': 'step_key query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inspection = self.get_queryset().get(pk=pk)
            InspectionRuntime.clear_step_response(inspection, step_key)

            return Response({
                'message': f'Step {step_key} cleared successfully'
            })

        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except InspectionAlreadyFinalizedException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['get'])
    def next_step(self, request, pk=None):
        """
        Get next incomplete step.

        Returns:
            200: Next step definition or null if complete
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
            next_step = InspectionRuntime.get_next_incomplete_step(inspection)

            if next_step is None:
                return Response({
                    'message': 'All steps complete',
                    'next_step': None
                })

            return Response({
                'next_step': next_step
            })

        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def evaluate_rules(self, request, pk=None):
        """
        Evaluate rules and generate defects without finalizing.

        Allows preview of defects before finalization.

        Returns:
            200: Defects generated
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            defects = InspectionRuntime.evaluate_rules(inspection)

            # Get defect summary
            from apps.inspections.services.defect_generator import DefectGenerator
            summary = DefectGenerator.get_defect_summary(inspection)

            defect_serializer = InspectionDefectSerializer(defects, many=True)

            return Response({
                'defects_generated': len(defects),
                'defects': defect_serializer.data,
                'summary': summary
            })

        except Exception as e:
            return Response(
                {'error': f'Failed to evaluate rules: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def defects(self, request, pk=None):
        """
        Get all defects for inspection.

        Returns:
            200: List of defects with summary
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        defects = inspection.defects.all()
        serializer = InspectionDefectSerializer(defects, many=True)

        # Get summary
        from apps.inspections.services.defect_generator import DefectGenerator
        summary = DefectGenerator.get_defect_summary(inspection)

        return Response({
            'count': defects.count(),
            'defects': serializer.data,
            'summary': summary
        })

    @action(detail=True, methods=['post'])
    def add_defect(self, request, pk=None):
        """
        Add a manual defect to inspection.

        POST /api/inspections/{id}/add_defect/

        Request body:
        {
            "step_key": "step_id",
            "severity": "CRITICAL|MAJOR|MINOR|ADVISORY",
            "title": "Defect title",
            "description": "Defect description",
            "defect_details": {"location": "...", "photos": [...]}
        }

        Returns:
            201: Defect created
            400: Invalid data
            403: Inspection finalized (cannot add defects)
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if inspection is finalized
        if inspection.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot add defects to completed inspection'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate required fields
        step_key = request.data.get('step_key')
        severity = request.data.get('severity')
        title = request.data.get('title')
        description = request.data.get('description', '')

        if not step_key:
            return Response(
                {'error': 'step_key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not severity or severity not in ['CRITICAL', 'MAJOR', 'MINOR', 'ADVISORY']:
            return Response(
                {'error': 'severity must be CRITICAL, MAJOR, MINOR, or ADVISORY'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not title:
            return Response(
                {'error': 'title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate defect_identity for manual defects
        import hashlib
        identity_string = f"{inspection.id}_{step_key}_manual_{title}_{datetime.now().isoformat()}"
        defect_identity = hashlib.sha256(identity_string.encode()).hexdigest()

        # Create defect
        defect = InspectionDefect.objects.create(
            inspection_run=inspection,
            defect_identity=defect_identity,
            module_key='',
            step_key=step_key,
            rule_id=None,  # None indicates manual defect
            severity=severity,
            status='OPEN',
            title=title,
            description=description,
            defect_details=request.data.get('defect_details', {}),
            evaluation_trace={}
        )

        serializer = InspectionDefectSerializer(defect)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def review(self, request, pk=None):
        """
        Get inspection review data (read-only view of completed inspection).

        GET /api/inspections/{id}/review/

        Returns inspection with all step responses formatted for display.
        Intended for review after completion before finalization.

        Returns:
            200: Inspection review data
            404: Inspection not found
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get full inspection details
        serializer = InspectionRunDetailSerializer(inspection)
        inspection_data = serializer.data

        # Get completion status
        completion_status = InspectionRuntime.calculate_completion_status(inspection)

        # Get defects with summary
        defects = inspection.defects.all()
        defect_serializer = InspectionDefectSerializer(defects, many=True)

        from apps.inspections.services.defect_generator import DefectGenerator
        defect_summary = DefectGenerator.get_defect_summary(inspection)

        return Response({
            'inspection': inspection_data,
            'completion': completion_status.to_dict(),
            'defects': {
                'count': defects.count(),
                'items': defect_serializer.data,
                'summary': defect_summary
            }
        })

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """
        Export inspection as PDF report.

        GET /api/inspections/{id}/export_pdf/

        Returns:
            200: PDF file download
            404: Inspection not found
            500: PDF generation failed
        """
        try:
            inspection = self.get_queryset().get(pk=pk)
        except InspectionRun.DoesNotExist:
            return Response(
                {'error': 'Inspection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            from .services.pdf_export_service import InspectionPDFExporter

            # Generate PDF
            exporter = InspectionPDFExporter(inspection)
            pdf_buffer = exporter.generate()

            # Create HTTP response with PDF
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')

            # Set filename
            filename = f"inspection_{inspection.id}_{inspection.template_key}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], parser_classes=[rest_framework.parsers.MultiPartParser, rest_framework.parsers.FormParser])
    def upload_photo(self, request, pk=None):
        """
        Upload photo to inspection.

        POST /api/inspections/{id}/upload_photo/

        Body (multipart/form-data):
        - image: Image file (required)
        - step_key: Step where photo was captured (required)
        - defect_id: Defect ID if photo is evidence (optional)
        - caption: Photo caption (optional)

        Returns:
            201: Photo uploaded successfully with URLs
            400: Validation error
            403: Cannot edit completed inspection
            404: Inspection not found

        Example Response:
        {
            "id": "uuid",
            "url": "/media/inspections/.../photo.jpg",
            "thumbnail_url": "/media/inspections/.../thumb_photo.jpg",
            "caption": "Crack in boom",
            "file_size": 1024000,
            "width": 1920,
            "height": 1080,
            "created_at": "2026-03-16T10:00:00Z"
        }
        """
        from .models import InspectionPhoto
        from .serializers import PhotoUploadSerializer, InspectionPhotoSerializer

        inspection = self.get_object()

        # Validate upload data
        serializer = PhotoUploadSerializer(
            data=request.data,
            context={'inspection': inspection}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create photo
        photo = InspectionPhoto.objects.create(
            inspection=inspection,
            step_key=serializer.validated_data['step_key'],
            defect=serializer.validated_data.get('defect'),
            image=serializer.validated_data['image'],
            caption=serializer.validated_data.get('caption', ''),
            uploaded_by=request.user
        )

        # Return photo data with URLs
        photo_serializer = InspectionPhotoSerializer(photo)
        return Response(photo_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """
        List all photos for inspection.

        GET /api/inspections/{id}/photos/

        Query parameters:
        - step_key: Filter by step (optional)
        - defect_id: Filter by defect (optional)

        Returns:
            200: List of photos with URLs

        Example Response:
        {
            "count": 5,
            "photos": [
                {
                    "id": "uuid",
                    "url": "/media/...",
                    "thumbnail_url": "/media/...",
                    "step_key": "visual_inspection",
                    ...
                }
            ]
        }
        """
        from .serializers import InspectionPhotoSerializer

        inspection = self.get_object()
        photos = inspection.photos.all()

        # Filter by step_key
        step_key = request.query_params.get('step_key')
        if step_key:
            photos = photos.filter(step_key=step_key)

        # Filter by defect
        defect_id = request.query_params.get('defect_id')
        if defect_id:
            photos = photos.filter(defect_id=defect_id)

        serializer = InspectionPhotoSerializer(photos, many=True)
        return Response({
            'count': len(serializer.data),
            'photos': serializer.data
        })

    @action(detail=True, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        """
        Delete a photo.

        DELETE /api/inspections/{id}/photos/{photo_id}/

        Returns:
            204: Photo deleted
            403: Cannot delete from completed inspection
            404: Photo not found
        """
        from .models import InspectionPhoto

        inspection = self.get_object()

        try:
            photo = InspectionPhoto.objects.get(id=photo_id, inspection=inspection)
        except InspectionPhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if inspection.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot delete photos from completed inspection'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete photo (model will handle file cleanup)
        photo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
