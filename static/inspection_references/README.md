# Inspection Reference Images

This directory contains reference images (figures, tables, diagrams) used during inspections to guide inspectors and ensure compliance with standards.

## Directory Structure

```
inspection_references/
└── ansi_a92_2_2021/
    ├── figures/
    │   ├── figure_1_dielectric_test_config.png
    │   ├── figure_1a_electrode_assembly.png
    │   └── ...
    ├── tables/
    │   ├── table_1_design_test_values.png
    │   ├── table_2_periodic_test_values.png
    │   └── table_3_before_use_tests.png
    └── README.md
```

## Image Requirements

### Format Specifications

| Property | Requirement |
|----------|------------|
| **File Format** | PNG (preferred) or JPG |
| **Resolution** | 1200-2000px width for high-DPI displays |
| **File Size** | < 500KB per image (optimize with TinyPNG/pngcrush) |
| **Color Mode** | Grayscale or minimal color for readability |
| **Text Size** | Minimum 12pt equivalent, high contrast |

### Content Guidelines

1. **Clarity**: All text must be readable at 100% zoom
2. **Contrast**: Use black text on white background (or high contrast)
3. **Annotations**: Add callouts/arrows where helpful
4. **Scale**: Include scale indicators for dimensional drawings
5. **Cleanliness**: Remove unnecessary borders, backgrounds, or watermarks

### Naming Convention

Follow this pattern for consistency:

```
{type}_{number}_{short_description}.png

Examples:
- figure_1_dielectric_test_config.png
- figure_1a_electrode_assembly.png
- table_2_periodic_test_values.png
```

**Rules:**
- Use lowercase with underscores
- Start with `figure_` or `table_`
- Include ANSI number (1, 1A, 2, etc.)
- Add brief description (< 30 chars)
- Use `.png` extension

## Adding Images to Templates

### 1. Add Image File

Place the image in the appropriate directory:
```bash
static/inspection_references/ansi_a92_2_2021/figures/figure_1_test_config.png
```

### 2. Reference in Template JSON

Add `reference_images` array to the step:

```json
{
  "step_key": "dielectric_test_ac",
  "title": "AC Dielectric Test",
  "reference_images": [
    {
      "image_id": "figure_1",
      "title": "Figure 1: Dielectric Test Configuration",
      "file_path": "ansi_a92_2_2021/figures/figure_1_test_config.png",
      "caption": "Test setup showing electrode placement and grounding arrangement",
      "display_mode": "both",
      "figure_number": "Figure 1"
    }
  ]
}
```

### Display Modes

| Mode | Behavior |
|------|----------|
| `"inline"` | Always visible in step content |
| `"modal"` | Click thumbnail to view full-size |
| `"both"` | Show inline + clickable modal |

**Recommendations:**
- Use `"inline"` for quick reference diagrams
- Use `"modal"` for detailed schematics
- Use `"both"` for critical test configurations

## Image Optimization

Before committing images, optimize them:

### Using TinyPNG (Recommended)
```bash
# Online: https://tinypng.com/
# Upload and download optimized version
```

### Using pngcrush (Command Line)
```bash
pngcrush -brute input.png output.png
```

### Using ImageMagick
```bash
convert input.png -quality 85 -strip output.png
```

## Available Figures (ANSI A92.2-2021)

Standard includes these reference figures:

| Figure | Title | Use Case |
|--------|-------|----------|
| Figure 1 | Dielectric Test Config (Cat A & B) | Dielectric testing setup |
| Figure 1A | Lower Test Electrode Details | Electrode assembly details |
| Figure 2 | Dielectric Test Config (Cat C & D) | Alternative test setup |
| Figure 2A | Optional Test Config (Cat C & D) | Optional configuration |
| Figure 3 | Chassis Insulating Systems | Chassis testing |
| Figure 3A | Shunting Arrangement | Electrical shunting |
| Figure 4 | Boom Positions for Test | Load/dielectric test positions |
| Figure 5 | Bonding Arrangements (Cat A) | Electrical bonding |
| Figure 6 | Upper Control Confirmation Test | Control component testing |
| Figure 7 | Identification Plate Format | Nameplate requirements |

## Available Tables (ANSI A92.2-2021)

| Table | Title | Use Case |
|-------|-------|----------|
| Table 1 | Design & Qualification Test Values | Manufacturing tests |
| Table 2 | Periodic Electrical Test Values | Routine periodic testing |
| Table 3 | Before Use Tests | Daily/before-use testing |

## Example: Complete Step with Images

```json
{
  "step_key": "dielectric_test_method_a",
  "type": "MEASUREMENT",
  "title": "Dielectric Test - Method A (AC)",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.1",
  "required": true,
  "reference_images": [
    {
      "image_id": "table_2",
      "title": "Table 2: Periodic Electrical Test Values",
      "file_path": "ansi_a92_2_2021/tables/table_2_periodic_test_values.png",
      "caption": "Use this table to determine required test voltage based on equipment voltage rating",
      "display_mode": "inline",
      "figure_number": "Table 2"
    },
    {
      "image_id": "figure_1",
      "title": "Figure 1: Test Configuration for Category A & B Devices",
      "file_path": "ansi_a92_2_2021/figures/figure_1_test_config.png",
      "caption": "Complete dielectric test setup showing grounding and electrode placement",
      "display_mode": "both",
      "figure_number": "Figure 1"
    },
    {
      "image_id": "figure_1a",
      "title": "Figure 1A: Lower Test Electrode Assembly Details",
      "file_path": "ansi_a92_2_2021/figures/figure_1a_electrode_details.png",
      "display_mode": "modal",
      "figure_number": "Figure 1A"
    }
  ],
  "fields": [...]
}
```

## Testing Images

Before deployment, test that:
1. ✅ Image loads correctly in frontend
2. ✅ Modal zoom/pan works smoothly
3. ✅ Image is readable on mobile devices
4. ✅ File size is optimized (< 500KB)
5. ✅ Image matches ANSI standard exactly

## Support

For questions about:
- **Image format/quality**: Contact development team
- **ANSI standard interpretation**: Contact compliance team
- **Template updates**: See template documentation
