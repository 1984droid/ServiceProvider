"""
Inspection PDF Export Service

Generates professional PDF reports for completed inspections.
"""

from datetime import datetime
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from apps.inspections.models import InspectionRun


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
        """Build defects summary section."""
        elements = []

        defects = self.inspection.defects.all().order_by('-severity', 'title')

        elements.append(Paragraph(
            f"Defects Found ({defects.count()})",
            self.styles['SectionHeader']
        ))

        if not defects.exists():
            elements.append(Paragraph("No defects found", self.styles['ReportBody']))
            return elements

        # Build defects table
        data = [['Severity', 'Location', 'Issue', 'Status']]

        for defect in defects:
            severity_color = self._get_severity_color(defect.severity)
            data.append([
                defect.get_severity_display(),
                defect.module_key or 'General',
                defect.title,
                defect.get_status_display()
            ])

        table = Table(data, colWidths=[1*inch, 1.5*inch, 2.5*inch, 1*inch])
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

    def _build_inspection_steps(self):
        """Build inspection steps section (simplified)."""
        elements = []

        elements.append(Paragraph("Inspection Data", self.styles['SectionHeader']))

        # Get step data from inspection
        step_data = self.inspection.step_data or {}

        if not step_data:
            elements.append(Paragraph("No step data recorded", self.styles['ReportBody']))
            return elements

        # Display step data summary
        elements.append(Paragraph(
            f"Total data points collected: {len(step_data)}",
            self.styles['ReportBody']
        ))

        return elements

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
