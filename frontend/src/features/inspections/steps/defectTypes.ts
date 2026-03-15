/**
 * Shared types for defect capture
 */

export interface DefectData {
  defect_id: string;
  title: string;
  severity: 'SAFE' | 'MINOR' | 'SERVICE_REQUIRED' | 'UNSAFE_OUT_OF_SERVICE';
  description: string;
  component?: string;
  location?: string;
  photo_evidence?: string[];
  corrective_action?: string;
  standard_reference?: string;
}

export interface DefectSchemaField {
  field_id: string;
  type: string;
  required: boolean;
  max_length?: number;
  enum_ref?: string;
  conditionally_required_if?: {
    field: string;
    values: string[];
  };
  help_text?: string;
}

export interface DefectSchema {
  defect_id_format: string;
  fields: DefectSchemaField[];
}

export interface DefectContext {
  standardReference?: string;
  triggeredFields: Array<{
    fieldId: string;
    label: string;
    value: string;
    suggestedSeverity?: 'SAFE' | 'MINOR' | 'SERVICE_REQUIRED' | 'UNSAFE_OUT_OF_SERVICE';
  }>;
}
