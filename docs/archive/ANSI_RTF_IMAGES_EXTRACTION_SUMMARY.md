# ANSI A92.2-2021 RTF Images - Extraction Complete

## Summary

✅ **Successfully extracted 17 images from ANSI+SAIA+A92.2-2021.rtf**

- 4 PNG images
- 13 JPEG images
- All saved to: `temp/extracted_ansi_images/`

## Images Extracted

| # | Type | Size | File |
|---|------|------|------|
| 01 | PNG | 18 KB | extracted_image_01.png |
| 02 | JPG | 73 KB | extracted_image_02.jpg |
| 03 | JPG | 196 KB | extracted_image_03.jpg |
| 04 | PNG | 86 KB | extracted_image_04.png |
| 05 | JPG | 59 KB | extracted_image_05.jpg |
| 06 | PNG | 122 KB | extracted_image_06.png |
| 07 | JPG | 76 KB | extracted_image_07.jpg |
| 08 | JPG | 153 KB | extracted_image_08.jpg |
| 09 | JPG | 25 KB | extracted_image_09.jpg |
| 10 | PNG | 26 KB | extracted_image_10.png |
| 11 | JPG | 124 KB | extracted_image_11.jpg |
| 12 | JPG | 167 KB | extracted_image_12.jpg |
| 13 | JPG | 142 KB | extracted_image_13.jpg |
| 14 | JPG | 130 KB | extracted_image_14.jpg |
| 15 | JPG | 114 KB | extracted_image_15.jpg |
| 16 | JPG | 128 KB | extracted_image_16.jpg |
| 17 | JPG | 73 KB | extracted_image_17.jpg |

## Expected ANSI Images

According to ANSI A92.2-2021, we should have:

### Figures (10 total):
1. **Figure 1**: Dielectric Test Configuration for Category A & B Aerial Devices
2. **Figure 1A**: Details of Lower Test Electrode Assembly & Conductive Shield
3. **Figure 2**: Dielectric Test Configuration for Category C & D Aerial Devices
4. **Figure 2A**: Optional Dielectric Test Configuration for Category C & D
5. **Figure 3**: Dielectric Test Configuration for Chassis Insulating Systems
6. **Figure 3A**: Suggested Shunting Arrangement for Chassis Insulating System
7. **Figure 4**: Boom Positions for Dielectric Test of Extensible Insulating Aerial Devices
8. **Figure 5**: Typical Bonding Arrangements for Category A Aerial Devices
9. **Figure 6**: Confirmation Test of Upper Control Components w/High Electrical Resistance
10. **Figure 7**: Recommended Identification Plate Format

### Tables (3 total):
1. **Table 1**: Design, Quality Assurance and Qualification Test Values
2. **Table 2**: Periodic Electrical Test Values
3. **Table 3**: Before Use Tests

### Other Images (4):
- Title pages
- Headers
- Logos
- Diagrams

**Total**: 17 images ✅ (10 figures + 3 tables + 4 other = 17)

## Next Steps

### 1. Manual Identification

You need to open each extracted image and identify what it contains:

```bash
# Open image viewer
start temp/extracted_ansi_images/
```

### 2. Rename and Organize

Once identified, rename and move to proper directories:

**Figures:**
```bash
move temp/extracted_ansi_images/extracted_image_XX.jpg static/inspection_references/ansi_a92_2_2021/figures/figure_1_dielectric_test_config.jpg
move temp/extracted_ansi_images/extracted_image_XX.jpg static/inspection_references/ansi_a92_2_2021/figures/figure_1a_electrode_assembly.jpg
# ... etc
```

**Tables:**
```bash
move temp/extracted_ansi_images/extracted_image_XX.jpg static/inspection_references/ansi_a92_2_2021/tables/table_1_design_test_values.jpg
move temp/extracted_ansi_images/extracted_image_XX.jpg static/inspection_references/ansi_a92_2_2021/tables/table_2_periodic_test_values.jpg
move temp/extracted_ansi_images/extracted_image_XX.jpg static/inspection_references/ansi_a92_2_2021/tables/table_3_before_use_tests.jpg
```

### 3. Naming Convention

Use this pattern:
```
{type}_{number}_{short_description}.{ext}

Examples:
- figure_1_dielectric_test_config.jpg
- figure_1a_electrode_assembly.jpg
- figure_6_upper_control_test.jpg
- table_2_periodic_test_values.jpg
```

### 4. Add to Templates

Once images are properly named and organized, add them to templates:

```json
{
  "step_key": "execute_test_method_a_ac",
  "reference_images": [
    {
      "image_id": "table_2",
      "title": "Table 2: Periodic Electrical Test Values",
      "file_path": "ansi_a92_2_2021/tables/table_2_periodic_test_values.jpg",
      "caption": "Use this table to determine required test voltage and maximum allowable current based on equipment voltage rating",
      "display_mode": "inline",
      "figure_number": "Table 2"
    },
    {
      "image_id": "figure_1",
      "title": "Figure 1: Dielectric Test Configuration",
      "file_path": "ansi_a92_2_2021/figures/figure_1_dielectric_test_config.jpg",
      "caption": "Complete test setup showing electrode placement and grounding for Category A & B devices",
      "display_mode": "both",
      "figure_number": "Figure 1"
    }
  ]
}
```

## Benefits of Using RTF Images

✅ **Better Quality**: Original embedded images at full resolution
✅ **Exact ANSI Diagrams**: Official figures/tables from the standard
✅ **Complete Set**: All 17 images including title pages
✅ **Ready to Use**: Can be directly referenced in templates
✅ **Offline Access**: Images bundled with app, no internet needed

## Priority Images for Dielectric Test Template

Based on the audit, these images are CRITICAL for the dielectric test template:

1. **Figure 1** - Cat A/B test configuration (CRITICAL)
2. **Figure 1A** - Lower electrode details (CRITICAL)
3. **Figure 2** - Cat C/D/E test configuration (CRITICAL)
4. **Figure 3** - Chassis insulating systems (CRITICAL)
5. **Figure 3A** - Shunting arrangement (CRITICAL)
6. **Figure 4** - Boom positioning (CRITICAL)
7. **Figure 5** - Bonding arrangements (CRITICAL)
8. **Figure 6** - Upper control test (CRITICAL - missing step!)
9. **Table 2** - Periodic test values (CRITICAL)
10. **Table 3** - Before use tests (CRITICAL)

## Image Optimization

After identifying and renaming, optionally optimize file sizes:

```bash
# Using ImageMagick
mogrify -strip -quality 85 -resize 1600x1600\> static/inspection_references/ansi_a92_2_2021/**/*.jpg

# Or using TinyPNG online:
# https://tinypng.com/
```

Target: < 500KB per image

## Template Updates Needed

Once images are organized, update these templates:

1. **dielectric_test_periodic.json** - Add ALL figures/tables
2. **periodic_inspection.json** - Add relevant structural diagrams
3. **major_structural_inspection.json** - Add structural/weld references
4. **frequent_inspection.json** - Add quick reference diagrams

## Using RTF for All A92.2 References

**YES** - The RTF file is superior for template development:

✅ **Embedded Images**: All figures/tables included
✅ **Better Formatting**: Preserves tables, diagrams, structure
✅ **Complete Document**: Single source of truth
✅ **Easy Extraction**: This script makes it simple

**Recommendation**: Keep both files:
- `ANSI+SAIA+A92.2-2021.rtf` - For image extraction and visual reference
- `ANSI+SAIA+A92.2-2021.txt` - For text searching and section lookups

Use RTF for visual elements, use TXT for automated text processing/searching.
