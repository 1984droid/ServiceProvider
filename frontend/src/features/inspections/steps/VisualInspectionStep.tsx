/**
 * VisualInspectionStep
 *
 * Renders VISUAL_INSPECTION step type
 * Supports defect capture mode (ADD_DEFECT_ITEMS) with structured defect schema
 */

import { useState, useMemo } from 'react';
import { StepHeader } from './StepHeader';
import { FieldRenderer } from '../FieldRenderer';
import { AddDefectModal } from './AddDefectModal';
import { StepDefectsList } from './StepDefectsList';
import type { DefectData, DefectContext } from './defectTypes';

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
  conditionally_required_if?: {
    any_field_in?: string[];
    description?: string;
  };
}

interface DefectSchema {
  defect_id_format: string;
  fields: Array<{
    field_id: string;
    type: string;
    required: boolean;
  }>;
}

interface ProcedureStep {
  step_key: string;
  type: string;
  title: string;
  standard_reference?: string;
  fields: SchemaField[];
  defect_schema_ref?: string;
  ui?: {
    mode?: string;
    guidance?: string[];
  };
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
  defectSchema?: DefectSchema;
}

// Values that trigger defect indicators with suggested severity mapping
const DEFECT_TRIGGER_VALUES = [
  'FAIL',
  'EXCESSIVE',
  'REQUIRES_REPLACEMENT',
  'SERVICE_REQUIRED',
  'UNSAFE_OUT_OF_SERVICE',
  'MODERATE',
  'MINOR',
];

// Map assessment values to suggested defect severity
const VALUE_TO_SEVERITY_MAP: Record<string, 'SAFE' | 'MINOR' | 'SERVICE_REQUIRED' | 'UNSAFE_OUT_OF_SERVICE'> = {
  'MINOR': 'MINOR',
  'MODERATE': 'MINOR',
  'EXCESSIVE': 'SERVICE_REQUIRED',
  'REQUIRES_REPLACEMENT': 'SERVICE_REQUIRED',
  'SERVICE_REQUIRED': 'SERVICE_REQUIRED',
  'UNSAFE_OUT_OF_SERVICE': 'UNSAFE_OUT_OF_SERVICE',
  'FAIL': 'SERVICE_REQUIRED',
};

export function VisualInspectionStep({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {},
  defectSchema,
}: VisualInspectionStepProps) {
  const [isDefectModalOpen, setIsDefectModalOpen] = useState(false);
  const [editingDefect, setEditingDefect] = useState<DefectData | null>(null);

  // Check if step supports defect capture
  const supportsDefects = step.defect_schema_ref && step.ui?.mode === 'ADD_DEFECT_ITEMS';

  // Get defects array from values
  const defects: DefectData[] = values.defects || [];

  // Detect if any assessment fields have defect conditions
  const hasDefectConditions = useMemo(() => {
    return Object.values(values).some(
      (value) => typeof value === 'string' && DEFECT_TRIGGER_VALUES.includes(value)
    );
  }, [values]);

  // Find fields with defect conditions for highlighting
  const fieldsWithDefects = useMemo(() => {
    const fields = new Set<string>();
    Object.entries(values).forEach(([fieldId, value]) => {
      if (typeof value === 'string' && DEFECT_TRIGGER_VALUES.includes(value)) {
        fields.add(fieldId);
      }
    });
    return fields;
  }, [values]);

  // Build context for defect modal with all triggered fields
  const defectContext = useMemo((): DefectContext => {
    const triggeredFields = Array.from(fieldsWithDefects).map(fieldId => {
      const fieldInfo = step.fields.find(f => f.field_id === fieldId);
      const value = values[fieldId] as string;
      return {
        fieldId,
        label: fieldInfo?.label || fieldId,
        value,
        suggestedSeverity: VALUE_TO_SEVERITY_MAP[value],
      };
    });

    return {
      standardReference: step.standard_reference,
      triggeredFields,
    };
  }, [fieldsWithDefects, step.fields, step.standard_reference, values]);

  const handleAddDefect = () => {
    setEditingDefect(null);
    setIsDefectModalOpen(true);
  };

  const handleEditDefect = (defect: DefectData) => {
    setEditingDefect(defect);
    setIsDefectModalOpen(true);
  };

  const handleSaveDefect = (defect: DefectData) => {
    const updatedDefects = editingDefect && defects.some(d => d.defect_id === editingDefect.defect_id)
      ? defects.map(d => (d.defect_id === defect.defect_id ? defect : d))
      : [...defects, defect];

    onChange('defects', updatedDefects);
    setEditingDefect(null);
  };

  const handleDeleteDefect = (defectId: string) => {
    onChange(
      'defects',
      defects.filter((d) => d.defect_id !== defectId)
    );
  };

  return (
    <div>
      <StepHeader
        title={step.title}
        standardReference={step.standard_reference}
        currentIndex={currentIndex}
        totalSteps={totalSteps}
        stepType={step.type}
      />

      {/* Guidance */}
      {step.ui?.guidance && step.ui.guidance.length > 0 && (
        <div className="mb-4 p-3 rounded bg-blue-50 border border-blue-200">
          <div className="text-sm font-medium text-blue-900 mb-2">Inspection Guidance:</div>
          <ul className="text-sm text-blue-800 space-y-1">
            {step.ui.guidance.map((text, index) => (
              <li key={index} className="flex items-start">
                <span className="mr-2">•</span>
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Defect Alert */}
      {supportsDefects && hasDefectConditions && (
        <div className="mb-4 p-4 rounded bg-yellow-50 border-l-4 border-yellow-400">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-yellow-800 font-semibold">⚠️ Defect Conditions Detected</span>
              </div>
              <p className="text-sm text-yellow-700">
                {fieldsWithDefects.size} field(s) require defect documentation. Click "Add Defect" to document details.
              </p>
            </div>
            {!disabled && (
              <button
                type="button"
                onClick={handleAddDefect}
                className="ml-4 px-4 py-2 text-sm font-medium text-white rounded transition-colors"
                style={{ backgroundColor: '#ea580c' }}
              >
                ➕ Add Defect
              </button>
            )}
          </div>
        </div>
      )}

      {/* Assessment Fields Grid */}
      <div className="grid grid-cols-2 gap-4">
        {step.fields
          .filter((field) => field.field_id !== 'defects') // Don't render defects array as field
          .map((field) => {
            const hasDefectValue = fieldsWithDefects.has(field.field_id);

            return (
              <div
                key={field.field_id}
                className={hasDefectValue ? 'ring-2 ring-yellow-400 rounded p-2' : ''}
              >
                {hasDefectValue && (
                  <div className="text-xs font-medium text-yellow-700 mb-1">
                    ⚠️ Defect condition
                  </div>
                )}
                <FieldRenderer
                  field={field}
                  value={values[field.field_id]}
                  onChange={(value) => onChange(field.field_id, value)}
                  error={errors[field.field_id]}
                  disabled={disabled}
                  enumValues={enumValues}
                />
              </div>
            );
          })}
      </div>

      {/* Defects List */}
      {supportsDefects && (
        <>
          <StepDefectsList
            defects={defects}
            onEdit={handleEditDefect}
            onDelete={handleDeleteDefect}
            disabled={disabled}
          />

          {/* Add Defect Button (always visible if mode supports it) */}
          {!disabled && (
            <div className="mt-4">
              <button
                type="button"
                onClick={handleAddDefect}
                className="px-4 py-2 text-sm font-medium border-2 border-dashed border-gray-300 rounded hover:border-gray-400 hover:bg-gray-50 transition-colors w-full"
              >
                ➕ Add Defect
              </button>
            </div>
          )}
        </>
      )}

      {/* Defect Modal */}
      {supportsDefects && defectSchema && (
        <AddDefectModal
          isOpen={isDefectModalOpen}
          onClose={() => {
            setIsDefectModalOpen(false);
            setEditingDefect(null);
          }}
          onSave={handleSaveDefect}
          defectSchema={defectSchema}
          enumValues={enumValues}
          initialData={editingDefect || undefined}
          editMode={!!editingDefect && defects.some(d => d.defect_id === editingDefect.defect_id)}
          context={defectContext}
        />
      )}
    </div>
  );
}
