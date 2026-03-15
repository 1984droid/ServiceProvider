/**
 * AddDefectModal
 *
 * Modal for adding structured defects during inspection execution
 * Based on defect_schema from template
 * Supports all fields: title, severity, description, component, location, photo_evidence, corrective_action, standard_reference
 */

import { useState, useEffect } from 'react';
import { FormField } from '@/components/molecules/FormField';
import { TextInput } from '@/components/atoms/TextInput';
import { TextArea } from '@/components/atoms/TextArea';
import { Select } from '@/components/atoms/Select';
import { PhotoField } from '@/components/atoms/PhotoField';
import type { DefectData, DefectSchema, DefectContext } from './defectTypes';

interface AddDefectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (defect: DefectData) => void;
  defectSchema: DefectSchema;
  enumValues: Record<string, string[]>;
  initialData?: Partial<DefectData>; // Pre-populate from assessment
  editMode?: boolean;
  context?: DefectContext; // Context from step assessment
}

const SEVERITY_OPTIONS = [
  { value: '', label: 'Select severity...' },
  { value: 'SAFE', label: 'Safe - No safety impact' },
  { value: 'MINOR', label: 'Minor - Monitor for next inspection' },
  { value: 'SERVICE_REQUIRED', label: 'Service Required - Schedule repair' },
  { value: 'UNSAFE_OUT_OF_SERVICE', label: 'Unsafe / Out of Service - Tag out equipment' },
];

const SEVERITY_COLORS: Record<string, string> = {
  SAFE: '#10b981',
  MINOR: '#f59e0b',
  SERVICE_REQUIRED: '#ea580c',
  UNSAFE_OUT_OF_SERVICE: '#dc2626',
};

export function AddDefectModal({
  isOpen,
  onClose,
  onSave,
  defectSchema,
  enumValues,
  initialData = {},
  editMode = false,
  context,
}: AddDefectModalProps) {
  const [selectedComponents, setSelectedComponents] = useState<Set<string>>(new Set());
  const [formData, setFormData] = useState<Partial<DefectData>>({
    defect_id: initialData.defect_id || crypto.randomUUID(),
    title: initialData.title || '',
    severity: initialData.severity || '' as any,
    description: initialData.description || '',
    component: initialData.component || '',
    location: initialData.location || '',
    photo_evidence: initialData.photo_evidence || [],
    corrective_action: initialData.corrective_action || '',
    standard_reference: initialData.standard_reference || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens
  useEffect(() => {
    if (!isOpen) return;

    // Auto-populate from context if not editing
    const isNewDefect = !initialData.defect_id;
    const highestSeverity = context?.triggeredFields
      .map(f => f.suggestedSeverity)
      .filter(Boolean)
      .sort((a, b) => {
        const order = ['SAFE', 'MINOR', 'SERVICE_REQUIRED', 'UNSAFE_OUT_OF_SERVICE'];
        return order.indexOf(b!) - order.indexOf(a!);
      })[0];

    setFormData({
      defect_id: initialData.defect_id || crypto.randomUUID(),
      title: initialData.title || '',
      severity: initialData.severity || (isNewDefect && highestSeverity ? highestSeverity : '' as any),
      description: initialData.description || '',
      component: initialData.component || '',
      location: initialData.location || '',
      photo_evidence: initialData.photo_evidence || [],
      corrective_action: initialData.corrective_action || '',
      standard_reference: initialData.standard_reference || (isNewDefect ? context?.standardReference || '' : ''),
    });
    setSelectedComponents(new Set());
    setErrors({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const handleChange = (field: keyof DefectData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required fields
    if (!formData.title?.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (!formData.severity) {
      newErrors.severity = 'Severity is required';
    }

    if (!formData.description?.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less';
    }

    // Conditional photo requirement
    if (
      formData.severity &&
      ['SERVICE_REQUIRED', 'UNSAFE_OUT_OF_SERVICE'].includes(formData.severity)
    ) {
      if (!formData.photo_evidence || formData.photo_evidence.length === 0) {
        newErrors.photo_evidence = 'Photos are required for this severity level';
      }
    }

    // Length validation
    if (formData.component && formData.component.length > 100) {
      newErrors.component = 'Component must be 100 characters or less';
    }

    if (formData.location && formData.location.length > 200) {
      newErrors.location = 'Location must be 200 characters or less';
    }

    if (formData.corrective_action && formData.corrective_action.length > 1000) {
      newErrors.corrective_action = 'Corrective action must be 1000 characters or less';
    }

    if (formData.standard_reference && formData.standard_reference.length > 100) {
      newErrors.standard_reference = 'Standard reference must be 100 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    onSave(formData as DefectData);
    onClose();
  };

  const handleCancel = () => {
    setFormData({});
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  // Photo requirement indicator
  const isPhotoRequired =
    formData.severity &&
    ['SERVICE_REQUIRED', 'UNSAFE_OUT_OF_SERVICE'].includes(formData.severity);

  const isPhotoSuggested =
    formData.severity &&
    ['MINOR'].includes(formData.severity);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">
            {editMode ? 'Edit Defect' : 'Add Defect'}
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Document defect details, severity, and evidence
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Component Selection - Show if context has triggered fields */}
          {context && context.triggeredFields && context.triggeredFields.length > 0 && !editMode && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
              <div className="font-medium text-gray-900 mb-2">
                Defect Conditions Detected ({context.triggeredFields.length})
              </div>
              <div className="text-sm text-gray-700 mb-3">
                Select the component(s) affected by this defect:
              </div>
              <div className="space-y-2">
                {context.triggeredFields.map(field => (
                  <label key={field.fieldId} className="flex items-center gap-3 p-2 hover:bg-yellow-100 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedComponents.has(field.fieldId)}
                      onChange={(e) => {
                        const newSelected = new Set(selectedComponents);
                        if (e.target.checked) {
                          newSelected.add(field.fieldId);
                          // Auto-fill component field if first selection
                          if (selectedComponents.size === 0 && !formData.component) {
                            handleChange('component', field.label);
                          }
                        } else {
                          newSelected.delete(field.fieldId);
                        }
                        setSelectedComponents(newSelected);
                      }}
                      className="h-4 w-4"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{field.label}</div>
                      <div className="text-xs text-gray-600">
                        Condition: <span className="font-medium">{field.value}</span>
                        {field.suggestedSeverity && (
                          <span className="ml-2 px-2 py-0.5 rounded text-xs font-medium" style={{
                            backgroundColor: SEVERITY_COLORS[field.suggestedSeverity],
                            color: 'white'
                          }}>
                            Suggested: {field.suggestedSeverity.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Severity */}
          <FormField label="Severity" required error={errors.severity}>
            <Select
              value={formData.severity || ''}
              onChange={(e) => handleChange('severity', e.target.value)}
              options={SEVERITY_OPTIONS}
            />
            {formData.severity && (
              <div
                className="mt-2 p-3 rounded text-sm font-medium text-white"
                style={{ backgroundColor: SEVERITY_COLORS[formData.severity] }}
              >
                {SEVERITY_OPTIONS.find(opt => opt.value === formData.severity)?.label}
              </div>
            )}
          </FormField>

          {/* Title */}
          <FormField
            label="Defect Title"
            required
            error={errors.title}
            helpText="Brief, descriptive summary (max 200 characters)"
          >
            <TextInput
              value={formData.title || ''}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="e.g., Excessive wear on boom pivot pins"
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.title?.length || 0} / 200 characters
            </div>
          </FormField>

          {/* Description */}
          <FormField
            label="Description"
            required
            error={errors.description}
            helpText="Detailed description with observations and measurements (max 2000 characters)"
          >
            <TextArea
              value={formData.description || ''}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Provide detailed information: what was observed, measurements, comparison to normal condition, immediate actions taken..."
              rows={5}
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.description?.length || 0} / 2000 characters
            </div>
          </FormField>

          {/* Component */}
          <FormField
            label="Component"
            error={errors.component}
            helpText="Component or system where defect was found (max 100 characters)"
          >
            <TextInput
              value={formData.component || ''}
              onChange={(e) => handleChange('component', e.target.value)}
              placeholder="e.g., Boom Pivot Pin, Hydraulic Cylinder - Boom Lift"
            />
          </FormField>

          {/* Location */}
          <FormField
            label="Location"
            error={errors.location}
            helpText="Specific physical location on equipment (max 200 characters)"
          >
            <TextInput
              value={formData.location || ''}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="e.g., Driver side, lower boom section, second pivot pin from base"
            />
          </FormField>

          {/* Photo Evidence */}
          <FormField
            label="Photo Evidence"
            required={isPhotoRequired}
            error={errors.photo_evidence}
            helpText={
              isPhotoRequired
                ? '⚠️ REQUIRED for this severity level'
                : isPhotoSuggested
                ? '📷 Strongly recommended for documentation'
                : 'Visual documentation of defect'
            }
          >
            {(isPhotoRequired || isPhotoSuggested) && (
              <div
                className={`mb-2 p-2 rounded text-sm ${
                  isPhotoRequired
                    ? 'bg-red-50 border border-red-300 text-red-800'
                    : 'bg-yellow-50 border border-yellow-300 text-yellow-800'
                }`}
              >
                {isPhotoRequired ? '⚠️ Photos REQUIRED for SERVICE_REQUIRED and UNSAFE_OUT_OF_SERVICE' : '📷 Photos strongly recommended'}
              </div>
            )}
            <PhotoField
              value={formData.photo_evidence || []}
              onChange={(value) => handleChange('photo_evidence', value)}
              multiple={true}
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.photo_evidence?.length || 0} photo(s) uploaded (max 10)
            </div>
          </FormField>

          {/* Corrective Action */}
          <FormField
            label="Corrective Action"
            error={errors.corrective_action}
            helpText="Recommended repair or corrective action (max 1000 characters)"
          >
            <TextArea
              value={formData.corrective_action || ''}
              onChange={(e) => handleChange('corrective_action', e.target.value)}
              placeholder="Recommended repair procedure, parts needed, or corrective actions..."
              rows={3}
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.corrective_action?.length || 0} / 1000 characters
            </div>
          </FormField>

          {/* Standard Reference */}
          <FormField
            label="Standard Reference"
            error={errors.standard_reference}
            helpText="Reference to applicable standard section (max 100 characters)"
          >
            <TextInput
              value={formData.standard_reference || ''}
              onChange={(e) => handleChange('standard_reference', e.target.value)}
              placeholder="e.g., ANSI A92.2-2021 Section 8.2.4(13)"
            />
          </FormField>

          {/* Form Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
              style={{ backgroundColor: '#7ed321' }}
            >
              {editMode ? 'Update Defect' : 'Add Defect'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
