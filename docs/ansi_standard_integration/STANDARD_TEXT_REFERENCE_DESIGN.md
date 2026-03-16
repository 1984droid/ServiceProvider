# Standard Text Reference System - Design Document

## Overview

Make ANSI A92.2-2021 standard text available to inspectors during inspection execution, providing context and guidance for each inspection step.

---

## Use Cases

### 1. **Inspector Needs Context**
- Inspector is performing "Operating Controls Test"
- Wants to see exact ANSI requirements: Section 8.2.3(2)
- Needs to understand what constitutes a pass/fail

### 2. **Inspector Training**
- New inspector learning the inspection process
- Reads standard text alongside step instructions
- Understands **why** they're checking specific items

### 3. **Compliance Documentation**
- Inspector documents defect
- System automatically captures ANSI section reference
- PDF report shows: "Per ANSI A92.2-2021 Section 8.2.3(2)..."

---

## Proposed Solution

### Option A: **Embedded Standard Text in Templates** ✅ RECOMMENDED

Add `standard_text` field to template steps with relevant ANSI section content.

**Pros:**
- Always available (no external file dependency)
- Fast (no parsing/loading required)
- Version-controlled with templates
- Can be edited/simplified for clarity

**Cons:**
- Duplication of content
- Manual maintenance if standard updates

**Example:**
```json
{
  "step_key": "operating_controls_test",
  "step_number": 2,
  "title": "Operating Controls Test",
  "instructions": "Test all boom operating controls...",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.3(2)",
  "standard_text": {
    "section": "8.2.3(2)",
    "title": "Frequent Inspection - Operating Controls",
    "content": "Performance test of all boom movements.",
    "full_section_available": true
  },
  "reference_images": [...]
}
```

### Option B: **Extracted Standard Text Database**

Extract ANSI sections into JSON/database, reference by section number.

**Pros:**
- Single source of truth
- Easy to update standard
- Can serve full text on demand

**Cons:**
- More complex infrastructure
- Parsing complexity
- Copyright considerations

**Example Structure:**
```json
{
  "sections": {
    "8.2.3": {
      "title": "Frequent Inspection",
      "subsections": {
        "1": "Structural members for deformation, cracks, or corrosion.",
        "2": "Performance test of all boom movements.",
        "3": "Safety devices test...",
        ...
      }
    }
  }
}
```

### Option C: **Hybrid Approach** ✅ BEST LONG-TERM

- **Short excerpt** embedded in template (1-2 sentences)
- **Full section** available via API/modal
- **Standard text file** extracted from DOCX for reference

**Benefits:**
- Lightweight templates
- Full text available when needed
- Easy updates

---

## Recommended Implementation (Option C - Hybrid)

### 1. Extract Standard Sections from DOCX

Script: `scripts/extract_standard_text.py`

Output: `static/inspection_references/ansi_a92_2_2021/standard_text.json`

```json
{
  "standard": "ANSI A92.2-2021",
  "title": "Vehicle-Mounted Elevating and Rotating Aerial Devices",
  "sections": {
    "5.4.2": {
      "title": "Qualification Test Procedures",
      "content": "Full section text here...",
      "subsections": {
        "5.4.2.1": "Test criteria of Table 1 shall be followed...",
        "5.4.2.2": "Category C, D and E...",
        ...
      }
    },
    "8.2.3": {
      "title": "Frequent Inspection",
      "content": "Items to be inspected daily to monthly intervals...",
      "items": [
        "Structural members for deformation, cracks, or corrosion.",
        "Performance test of all boom movements.",
        "Safety devices test...",
        ...
      ]
    },
    "8.2.4": {
      "title": "Periodic Inspection",
      "content": "Inspection at 1-12 month intervals...",
      "items": [...]
    }
  }
}
```

### 2. Extend Template Schema

Add `standard_text_ref` to ProcedureStep:

```python
class StandardTextReference(BaseModel):
    """Reference to ANSI standard section."""

    section: str = Field(..., description="Section number (e.g., '8.2.3(2)')")
    excerpt: Optional[str] = Field(
        default=None,
        description="Short excerpt (1-2 sentences) shown inline"
    )
    show_full_section: bool = Field(
        default=False,
        description="If true, make full section available via modal"
    )

class ProcedureStep(BaseModel):
    # ... existing fields ...

    standard_text_ref: Optional[StandardTextReference] = Field(
        default=None,
        description="ANSI standard text reference for this step"
    )
```

### 3. Template Usage Example

```json
{
  "step_key": "hydraulic_system_inspection",
  "step_number": 4,
  "title": "Hydraulic System Inspection",
  "instructions": "Inspect hydraulic system for proper oil level, leaks, and damage.",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.4(4)-(6)",
  "standard_text_ref": {
    "section": "8.2.4(4)-(6)",
    "excerpt": "Hydraulic system for proper oil level. Hydraulic fittings, hoses, and tubing for evidence of leakage, abnormal deformation, or excessive abrasion.",
    "show_full_section": true
  },
  "reference_images": [
    {
      "image_id": "figure_3",
      "title": "Figure 3: Hydraulic System Components",
      "file_path": "ansi_a92_2_2021/figures/figure_3_chassis_insulating_systems.png",
      "display_mode": "modal"
    }
  ]
}
```

### 4. Frontend Display

**Inline (always visible):**
```
┌─────────────────────────────────────────────────┐
│ Step 4: Hydraulic System Inspection             │
├─────────────────────────────────────────────────┤
│ Inspect hydraulic system for proper oil level,  │
│ leaks, and damage.                              │
│                                                  │
│ 📖 ANSI A92.2-2021 Section 8.2.4(4)-(6)        │
│ "Hydraulic system for proper oil level.         │
│ Hydraulic fittings, hoses, and tubing for       │
│ evidence of leakage, abnormal deformation, or   │
│ excessive abrasion."                             │
│                                                  │
│ [View Full Section] [View Figure 3]             │
└─────────────────────────────────────────────────┘
```

**Modal (click to expand):**
```
┌───────────────────────────────────────────────────┐
│ ANSI A92.2-2021 Section 8.2.4                     │
│ Periodic Inspection                               │
├───────────────────────────────────────────────────┤
│                                                   │
│ An inspection of the mobile unit (MEWP) shall be │
│ performed at the intervals defined in 8.2.2       │
│ depending upon its activity, severity of service, │
│ and environment...                                │
│                                                   │
│ (4) Hydraulic system for proper oil level.       │
│ (5) Hydraulic and pneumatic fittings, hoses,     │
│     and tubing for evidence of leakage, abnormal  │
│     deformation, or excessive abrasion.           │
│ (6) Compressors, pumps, motors, and generators   │
│     for loose fasteners, leaks, unusual noises... │
│                                                   │
│ [Close]                                           │
└───────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Extract Standard Text
1. Create `scripts/extract_standard_text.py`
2. Parse ANSI DOCX by section numbers
3. Output `standard_text.json`

### Phase 2: Schema Extension
1. Add `StandardTextReference` to `template_schema.py`
2. Add `standard_text_ref` to `ProcedureStep`
3. Update template validation

### Phase 3: Template Updates
1. Add standard text references to frequent inspection template
2. Add standard text references to periodic inspection template
3. Add standard text references to dielectric test template

### Phase 4: Frontend Implementation
1. Display inline excerpts on inspection execution page
2. Add "View Full Section" modal
3. Add "View Standard Text" button to each step

### Phase 5: PDF Integration
1. Include standard text excerpts in PDF reports
2. Add "Compliance References" section to PDF
3. Show standard text alongside defects

---

## Copyright Considerations

⚠️ **Important:** ANSI A92.2-2021 is a copyrighted standard.

**Allowed:**
- Short excerpts for compliance purposes
- Section references and citations
- Paraphrasing requirements

**Not Allowed:**
- Reproducing entire standard
- Distributing full standard text to unauthorized users

**Recommendation:**
- Limit excerpts to 1-2 sentences per step
- Require users to have valid ANSI standard access
- Full standard text available only to authenticated inspectors
- Consider licensing from ANSI if distributing widely

---

## Benefits

### For Inspectors
✅ Context at point of work
✅ Training while doing
✅ Confidence in compliance
✅ Reduced errors

### For Company
✅ Defensible inspections
✅ Compliance documentation
✅ Training efficiency
✅ Audit trail

### For Customers
✅ Transparent process
✅ ANSI-compliant reports
✅ Trust in inspection quality

---

## Next Steps

1. ✅ Analyze DOCX structure (DONE)
2. Create extraction script
3. Extract standard text to JSON
4. Extend Pydantic schema
5. Update templates with text references
6. Implement frontend display
7. Test with inspectors

