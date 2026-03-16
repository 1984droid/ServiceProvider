"""
Defect to Work Order Service

Automates work order generation from inspection defects.
Maps defects to vocabulary-based work order line items.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.db import transaction
from apps.inspections.models import InspectionDefect, InspectionRun
from apps.work_orders.models import WorkOrder, WorkOrderLine
from apps.work_orders.services.vocabulary_service import VocabularyService


class DefectToWorkOrderService:
    """
    Service for generating work orders from inspection defects.

    Mapping Strategy:
    1. Direct catalog mapping from JSON seed map
    2. Rule-based extraction from step_key and defect description
    3. Fallback to generic vocabulary

    Data Source:
    - data/work_order_catalogs/inspection_defect_to_work_order_seed_map_ansi_a92_2_2021.json
    """

    _mapping_cache = None
    _base_path = os.path.join(settings.BASE_DIR, 'data', 'work_order_catalogs')

    @classmethod
    def load_defect_mapping(cls, force_reload: bool = False) -> Dict[str, Dict]:
        """
        Load defect-to-work-order mapping from JSON catalog.

        Args:
            force_reload: Force reload from file (bypass cache)

        Returns:
            Dict mapping defect patterns to vocabulary
        """
        if cls._mapping_cache is not None and not force_reload:
            return cls._mapping_cache

        mapping_path = os.path.join(
            cls._base_path,
            'inspection_defect_to_work_order_seed_map_ansi_a92_2_2021.json'
        )

        if os.path.exists(mapping_path):
            with open(mapping_path, 'r') as f:
                cls._mapping_cache = json.load(f)
        else:
            # Cache empty mapping if file doesn't exist
            cls._mapping_cache = {}

        return cls._mapping_cache

    @classmethod
    def map_defect_to_vocabulary(
        cls,
        defect: InspectionDefect
    ) -> Dict[str, str]:
        """
        Map inspection defect to work order vocabulary (verb/noun/location).

        Strategy:
        1. Look up in catalog by step_key or rule_id
        2. Extract from defect title/description
        3. Fallback to generic mapping based on severity

        Args:
            defect: InspectionDefect instance

        Returns:
            Dict with keys: verb, noun, service_location, description
        """
        # Build base description (include both title and description if both exist)
        if defect.title and defect.description and defect.title != defect.description:
            base_description = f"{defect.title}\n\n{defect.description}"
        else:
            base_description = defect.description or defect.title

        # Add standard reference if available
        defect_details = defect.defect_details or {}
        standard_ref = defect_details.get('standard_reference')
        if standard_ref:
            base_description = f"{base_description}\n\nStandard: {standard_ref}"

        # Try catalog mapping first
        mapping = cls.load_defect_mapping()

        # Try step_key lookup
        if defect.step_key and defect.step_key in mapping:
            catalog_entry = mapping[defect.step_key]
            return {
                'verb': catalog_entry.get('verb', 'Inspect'),
                'noun': catalog_entry.get('noun', 'Component'),
                'service_location': catalog_entry.get('service_location', 'General'),
                'description': base_description
            }

        # Try rule_id lookup
        if defect.rule_id and defect.rule_id in mapping:
            catalog_entry = mapping[defect.rule_id]
            return {
                'verb': catalog_entry.get('verb', 'Inspect'),
                'noun': catalog_entry.get('noun', 'Component'),
                'service_location': catalog_entry.get('service_location', 'General'),
                'description': base_description
            }

        # Fallback: Rule-based extraction from title/description
        return cls._extract_vocabulary_from_text(defect, base_description)

    @classmethod
    def _extract_vocabulary_from_text(cls, defect: InspectionDefect, description: str = None) -> Dict[str, str]:
        """
        Extract vocabulary from defect title/description using keyword matching.

        Args:
            defect: InspectionDefect instance
            description: Pre-built description (optional, will build if not provided)

        Returns:
            Dict with keys: verb, noun, service_location, description
        """
        text = f"{defect.title} {defect.description}".lower()

        # Use VocabularyService to suggest vocabulary
        suggestions = VocabularyService.suggest_vocabulary(text)

        # Pick first suggestion or fallback
        verb = suggestions['verbs'][0] if suggestions['verbs'] else cls._default_verb_for_severity(defect.severity)
        noun = suggestions['nouns'][0] if suggestions['nouns'] else 'Component'
        location = suggestions['locations'][0] if suggestions['locations'] else cls._default_location_from_module(defect.module_key)

        # Use provided description or build one
        if description is None:
            # Include both title and description if both exist
            if defect.title and defect.description and defect.title != defect.description:
                description = f"{defect.title}\n\n{defect.description}"
            else:
                description = defect.description or defect.title

            defect_details = defect.defect_details or {}
            standard_ref = defect_details.get('standard_reference')
            if standard_ref:
                description = f"{description}\n\nStandard: {standard_ref}"

        return {
            'verb': verb,
            'noun': noun,
            'service_location': location,
            'description': description
        }

    @classmethod
    def _default_verb_for_severity(cls, severity: str) -> str:
        """
        Get default verb based on defect severity.

        Args:
            severity: Defect severity (CRITICAL, MAJOR, MINOR, ADVISORY)

        Returns:
            Default verb
        """
        severity_verb_map = {
            'CRITICAL': 'Replace',
            'MAJOR': 'Repair',
            'MINOR': 'Adjust',
            'ADVISORY': 'Inspect'
        }
        return severity_verb_map.get(severity, 'Inspect')

    @classmethod
    def _default_location_from_module(cls, module_key: str) -> str:
        """
        Extract service location from module key.

        Args:
            module_key: Module key like 'boom_inspection', 'chassis_inspection'

        Returns:
            Service location
        """
        if not module_key:
            return 'General'

        # Simple mapping based on common module patterns
        module_lower = module_key.lower()

        if 'boom' in module_lower:
            return 'Boom Assembly'
        elif 'chassis' in module_lower or 'vehicle' in module_lower:
            return 'Chassis'
        elif 'turret' in module_lower:
            return 'Turret Assembly'
        elif 'outrigger' in module_lower:
            return 'Outrigger System'
        elif 'hydraulic' in module_lower:
            return 'Hydraulic System'
        elif 'electrical' in module_lower or 'control' in module_lower:
            return 'Electrical System'
        else:
            return 'General'

    @classmethod
    @transaction.atomic
    def generate_work_order_from_defect(
        cls,
        defect: InspectionDefect,
        department_id: Optional[str] = None,
        auto_approve: bool = False
    ) -> WorkOrder:
        """
        Generate a work order from a single defect.

        Args:
            defect: InspectionDefect to convert
            department_id: Department to assign work order to
            auto_approve: Automatically approve work order

        Returns:
            Created WorkOrder instance

        Raises:
            ValueError: If defect already has work order
        """
        # Check if defect already has work order
        existing_wo = WorkOrder.objects.filter(
            source_type='INSPECTION_DEFECT',
            source_id=defect.id
        ).first()

        if existing_wo:
            raise ValueError(f"Defect {defect.id} already has work order {existing_wo.id}")

        # Get inspection and asset
        inspection = defect.inspection_run
        asset = inspection.asset
        customer = inspection.customer

        # Map defect to vocabulary
        vocab = cls.map_defect_to_vocabulary(defect)

        # Build comprehensive description from defect data
        work_description = cls._build_work_description(defect, vocab)

        # Create work order
        wo = WorkOrder.objects.create(
            customer=customer,
            asset_type=inspection.asset_type,
            asset_id=inspection.asset_id,
            department_id=department_id,
            title=f"{vocab['verb']} {vocab['noun']} - {asset}",
            description=work_description,
            priority=cls._map_severity_to_priority(defect.severity),
            source_type='INSPECTION_DEFECT',
            source_id=defect.id,
            status='PENDING',
            approval_status='APPROVED' if auto_approve else 'PENDING_APPROVAL'
        )

        # Create work order line
        WorkOrderLine.objects.create(
            work_order=wo,
            line_number=1,
            verb=vocab['verb'],
            noun=vocab['noun'],
            service_location=vocab['service_location'],
            description=vocab['description'],
            blocks_operation=(defect.severity == 'CRITICAL'),
            status='PENDING'
        )

        # Update defect status
        defect.status = 'WORK_ORDER_CREATED'
        defect.save()

        return wo

    @classmethod
    def _build_work_description(cls, defect: InspectionDefect, vocab: Dict[str, str]) -> str:
        """
        Build comprehensive work order description from defect data.

        Includes all structured defect fields per DATA_CONTRACT.md:
        - Title and description
        - Component
        - Equipment location
        - Standard reference
        - Corrective action
        - Photo count

        Args:
            defect: InspectionDefect instance
            vocab: Vocabulary mapping dict

        Returns:
            Formatted work order description
        """
        parts = []

        # Header
        parts.append(f"DEFECT: {defect.title}")
        parts.append(f"Severity: {defect.get_severity_display()}")
        parts.append("")

        # Description
        if defect.description:
            parts.append("DESCRIPTION:")
            parts.append(defect.description)
            parts.append("")

        # Extract structured defect details
        defect_details = defect.defect_details or {}

        # Component
        component = defect_details.get('component')
        if component:
            parts.append(f"Component: {component}")

        # Equipment Location (from defect schema, not module_key)
        location = defect_details.get('location')
        if location:
            parts.append(f"Equipment Location: {location}")

        # Standard Reference (REQUIRED per user specification)
        standard_ref = defect_details.get('standard_reference')
        if standard_ref:
            parts.append(f"Standard Reference: {standard_ref}")

        # Corrective Action
        corrective_action = defect_details.get('corrective_action')
        if corrective_action:
            parts.append("")
            parts.append("CORRECTIVE ACTION:")
            parts.append(corrective_action)

        # Photo Evidence
        photos = defect_details.get('photos', [])
        if photos:
            parts.append("")
            parts.append(f"Photo Evidence: {len(photos)} photo(s) attached to defect record")

        # Inspection context
        parts.append("")
        parts.append(f"Inspection ID: {defect.inspection_run_id}")
        parts.append(f"Step: {defect.step_key}")

        return "\n".join(parts)

    @classmethod
    def _map_severity_to_priority(cls, severity: str) -> str:
        """
        Map defect severity to work order priority.

        Args:
            severity: Defect severity

        Returns:
            Work order priority
        """
        severity_priority_map = {
            'CRITICAL': 'EMERGENCY',
            'MAJOR': 'HIGH',
            'MINOR': 'NORMAL',
            'ADVISORY': 'LOW'
        }
        return severity_priority_map.get(severity, 'NORMAL')

    @classmethod
    @transaction.atomic
    def generate_work_orders_from_inspection(
        cls,
        inspection: InspectionRun,
        group_by_location: bool = True,
        department_id: Optional[str] = None,
        auto_approve: bool = False
    ) -> List[WorkOrder]:
        """
        Generate work orders from ALL defects in an inspection.

        All defects are included regardless of severity. CRITICAL defects
        will have blocks_operation=True on their work order lines.

        Args:
            inspection: InspectionRun instance
            group_by_location: Group defects by service location into single WO
            department_id: Department to assign work orders to
            auto_approve: Automatically approve work orders

        Returns:
            List of created WorkOrder instances
        """
        # Get ALL defects that need work orders (no severity filtering)
        defects = inspection.defects.filter(status='OPEN')

        if not defects.exists():
            return []

        work_orders = []

        if group_by_location:
            # Group defects by service location
            location_groups = cls._group_defects_by_location(defects)

            for location, defect_list in location_groups.items():
                wo = cls._create_grouped_work_order(
                    inspection=inspection,
                    defects=defect_list,
                    location=location,
                    department_id=department_id,
                    auto_approve=auto_approve
                )
                work_orders.append(wo)
        else:
            # Create individual work order for each defect
            for defect in defects:
                try:
                    wo = cls.generate_work_order_from_defect(
                        defect=defect,
                        department_id=department_id,
                        auto_approve=auto_approve
                    )
                    work_orders.append(wo)
                except ValueError:
                    # Defect already has work order, skip
                    continue

        return work_orders

    @classmethod
    def _group_defects_by_location(cls, defects) -> Dict[str, List[InspectionDefect]]:
        """
        Group defects by service location.

        Args:
            defects: QuerySet of InspectionDefect

        Returns:
            Dict mapping location to list of defects
        """
        groups = {}

        for defect in defects:
            vocab = cls.map_defect_to_vocabulary(defect)
            location = vocab['service_location']

            if location not in groups:
                groups[location] = []
            groups[location].append(defect)

        return groups

    @classmethod
    @transaction.atomic
    def _create_grouped_work_order(
        cls,
        inspection: InspectionRun,
        defects: List[InspectionDefect],
        location: str,
        department_id: Optional[str],
        auto_approve: bool
    ) -> WorkOrder:
        """
        Create a single work order with multiple lines from grouped defects.

        Args:
            inspection: InspectionRun instance
            defects: List of defects for this work order
            location: Service location for grouping
            department_id: Department to assign to
            auto_approve: Auto-approve flag

        Returns:
            Created WorkOrder instance
        """
        asset = inspection.asset
        customer = inspection.customer

        # Determine highest priority from defects
        severities = [d.severity for d in defects]
        if 'CRITICAL' in severities:
            priority = 'EMERGENCY'
        elif 'MAJOR' in severities:
            priority = 'HIGH'
        elif 'MINOR' in severities:
            priority = 'NORMAL'
        else:
            priority = 'LOW'

        # Create work order
        wo = WorkOrder.objects.create(
            customer=customer,
            asset_type=inspection.asset_type,
            asset_id=inspection.asset_id,
            department_id=department_id,
            title=f"Inspection Repairs - {location} - {asset}",
            description=f"Work order generated from {len(defects)} defect(s) in inspection {inspection.id}",
            priority=priority,
            source_type='INSPECTION_DEFECT',
            source_id=inspection.id,  # Link to inspection, not individual defect
            status='PENDING',
            approval_status='APPROVED' if auto_approve else 'PENDING_APPROVAL'
        )

        # Create line for each defect
        for idx, defect in enumerate(defects, start=1):
            vocab = cls.map_defect_to_vocabulary(defect)

            # Build detailed line description with all defect data
            line_description = cls._build_line_description(defect, vocab)

            WorkOrderLine.objects.create(
                work_order=wo,
                line_number=idx,
                verb=vocab['verb'],
                noun=vocab['noun'],
                service_location=vocab['service_location'],
                description=line_description,
                blocks_operation=(defect.severity == 'CRITICAL'),
                status='PENDING'
            )

            # Update defect status
            defect.status = 'WORK_ORDER_CREATED'
            defect.save()

        return wo

    @classmethod
    def _build_line_description(cls, defect: InspectionDefect, vocab: Dict[str, str]) -> str:
        """
        Build work order line description with structured defect data.

        Used for grouped work orders where each defect becomes a line item.

        Args:
            defect: InspectionDefect instance
            vocab: Vocabulary mapping dict

        Returns:
            Formatted line description
        """
        parts = []

        # Start with severity and title
        parts.append(f"[{defect.get_severity_display()}] {defect.title}")

        # Add description if present
        if defect.description:
            parts.append(f"  Description: {defect.description}")

        # Extract structured details
        defect_details = defect.defect_details or {}

        # Component
        component = defect_details.get('component')
        if component:
            parts.append(f"  Component: {component}")

        # Equipment Location
        location = defect_details.get('location')
        if location:
            parts.append(f"  Location: {location}")

        # Standard Reference
        standard_ref = defect_details.get('standard_reference')
        if standard_ref:
            parts.append(f"  Standard: {standard_ref}")

        # Corrective Action
        corrective_action = defect_details.get('corrective_action')
        if corrective_action:
            parts.append(f"  Action: {corrective_action}")

        # Photo count
        photos = defect_details.get('photos', [])
        if photos:
            parts.append(f"  Photos: {len(photos)} attached")

        return "\n".join(parts)

    @classmethod
    def get_defect_work_order(cls, defect: InspectionDefect) -> Optional[WorkOrder]:
        """
        Get work order associated with a defect.

        Args:
            defect: InspectionDefect instance

        Returns:
            WorkOrder instance or None
        """
        return WorkOrder.objects.filter(
            source_type='INSPECTION_DEFECT',
            source_id=defect.id
        ).first()

    @classmethod
    def get_inspection_work_orders(cls, inspection: InspectionRun) -> List[WorkOrder]:
        """
        Get all work orders generated from an inspection.

        Args:
            inspection: InspectionRun instance

        Returns:
            List of WorkOrder instances
        """
        # Get work orders linked to inspection
        inspection_wos = list(WorkOrder.objects.filter(
            source_type='INSPECTION_DEFECT',
            source_id=inspection.id
        ))

        # Get work orders linked to individual defects
        defect_ids = inspection.defects.values_list('id', flat=True)
        defect_wos = list(WorkOrder.objects.filter(
            source_type='INSPECTION_DEFECT',
            source_id__in=defect_ids
        ))

        return inspection_wos + defect_wos
