# Asset Templates v2 Package

This package contains:
- Asset subtype hierarchy with robust categories (fleet, equipment, shop equipment, tools, safety, facilities, real estate, IT, containers)
- Typed capability definitions (minimal free text)
- Capability packs for reuse and inheritance
- Starter inspection checklists and programs
- Starter maintenance task catalog and programs
- Default program assignments by subtype

Main files:
- ASSET_TEMPLATE_SYSTEM_V2.md
- asset_subtypes.json
- capability_definitions.json
- capability_packs.json
- inspection_checklists.json
- inspection_programs.json
- maintenance_task_catalog.json
- maintenance_programs.json
- subtype_program_defaults.json



Work order integration:
- work_order_vocabulary/ (nouns, verbs, locations, schema)
- work_order_integration/ (seed mapping from A92.2 defects to work order line suggestions)
