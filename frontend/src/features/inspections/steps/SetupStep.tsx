/**
 * SetupStep
 *
 * Renders SETUP step type
 * Simple form with fields - no special logic
 */

import { useState } from 'react';
import { StepHeader } from './StepHeader';
import { FieldRenderer } from '../FieldRenderer';
import { employeesApi } from '@/api/employees.api';

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

interface SetupStepProps {
  step: ProcedureStep;
  currentIndex: number;
  totalSteps: number;
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  errors?: Record<string, string>;
  disabled?: boolean;
  enumValues?: Record<string, string[]>;
  templateKey?: string;
}

export function SetupStep({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {},
  templateKey = ''
}: SetupStepProps) {
  const [isAutoFilling, setIsAutoFilling] = useState(false);
  const [autoFillError, setAutoFillError] = useState<string | null>(null);

  // Check if this step has inspector-related fields
  const hasInspectorFields = step.fields.some(field => {
    const fieldId = field.field_id.toLowerCase();
    const label = (field.label || '').toLowerCase();
    return fieldId.includes('inspector') ||
           label.includes('inspector') ||
           fieldId.includes('certification') ||
           label.includes('certification') ||
           fieldId.includes('qualification') ||
           label.includes('qualification');
  });

  const handleAutoFill = async () => {
    setIsAutoFilling(true);
    setAutoFillError(null);

    try {
      const employee = await employeesApi.me();

      // Extract standard from template_key (e.g., 'ansi_a92_2_periodic_inspection' -> 'a92.2')
      const extractStandard = (key: string): string | null => {
        // Match patterns like 'a92_2' or 'a92_5' or 'a92_6' in template key
        const match = key.match(/a92[_\-](\d+)/i);
        if (match) {
          return `a92.${match[1]}`;
        }
        return null;
      };

      const templateStandard = templateKey ? extractStandard(templateKey.toLowerCase()) : null;

      // Auto-fill inspector name fields
      step.fields.forEach(field => {
        const fieldId = field.field_id.toLowerCase();
        const label = (field.label || '').toLowerCase();

        if (fieldId.includes('inspector') && fieldId.includes('name') ||
            label.includes('inspector') && label.includes('name')) {
          onChange(field.field_id, employee.full_name);
        }

        // Auto-fill certification fields - only matching certifications
        if ((fieldId.includes('certification') || fieldId.includes('qualification') ||
             label.includes('certification') || label.includes('qualification')) &&
            !fieldId.includes('name') && !label.includes('name')) {
          if (employee.certifications && employee.certifications.length > 0) {
            // Filter certifications to match the template standard
            let matchingCerts = employee.certifications;
            if (templateStandard) {
              matchingCerts = employee.certifications.filter(cert =>
                cert.standard.toLowerCase().includes(templateStandard)
              );
            }

            if (matchingCerts.length > 0) {
              const certString = matchingCerts
                .map(cert => cert.cert_number)
                .join(', ');
              onChange(field.field_id, certString);
            }
          }
        }

        // Auto-fill current inspection date to today (but NOT last inspection date)
        if ((fieldId.includes('inspection') && fieldId.includes('date') ||
             label.includes('inspection') && label.includes('date')) &&
            !fieldId.includes('last') && !label.includes('last') &&
            !fieldId.includes('previous') && !label.includes('previous') &&
            field.type === 'DATE') {
          const today = new Date().toISOString().split('T')[0];
          onChange(field.field_id, today);
        }
      });
    } catch (error: any) {
      console.error('Auto-fill failed:', error);
      setAutoFillError(error.response?.data?.detail || 'Failed to load inspector information');
    } finally {
      setIsAutoFilling(false);
    }
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

      {hasInspectorFields && !disabled && (
        <div className="mb-4">
          <button
            type="button"
            onClick={handleAutoFill}
            disabled={isAutoFilling}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isAutoFilling ? 'Loading...' : 'Auto-fill Inspector Info'}
          </button>
          {autoFillError && (
            <p className="mt-2 text-sm text-red-600">{autoFillError}</p>
          )}
        </div>
      )}

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
