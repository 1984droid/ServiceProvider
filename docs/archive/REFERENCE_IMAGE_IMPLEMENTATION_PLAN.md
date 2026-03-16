# Reference Image Implementation Plan

## Overview
Add support for displaying reference images (ANSI figures/tables) during inspection steps to help inspectors identify defects and understand requirements.

## Use Cases

### Primary Use Cases
1. **Dielectric Test Setup** - Show test configuration diagrams (Figures 1, 2, 3, 4)
2. **Weld Inspection** - Reference weld types and inspection points
3. **Bolts/Fasteners** - Show proper torque patterns and inspection criteria
4. **Load Test** - Display boom positioning for tests (Figure 4)
5. **Bonding Arrangements** - Show electrical bonding for Category A devices (Figure 5)
6. **Test Values** - Display Tables 1-3 for voltage/current thresholds

### Example Scenarios
- Inspector performing dielectric test needs to reference Figure 1A (lower test electrode assembly)
- Inspector checking welds needs to see what constitutes a crack vs. acceptable weld
- Inspector performing load test needs to position boom per Figure 4

---

## Technical Design

### 1. Template Schema Extension

Add `reference_images` array to `ProcedureStep` schema:

```python
# apps/inspections/schemas/template_schema.py

class ReferenceImage(BaseModel):
    """Reference image for inspection guidance."""
    image_id: str = Field(..., description="Unique identifier (e.g., 'figure_1a')")
    title: str = Field(..., description="Image title (e.g., 'Figure 1A: Lower Test Electrode')")
    file_path: str = Field(..., description="Path relative to static/inspection_references/")
    caption: Optional[str] = Field(None, description="Optional detailed caption")
    display_mode: Literal["inline", "modal", "both"] = Field(
        default="modal",
        description="How to display: inline (always visible), modal (click to view), both"
    )
    figure_number: Optional[str] = Field(None, description="ANSI figure/table number (e.g., 'Figure 1A')")

class ProcedureStep(BaseModel):
    """A single step in an inspection procedure."""
    # ... existing fields ...
    reference_images: Optional[List[ReferenceImage]] = Field(
        default=None,
        description="Reference images/diagrams for this step"
    )
```

### 2. Template JSON Format

```json
{
  "step_key": "dielectric_test_ac_method",
  "title": "AC Dielectric Test (Method A)",
  "type": "MEASUREMENT",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.1",
  "reference_images": [
    {
      "image_id": "figure_1",
      "title": "Figure 1: Test Configuration for Category A & B",
      "file_path": "ansi_a92_2_2021/figure_1_dielectric_test_config.png",
      "caption": "Dielectric test configuration showing electrode placement and grounding",
      "display_mode": "both",
      "figure_number": "Figure 1"
    },
    {
      "image_id": "figure_1a",
      "title": "Figure 1A: Lower Test Electrode Details",
      "file_path": "ansi_a92_2_2021/figure_1a_electrode_assembly.png",
      "display_mode": "modal",
      "figure_number": "Figure 1A"
    },
    {
      "image_id": "table_2",
      "title": "Table 2: Periodic Electrical Test Values",
      "file_path": "ansi_a92_2_2021/table_2_periodic_test_values.png",
      "caption": "Reference voltage and current limits for periodic testing",
      "display_mode": "inline",
      "figure_number": "Table 2"
    }
  ],
  "fields": [...]
}
```

### 3. Static File Organization

```
static/
└── inspection_references/
    └── ansi_a92_2_2021/
        ├── figures/
        │   ├── figure_1_dielectric_test_config.png
        │   ├── figure_1a_electrode_assembly.png
        │   ├── figure_2_cat_c_d_test_config.png
        │   ├── figure_2a_optional_test_config.png
        │   ├── figure_3_chassis_insulating.png
        │   ├── figure_3a_shunting_arrangement.png
        │   ├── figure_4_boom_positions.png
        │   ├── figure_5_bonding_arrangements.png
        │   ├── figure_6_upper_control_test.png
        │   └── figure_7_identification_plate.png
        ├── tables/
        │   ├── table_1_design_test_values.png
        │   ├── table_2_periodic_test_values.png
        │   └── table_3_before_use_tests.png
        └── README.md  # Instructions for adding new images
```

### 4. Frontend Components

#### A. ReferenceImageViewer Component

```typescript
// frontend/src/features/inspections/components/ReferenceImageViewer.tsx

interface ReferenceImage {
  image_id: string;
  title: string;
  file_path: string;
  caption?: string;
  display_mode: 'inline' | 'modal' | 'both';
  figure_number?: string;
}

interface Props {
  images: ReferenceImage[];
  mode: 'inline' | 'modal';
}

export function ReferenceImageViewer({ images, mode }: Props) {
  // Inline mode: display images directly in step
  // Modal mode: show thumbnails, click to enlarge
  // Support zooming, downloading
}
```

#### B. Integration in InspectionExecutePage

```typescript
// frontend/src/features/inspections/InspectionExecutePage.tsx

function StepContent({ step }) {
  const referenceImages = step.reference_images || [];

  // Separate inline vs modal images
  const inlineImages = referenceImages.filter(
    img => img.display_mode === 'inline' || img.display_mode === 'both'
  );
  const modalImages = referenceImages.filter(
    img => img.display_mode === 'modal' || img.display_mode === 'both'
  );

  return (
    <>
      {/* Step title and description */}

      {/* Inline reference images */}
      {inlineImages.length > 0 && (
        <div className="my-4 border rounded-lg p-4 bg-blue-50">
          <h4 className="font-medium mb-2">Reference Diagrams</h4>
          <ReferenceImageViewer images={inlineImages} mode="inline" />
        </div>
      )}

      {/* Step fields */}

      {/* Modal reference images button */}
      {modalImages.length > 0 && (
        <button
          onClick={() => openImageModal(modalImages)}
          className="flex items-center gap-2 text-blue-600"
        >
          <ImageIcon />
          View Reference Images ({modalImages.length})
        </button>
      )}
    </>
  );
}
```

### 5. Image Modal with Zoom

Features:
- Full-screen modal
- Zoom in/out (pinch, scroll, buttons)
- Pan when zoomed
- Download image
- Navigate between multiple images
- Keyboard shortcuts (arrow keys, ESC, +/-)

---

## Implementation Steps

### Phase 1: Schema & Backend (30 min)
1. ✅ Update `template_schema.py` - Add `ReferenceImage` model
2. ✅ Add `reference_images` field to `ProcedureStep`
3. ✅ Create directory structure in `static/inspection_references/`
4. ✅ Add README with instructions for image format/size guidelines

### Phase 2: Frontend Components (60 min)
1. ✅ Create `ReferenceImageViewer.tsx` component
2. ✅ Create `ReferenceImageModal.tsx` with zoom/pan
3. ✅ Integrate into `InspectionExecutePage.tsx`
4. ✅ Add responsive design (mobile-friendly)
5. ✅ Test with sample images

### Phase 3: Template Updates (15 min)
1. ✅ Add reference images to dielectric test steps
2. ✅ Document pattern for other templates
3. ✅ Test end-to-end flow

---

## Image Requirements

### Format
- **Type**: PNG (preferred) or JPG
- **Resolution**: 1200-2000px width (high-DPI displays)
- **File size**: < 500KB per image (optimize with pngcrush/tinypng)
- **Color**: Grayscale or minimal color (easier to read)

### Content
- Clear, readable text (minimum 12pt equivalent)
- High contrast (black text on white background)
- Annotations/callouts where helpful
- Scale indicators if needed

### Naming Convention
```
figure_{number}_{description}.png
table_{number}_{description}.png

Examples:
- figure_1_dielectric_test_config.png
- figure_1a_electrode_assembly.png
- table_2_periodic_test_values.png
```

---

## Benefits

1. **Better Compliance** - Inspectors reference exact ANSI diagrams
2. **Reduced Errors** - Visual guides prevent misinterpretation
3. **Faster Training** - New inspectors learn correct procedures
4. **Professional Documentation** - PDFs can include referenced figures
5. **Offline Capability** - Images bundled with app, no internet needed

---

## Future Enhancements

- **Annotated Images**: Allow inspectors to mark up images with findings
- **Video References**: Support MP4/WEBM for procedural videos
- **3D Models**: Interactive 3D views of equipment components
- **AR Overlay**: Augmented reality to highlight inspection points
