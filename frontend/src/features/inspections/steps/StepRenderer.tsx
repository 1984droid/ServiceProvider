/**
 * StepRenderer
 *
 * Routes to the correct step component based on step.type
 * Handles all 5 step types from inspection templates
 */

import { SetupStep } from './SetupStep';
import { VisualInspectionStep } from './VisualInspectionStep';
import { FunctionTestStep } from './FunctionTestStep';
import { MeasurementStep } from './MeasurementStep';
import { DefectCaptureStep } from './DefectCaptureStep';

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

interface StepRendererProps {
  step: ProcedureStep;
  currentIndex: number;
  totalSteps: number;
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  errors?: Record<string, string>;
  disabled?: boolean;
  enumValues?: Record<string, string[]>;
  measurementSets?: Record<string, MeasurementSet>;
  inspectionId?: string;
}

export function StepRenderer({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {},
  measurementSets = {},
  inspectionId = ''
}: StepRendererProps) {

  const stepType = step.type.toUpperCase();

  // Route to the appropriate step component
  switch (stepType) {
    case 'SETUP':
      return (
        <SetupStep
          step={step}
          currentIndex={currentIndex}
          totalSteps={totalSteps}
          values={values}
          onChange={onChange}
          errors={errors}
          disabled={disabled}
          enumValues={enumValues}
        />
      );

    case 'VISUAL_INSPECTION':
      return (
        <VisualInspectionStep
          step={step}
          currentIndex={currentIndex}
          totalSteps={totalSteps}
          values={values}
          onChange={onChange}
          errors={errors}
          disabled={disabled}
          enumValues={enumValues}
        />
      );

    case 'FUNCTION_TEST':
      return (
        <FunctionTestStep
          step={step}
          currentIndex={currentIndex}
          totalSteps={totalSteps}
          values={values}
          onChange={onChange}
          errors={errors}
          disabled={disabled}
          enumValues={enumValues}
        />
      );

    case 'MEASUREMENT':
      return (
        <MeasurementStep
          step={step}
          currentIndex={currentIndex}
          totalSteps={totalSteps}
          values={values}
          onChange={onChange}
          errors={errors}
          disabled={disabled}
          enumValues={enumValues}
          measurementSets={measurementSets}
        />
      );

    case 'DEFECT_CAPTURE':
      return (
        <DefectCaptureStep
          step={step}
          currentIndex={currentIndex}
          totalSteps={totalSteps}
          values={values}
          onChange={onChange}
          errors={errors}
          disabled={disabled}
          enumValues={enumValues}
          inspectionId={inspectionId}
        />
      );

    default:
      return (
        <div className="p-6 border rounded-lg" style={{ borderColor: '#fbbf24', backgroundColor: '#fef3c7' }}>
          <h3 className="text-lg font-semibold mb-2" style={{ color: '#92400e' }}>
            Unsupported Step Type
          </h3>
          <p className="text-sm" style={{ color: '#92400e' }}>
            Step type "{step.type}" is not supported. Please check the template definition.
          </p>
        </div>
      );
  }
}
