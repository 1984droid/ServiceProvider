/**
 * DefectCaptureStep
 *
 * Renders DEFECT_CAPTURE step type with defect list and creation UI
 */

import { useState, useEffect } from 'react';
import { StepHeader } from './StepHeader';
import { FieldRenderer } from '../FieldRenderer';
import { DefectForm } from '../DefectForm';
import { Button } from '@/components/atoms/Button';
import { apiClient } from '@/lib/axios';

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
  step_id: string;
  step_key: string;
  type: string;
  title: string;
  standard_reference?: string;
  fields: SchemaField[];
}

interface Defect {
  id: string;
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY';
  status: string;
  title: string;
  description: string;
  step_key: string;
  rule_id?: string | null;
  defect_details?: any;
  created_at: string;
}

interface DefectCaptureStepProps {
  step: ProcedureStep;
  currentIndex: number;
  totalSteps: number;
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  errors?: Record<string, string>;
  disabled?: boolean;
  enumValues?: Record<string, string[]>;
  inspectionId: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  MAJOR: '#ea580c',
  MINOR: '#f59e0b',
  ADVISORY: '#3b82f6',
};

const SEVERITY_ICONS: Record<string, string> = {
  CRITICAL: '⛔',
  MAJOR: '⚠️',
  MINOR: '🔧',
  ADVISORY: 'ℹ️',
};

export function DefectCaptureStep({
  step,
  currentIndex,
  totalSteps,
  values,
  onChange,
  errors = {},
  disabled = false,
  enumValues = {},
  inspectionId
}: DefectCaptureStepProps) {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [isLoadingDefects, setIsLoadingDefects] = useState(true);
  const [showDefectForm, setShowDefectForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load defects for this inspection
  useEffect(() => {
    loadDefects();
  }, [inspectionId]);

  const loadDefects = async () => {
    setIsLoadingDefects(true);
    setError(null);
    try {
      const response = await apiClient.get(`/inspections/${inspectionId}/defects/`);
      setDefects(response.data.defects || []);
    } catch (err: any) {
      console.error('Failed to load defects:', err);
      setError('Failed to load defects');
    } finally {
      setIsLoadingDefects(false);
    }
  };

  const handleAddDefect = async (formData: any) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const defectData = {
        step_key: step.step_id,
        severity: formData.severity,
        title: formData.title,
        description: formData.description,
        defect_details: {
          location: formData.location || '',
        },
      };

      await apiClient.post(`/inspections/${inspectionId}/add_defect/`, defectData);

      // Reload defects
      await loadDefects();

      // Close form
      setShowDefectForm(false);
    } catch (err: any) {
      console.error('Failed to add defect:', err);
      setError(err.response?.data?.error || 'Failed to add defect');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filter defects for this step
  const stepDefects = defects.filter(d => d.step_key === step.step_id);

  return (
    <div>
      <StepHeader
        title={step.title}
        standardReference={step.standard_reference}
        currentIndex={currentIndex}
        totalSteps={totalSteps}
        stepType={step.type}
      />

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 rounded" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Defects Section */}
      <div className="mb-6 p-4 rounded-lg border" style={{ borderColor: '#e5e7eb', backgroundColor: '#f9fafb' }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold" style={{ color: '#111827' }}>
            Defects Found ({stepDefects.length})
          </h3>
          <Button
            onClick={() => setShowDefectForm(!showDefectForm)}
            variant="primary"
            disabled={disabled}
          >
            {showDefectForm ? 'Cancel' : '+ Add Defect'}
          </Button>
        </div>

        {/* Add Defect Form */}
        {showDefectForm && (
          <div className="mb-4 p-4 rounded-lg border" style={{ borderColor: '#d1d5db', backgroundColor: 'white' }}>
            <h4 className="text-md font-semibold mb-3" style={{ color: '#111827' }}>
              New Defect
            </h4>
            <DefectForm
              onSubmit={handleAddDefect}
              onCancel={() => setShowDefectForm(false)}
              isSubmitting={isSubmitting}
            />
          </div>
        )}

        {/* Defects List */}
        {isLoadingDefects ? (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
            <p className="mt-2 text-sm text-gray-600">Loading defects...</p>
          </div>
        ) : stepDefects.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No defects found for this step</p>
            <p className="text-sm mt-1">Click "Add Defect" to record any issues found during inspection</p>
          </div>
        ) : (
          <div className="space-y-3">
            {stepDefects.map((defect) => (
              <div
                key={defect.id}
                className="p-4 rounded-lg border"
                style={{
                  borderColor: '#e5e7eb',
                  backgroundColor: 'white',
                  borderLeftWidth: '4px',
                  borderLeftColor: SEVERITY_COLORS[defect.severity],
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">{SEVERITY_ICONS[defect.severity]}</span>
                      <span
                        className="px-2 py-1 text-xs font-semibold rounded uppercase"
                        style={{
                          backgroundColor: SEVERITY_COLORS[defect.severity],
                          color: 'white',
                        }}
                      >
                        {defect.severity}
                      </span>
                      {defect.rule_id && (
                        <span className="px-2 py-1 text-xs rounded" style={{ backgroundColor: '#e0e7ff', color: '#4338ca' }}>
                          Auto-generated
                        </span>
                      )}
                    </div>
                    <h4 className="font-semibold text-md mb-1" style={{ color: '#111827' }}>
                      {defect.title}
                    </h4>
                    <p className="text-sm mb-2" style={{ color: '#6b7280' }}>
                      {defect.description}
                    </p>
                    {defect.defect_details?.location && (
                      <p className="text-xs" style={{ color: '#9ca3af' }}>
                        📍 Location: {defect.defect_details.location}
                      </p>
                    )}
                  </div>
                  <div className="text-xs text-right" style={{ color: '#9ca3af' }}>
                    <p>{new Date(defect.created_at).toLocaleDateString()}</p>
                    <p>{new Date(defect.created_at).toLocaleTimeString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Step Fields */}
      {step.fields.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-md font-semibold" style={{ color: '#111827' }}>
            Additional Information
          </h3>
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
      )}
    </div>
  );
}
