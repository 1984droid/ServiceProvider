/**
 * MeasurementStep
 *
 * Renders MEASUREMENT step type
 * Supports measurement_sets for grouped/tabular measurements
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
  measurement_set_ref?: string;
}

interface MeasurementSet {
  measurement_set_id: string;
  title: string;
  fields: SchemaField[];
}

interface MeasurementStepProps {
  step: ProcedureStep;
  currentIndex: number;
  totalSteps: number;
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  errors?: Record<string, string>;
  disabled?: boolean;
  enumValues?: Record<string, string[]>;
  measurementSets?: Record<string, MeasurementSet>;
}

export function MeasurementStep({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {},
  measurementSets = {}
}: MeasurementStepProps) {

  // Check if this step uses a measurement set
  const measurementSet = step.measurement_set_ref ? measurementSets[step.measurement_set_ref] : null;
  const fieldsToRender = measurementSet ? measurementSet.fields : step.fields;

  return (
    <div>
      <StepHeader
        title={step.title}
        standardReference={step.standard_reference}
        currentIndex={currentIndex}
        totalSteps={totalSteps}
        stepType={step.type}
      />

      {measurementSet && (
        <div className="mb-3 p-2 rounded-lg" style={{ backgroundColor: '#eff6ff' }}>
          <p className="text-xs font-medium" style={{ color: '#1e40af' }}>
            {measurementSet.title}
          </p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        {fieldsToRender.map((field) => (
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
