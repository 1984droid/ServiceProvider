"""
Inspection PDF Export Service

Generates professional PDF reports for completed inspections.
"""

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from apps.inspections.models import InspectionRun, InspectionPhoto


class InspectionPDFExporter:
    """
    Service for generating PDF reports from inspection runs.

    Features:
    - Professional header with company info
    - Asset and inspection metadata
    - Step-by-step results with pass/fail indicators
    - Defects summary grouped by severity
    - Inspector signature section
    - Page numbers and timestamps
    """

    # Class-level cache for standard text lookup
    _standard_text_cache = None

    def __init__(self, inspection: InspectionRun):
        """
        Initialize PDF exporter.

        Args:
            inspection: InspectionRun instance to export
        """
        self.inspection = inspection
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self._load_standard_text_cache()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6
        ))

        # Small text
        self.styles.add(ParagraphStyle(
            name='ReportSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=4
        ))

    def _load_standard_text_cache(self):
        """Load ANSI standard text excerpts for reference lookup."""
        if InspectionPDFExporter._standard_text_cache is None:
            try:
                standard_text_path = Path('static/inspection_references/ansi_a92_2_2021/standard_text.json')
                if standard_text_path.exists():
                    with open(standard_text_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Create section -> excerpt mapping
                        excerpts = {}
                        for excerpt_data in data.get('common_excerpts', {}).values():
                            section = excerpt_data.get('section', '')
                            excerpt = excerpt_data.get('excerpt', '')
                            if section and excerpt:
                                excerpts[section] = excerpt
                        InspectionPDFExporter._standard_text_cache = excerpts
                else:
                    InspectionPDFExporter._standard_text_cache = {}
            except Exception:
                # Fail gracefully if standard text not available
                InspectionPDFExporter._standard_text_cache = {}

    def _get_standard_text_for_reference(self, standard_reference: str) -> Optional[str]:
        """
        Look up standard text excerpt for a given standard reference.

        Args:
            standard_reference: Standard reference string (e.g., "ANSI A92.2-2021 Section 8.2.3")

        Returns:
            Standard text excerpt if found, None otherwise
        """
        if not InspectionPDFExporter._standard_text_cache:
            return None

        # Try to find matching section in cache
        for section, excerpt in InspectionPDFExporter._standard_text_cache.items():
            if section in standard_reference:
                # Truncate if too long
                if len(excerpt) > 150:
                    return excerpt[:147] + '...'
                return excerpt

        return None

    def generate(self) -> BytesIO:
        """
        Generate PDF report.

        Returns:
            BytesIO buffer containing PDF data
        """
        # Create document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f"Inspection Report - {self.inspection.id}"
        )

        # Build story (content elements)
        story = []

        # Header
        story.extend(self._build_header())
        story.append(Spacer(1, 0.2*inch))

        # Asset Information
        story.extend(self._build_asset_info())
        story.append(Spacer(1, 0.2*inch))

        # Inspection Metadata
        story.extend(self._build_inspection_metadata())
        story.append(Spacer(1, 0.2*inch))

        # Defects Summary
        if self.inspection.defects.exists():
            story.extend(self._build_defects_summary())
            story.append(Spacer(1, 0.2*inch))

        # Inspection Steps (if template snapshot has steps)
        if self.inspection.template_snapshot:
            story.extend(self._build_inspection_steps())
            story.append(Spacer(1, 0.2*inch))

        # Signature Section
        story.extend(self._build_signature_section())

        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)

        # Reset buffer position
        self.buffer.seek(0)
        return self.buffer

    def _build_header(self):
        """Build report header."""
        elements = []

        # Title
        elements.append(Paragraph(
            "INSPECTION REPORT",
            self.styles['CustomTitle']
        ))

        # Subtitle with template name
        template_name = self.inspection.template_key.replace('_', ' ').title()
        elements.append(Paragraph(
            f"<i>{template_name}</i>",
            self.styles['ReportBody']
        ))

        return elements

    def _build_asset_info(self):
        """Build asset information section."""
        elements = []

        elements.append(Paragraph("Asset Information", self.styles['SectionHeader']))

        asset = self.inspection.asset
        if not asset:
            elements.append(Paragraph("Asset information not available", self.styles['ReportBody']))
            return elements

        # Build asset info table
        data = []

        if self.inspection.asset_type == 'VEHICLE':
            data.extend([
                ['Type:', 'Vehicle'],
                ['VIN:', asset.vin or 'N/A'],
                ['Unit Number:', asset.unit_number or 'N/A'],
                ['Make/Model:', f"{asset.make} {asset.model}" if asset.make else 'N/A'],
                ['Year:', str(asset.year) if asset.year else 'N/A'],
                ['License Plate:', asset.license_plate or 'N/A'],
            ])
        else:  # EQUIPMENT
            data.extend([
                ['Type:', 'Equipment'],
                ['Serial Number:', asset.serial_number or 'N/A'],
                ['Asset Number:', asset.asset_number or 'N/A'],
                ['Equipment Type:', asset.get_equipment_type_display() or 'N/A'],
                ['Manufacturer/Model:', f"{asset.manufacturer} {asset.model}" if asset.manufacturer else 'N/A'],
                ['Year:', str(asset.year) if asset.year else 'N/A'],
            ])

        table = Table(data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(table)

        return elements

    def _build_inspection_metadata(self):
        """Build inspection metadata section."""
        elements = []

        elements.append(Paragraph("Inspection Details", self.styles['SectionHeader']))

        data = [
            ['Status:', self.inspection.get_status_display()],
            ['Started:', self.inspection.started_at.strftime('%Y-%m-%d %H:%M') if self.inspection.started_at else 'N/A'],
            ['Completed:', self.inspection.finalized_at.strftime('%Y-%m-%d %H:%M') if self.inspection.finalized_at else 'In Progress'],
            ['Inspector:', self.inspection.inspector_name or 'Not Specified'],
            ['Customer:', self.inspection.customer.name if self.inspection.customer else 'N/A'],
        ]

        table = Table(data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(table)

        return elements

    def _build_defects_summary(self):
        """
        Build comprehensive defects section.

        Includes:
        - Summary table
        - Detailed breakdown of each defect with all fields
        """
        elements = []

        defects = self.inspection.defects.all().order_by('-severity', 'title')

        elements.append(Paragraph(
            f"Defects Found ({defects.count()})",
            self.styles['SectionHeader']
        ))

        if not defects.exists():
            elements.append(Paragraph("No defects found", self.styles['ReportBody']))
            return elements

        # Summary table
        elements.append(Paragraph("Summary", self.styles['SubSection']))
        data = [['Severity', 'Title', 'Component', 'Location']]

        for defect in defects:
            defect_details = defect.defect_details or {}
            component = defect_details.get('component', 'N/A')
            location = defect_details.get('location', defect.module_key or 'General')

            data.append([
                defect.get_severity_display(),
                defect.title[:50] + ('...' if len(defect.title) > 50 else ''),
                component[:30] + ('...' if len(str(component)) > 30 else ''),
                location[:30] + ('...' if len(str(location)) > 30 else '')
            ])

        table = Table(data, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        # Detailed defect breakdown
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Defect Information", self.styles['SectionHeader']))

        for idx, defect in enumerate(defects, start=1):
            elements.extend(self._build_defect_detail(defect, idx))
            if idx < defects.count():
                elements.append(Spacer(1, 0.15*inch))

        return elements

    def _build_inspection_steps(self):
        """
        Build detailed inspection steps section with template parsing.

        Parses template_snapshot to show:
        - Step titles and labels
        - Responses with proper formatting
        - Pass/fail indicators
        - Grouped by modules
        """
        elements = []

        # Get step data and template
        step_data = self.inspection.step_data or {}
        template_snapshot = self.inspection.template_snapshot or {}

        if not step_data:
            elements.append(Paragraph("Inspection Results", self.styles['SectionHeader']))
            elements.append(Paragraph("No inspection data recorded", self.styles['ReportBody']))
            return elements

        # Parse template structure
        procedure = template_snapshot.get('procedure', {})
        modules = template_snapshot.get('modules', [])

        # Handle both procedure-based and module-based templates
        if procedure and 'steps' in procedure:
            # New procedure-based format
            elements.extend(self._build_procedure_steps(procedure, step_data))
        elif modules:
            # Legacy module-based format
            elements.extend(self._build_module_steps(modules, step_data))
        else:
            # Fallback: raw step data
            elements.extend(self._build_raw_step_data(step_data))

        return elements

    def _build_procedure_steps(self, procedure, step_data):
        """Build steps from procedure-based template."""
        elements = []

        elements.append(Paragraph("Inspection Results", self.styles['SectionHeader']))

        steps = procedure.get('steps', [])
        if not steps:
            elements.append(Paragraph("No steps defined in template", self.styles['ReportBody']))
            return elements

        # Build table header
        data = [['Step', 'Result', 'Status']]

        for step in steps:
            step_key = step.get('step_key')
            title = step.get('title', step_key)
            step_type = step.get('type', '')
            standard_ref = step.get('standard_reference', '')
            standard_text_data = step.get('standard_text', {})

            # Get response from step_data
            response = step_data.get(step_key, 'Not Performed')

            # Format response based on type
            formatted_response = self._format_step_response(response, step)

            # Determine status
            status = self._determine_step_status(response, step)

            # Build step title with standard reference
            step_title_parts = [title]

            # Add standard reference if available
            if standard_ref:
                step_title_parts.append(f"\n<font size=8 color='#7f8c8d'>{standard_ref}</font>")

            # Add standard text excerpt if available
            if standard_text_data and 'excerpt' in standard_text_data:
                excerpt = standard_text_data['excerpt']
                # Truncate if too long
                if len(excerpt) > 150:
                    excerpt = excerpt[:147] + '...'
                step_title_parts.append(f"\n<font size=7 color='#95a5a6'><i>\"{excerpt}\"</i></font>")

            step_title_html = ''.join(step_title_parts)

            # Add to table
            data.append([
                Paragraph(step_title_html, self.styles['ReportBody']),
                formatted_response,
                status
            ])

        # Create table
        table = Table(data, colWidths=[3*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))

        elements.append(table)
        return elements

    def _build_module_steps(self, modules, step_data):
        """Build steps from module-based template (legacy)."""
        elements = []

        elements.append(Paragraph("Inspection Results", self.styles['SectionHeader']))

        for module in modules:
            module_name = module.get('name', 'Unknown Module')
            module_steps = module.get('steps', [])

            if not module_steps:
                continue

            # Module header
            elements.append(Paragraph(module_name, self.styles['SubSection']))

            # Build step table for this module
            data = [['Step', 'Result', 'Status']]

            for step in module_steps:
                step_key = step.get('step_key')
                title = step.get('title', step_key)
                standard_ref = step.get('standard_reference', '')
                standard_text_data = step.get('standard_text', {})

                response = step_data.get(step_key, 'Not Performed')
                formatted_response = self._format_step_response(response, step)
                status = self._determine_step_status(response, step)

                # Build step title with standard reference
                step_title_parts = [title]

                if standard_ref:
                    step_title_parts.append(f"\n<font size=7 color='#7f8c8d'>{standard_ref}</font>")

                if standard_text_data and 'excerpt' in standard_text_data:
                    excerpt = standard_text_data['excerpt']
                    if len(excerpt) > 120:
                        excerpt = excerpt[:117] + '...'
                    step_title_parts.append(f"\n<font size=6 color='#95a5a6'><i>\"{excerpt}\"</i></font>")

                step_title_html = ''.join(step_title_parts)

                data.append([Paragraph(step_title_html, self.styles['ReportBody']), formatted_response, status])

            # Create table
            table = Table(data, colWidths=[3*inch, 2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_raw_step_data(self, step_data):
        """Fallback: display raw step data when template structure unknown."""
        elements = []

        elements.append(Paragraph("Inspection Data", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"Collected {len(step_data)} data points",
            self.styles['ReportBody']
        ))

        # Simple key-value display
        data = [['Step Key', 'Response']]
        for key, value in sorted(step_data.items()):
            formatted_value = self._format_value(value)
            data.append([key, formatted_value])

        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))

        elements.append(table)
        return elements

    def _format_step_response(self, response, step_definition):
        """Format response based on field type."""
        if response is None or response == '':
            return 'N/A'

        field_type = step_definition.get('type', '').upper()

        # Boolean/Pass-Fail
        if isinstance(response, bool):
            return 'PASS' if response else 'FAIL'

        # Handle common string responses
        if isinstance(response, str):
            response_upper = response.upper()
            if response_upper in ['PASS', 'FAIL', 'OK', 'NOT_OK']:
                return response_upper
            if response_upper in ['NOT_PERFORMED', 'N/A', 'SKIPPED']:
                return response

        # Numeric with units
        if isinstance(response, (int, float)) and 'unit' in step_definition:
            unit = step_definition.get('unit', '')
            return f"{response} {unit}"

        # Lists/Arrays
        if isinstance(response, list):
            return ', '.join(str(item) for item in response)

        # Dict/Object
        if isinstance(response, dict):
            # Try to extract meaningful value
            if 'value' in response:
                return str(response['value'])
            if 'result' in response:
                return str(response['result'])
            return str(response)

        return str(response)

    def _determine_step_status(self, response, step_definition):
        """Determine pass/fail/skipped status for a step."""
        if response is None or response == '' or response == 'Not Performed':
            return 'SKIPPED'

        # Boolean
        if isinstance(response, bool):
            return 'PASS' if response else 'FAIL'

        # String responses
        if isinstance(response, str):
            response_upper = response.upper()
            if response_upper in ['PASS', 'OK', 'SAFE', 'NORMAL']:
                return 'PASS'
            if response_upper in ['FAIL', 'NOT_OK', 'UNSAFE', 'DEFECT']:
                return 'FAIL'
            if response_upper in ['NOT_PERFORMED', 'N/A', 'SKIPPED', 'NOT_APPLICABLE']:
                return 'SKIPPED'

        # Check against rules if available
        rules = step_definition.get('rules', [])
        if rules:
            # If there are rules and we have a response, assume PASS unless FAIL detected
            # This is simplified - real rule evaluation would be more complex
            return 'PASS'

        # Default: if we have a response, consider it performed
        return 'DONE'

    def _format_value(self, value):
        """Format any value for display."""
        if value is None:
            return 'N/A'
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, (list, tuple)):
            return ', '.join(str(v) for v in value)
        if isinstance(value, dict):
            return str(value)
        return str(value)

    def _build_signature_section(self):
        """Build signature section."""
        elements = []

        elements.append(Paragraph("Inspector Certification", self.styles['SectionHeader']))

        sig_data = self.inspection.inspector_signature or {}

        if sig_data:
            elements.append(Paragraph(
                f"<b>Signed by:</b> {sig_data.get('name', 'Unknown')}",
                self.styles['ReportBody']
            ))
            if sig_data.get('date'):
                elements.append(Paragraph(
                    f"<b>Date:</b> {sig_data.get('date')}",
                    self.styles['ReportBody']
                ))
        else:
            elements.append(Paragraph(
                "Inspector signature not captured",
                self.styles['ReportSmall']
            ))

        # Signature line
        elements.append(Spacer(1, 0.5*inch))
        sig_line_data = [['_' * 50, '', 'Date: _' * 15]]
        sig_table = Table(sig_line_data, colWidths=[3*inch, 0.5*inch, 2.5*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#7f8c8d')),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(sig_table)

        return elements

    def _build_defect_detail(self, defect, defect_number: int):
        """
        Build detailed breakdown for a single defect.

        Shows all 8 structured defect fields per DATA_CONTRACT.md:
        - Title, severity, description
        - Component, location
        - Standard reference
        - Corrective action
        - Photo evidence count

        Args:
            defect: InspectionDefect instance
            defect_number: Sequential defect number

        Returns:
            List of reportlab elements
        """
        elements = []

        # Defect header with severity color
        severity_color = self._get_severity_color(defect.severity)
        header_style = ParagraphStyle(
            name=f'DefectHeader{defect_number}',
            parent=self.styles['SubSection'],
            textColor=severity_color,
            fontSize=11,
            spaceAfter=6
        )

        elements.append(Paragraph(
            f"Defect #{defect_number}: [{defect.get_severity_display()}] {defect.title}",
            header_style
        ))

        # Build defect detail table
        defect_details = defect.defect_details or {}
        data = []

        # Severity
        data.append(['Severity:', defect.get_severity_display()])

        # Description
        if defect.description:
            data.append(['Description:', defect.description])

        # Component
        component = defect_details.get('component')
        if component:
            data.append(['Component:', component])

        # Equipment Location
        location = defect_details.get('location')
        if location:
            data.append(['Equipment Location:', location])
        elif defect.module_key:
            data.append(['Module:', defect.module_key])

        # Standard Reference (REQUIRED field)
        standard_ref = defect_details.get('standard_reference')
        if standard_ref:
            # Try to add standard text excerpt if available
            standard_text_excerpt = self._get_standard_text_for_reference(standard_ref)
            if standard_text_excerpt:
                ref_with_excerpt = f"{standard_ref}\n\"{standard_text_excerpt}\""
                data.append(['Standard Reference:', ref_with_excerpt])
            else:
                data.append(['Standard Reference:', standard_ref])

        # Corrective Action
        corrective_action = defect_details.get('corrective_action')
        if corrective_action:
            data.append(['Corrective Action:', corrective_action])

        # Status
        data.append(['Status:', defect.get_status_display()])

        # Inspection context
        data.append(['Step:', defect.step_key])

        # Create table
        detail_table = Table(data, colWidths=[1.5*inch, 4.5*inch])
        detail_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))

        elements.append(detail_table)

        # Add photo evidence thumbnails if available
        photo_grid = self._build_photo_grid(defect)
        if photo_grid:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"Photo Evidence ({len(defect.photos.all())} photo(s)):",
                self.styles['ReportSmall']
            ))
            elements.append(Spacer(1, 0.05*inch))
            elements.extend(photo_grid)

        return elements

    def _build_photo_grid(self, defect):
        """
        Build a grid of photo thumbnails for a defect.

        Limits to 3 photos maximum to keep PDF file size reasonable.
        Uses thumbnails (300x300) for optimal file size.

        Args:
            defect: InspectionDefect instance

        Returns:
            List of reportlab elements or None if no photos
        """
        import os
        from django.conf import settings

        # Get photos for this defect
        photos = defect.photos.all()[:3]  # Limit to 3 photos

        if not photos:
            return None

        elements = []
        photo_images = []

        # Build Image objects for each photo
        for photo in photos:
            try:
                # Use thumbnail if available, otherwise original
                image_path = photo.thumbnail.path if photo.thumbnail else photo.image.path

                # Check if file exists
                if not os.path.exists(image_path):
                    continue

                # Create reportlab Image with fixed size (2 inches wide, maintaining aspect ratio)
                img = Image(image_path, width=2*inch, height=2*inch)
                photo_images.append(img)

            except Exception as e:
                # Skip photos that can't be loaded
                continue

        if not photo_images:
            return None

        # Create a table to display photos in a row (up to 3 photos per row)
        # Calculate dynamic column widths based on number of photos
        num_photos = len(photo_images)
        col_width = 2*inch
        spacing = 0.2*inch

        if num_photos == 1:
            # Single photo, centered
            photo_table = Table([[photo_images[0]]], colWidths=[col_width])
        elif num_photos == 2:
            # Two photos side by side
            photo_table = Table([photo_images], colWidths=[col_width, col_width])
        else:
            # Three photos in a row
            photo_table = Table([photo_images], colWidths=[col_width, col_width, col_width])

        photo_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), spacing/2),
            ('RIGHTPADDING', (0, 0), (-1, -1), spacing/2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        elements.append(photo_table)

        # Add note if more photos exist
        total_photos = defect.photos.count()
        if total_photos > 3:
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(
                f"<i>({total_photos - 3} additional photo(s) not shown)</i>",
                self.styles['ReportSmall']
            ))

        return elements

    def _get_severity_color(self, severity: str) -> colors.Color:
        """Get color for severity level."""
        severity_colors = {
            'CRITICAL': colors.HexColor('#e74c3c'),
            'MAJOR': colors.HexColor('#e67e22'),
            'MINOR': colors.HexColor('#f39c12'),
            'ADVISORY': colors.HexColor('#3498db'),
        }
        return severity_colors.get(severity, colors.HexColor('#95a5a6'))

    def _add_page_number(self, canvas, doc):
        """Add page number and footer to each page."""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawRightString(
            7.5*inch,
            0.5*inch,
            text
        )
        # Add generated timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        canvas.drawString(
            0.75*inch,
            0.5*inch,
            f"Generated: {timestamp}"
        )
        canvas.restoreState()
