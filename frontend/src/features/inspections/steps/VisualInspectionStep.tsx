/**
 * VisualInspectionStep
 *
 * Renders VISUAL_INSPECTION step type
 * Same as SetupStep for now - renders fields in grid
 */

import { StepHeader } from './StepHeader';
import { FieldRenderer } from '../FieldRenderer';

interface SchemaField {
  field_id: string;
  label?: string;
  type: string;
  required?: boolean;
  enum_ref?: string;
  values?: string[];
  min?: number;
  max?: number;
  precision?: number;
  help_text?: string;
}

interface ProcedureStep {
  step_key: string;
  type: string;
  title: string;
  standard_reference?: string;
  fields: SchemaField[];
}

interface VisualInspectionStepProps {
  step: ProcedureStep;
  currentIndex: number;
  totalSteps: number;
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  errors?: Record<string, string>;
  disabled?: boolean;
  enumValues?: Record<string, string[]>;
}

export function VisualInspectionStep({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {}
}: VisualInspectionStepProps) {
  return (
    <div>
      <StepHeader
        title={step.title}
        standardReference={step.standard_reference}
        currentIndex={currentIndex}
        totalSteps={totalSteps}
        stepType={step.type}
      />

      <div className="space-y-6">
        {step.fields.map((field) => (
          <FieldRenderer
            key={field.field_id}
            field={field}
            value={values[field.field_id]}
            onChange={(value) => onChange(field.field_id, value)}
            error={errors[field.field_id]}
            disabled={disabled}
            enumValues={enumValues}
          />
        ))}
      </div>
    </div>
  );
}
