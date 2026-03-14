/**
 * DefectForm
 *
 * Form for creating manual defects during inspection
 */

import { useState } from 'react';
import { FormField } from '@/components/molecules/FormField';
import { TextInput } from '@/components/atoms/TextInput';
import { TextArea } from '@/components/atoms/TextArea';
import { Select } from '@/components/atoms/Select';
import { Button } from '@/components/atoms/Button';

interface DefectFormData {
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY' | '';
  title: string;
  description: string;
  location?: string;
}

interface DefectFormProps {
  onSubmit: (data: DefectFormData) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const SEVERITY_OPTIONS = [
  { value: '', label: 'Select severity...' },
  { value: 'CRITICAL', label: 'Critical - Unsafe to operate' },
  { value: 'MAJOR', label: 'Major - Significant issue' },
  { value: 'MINOR', label: 'Minor - Maintenance needed' },
  { value: 'ADVISORY', label: 'Advisory - Informational' },
];

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  MAJOR: '#ea580c',
  MINOR: '#f59e0b',
  ADVISORY: '#3b82f6',
};

export function DefectForm({
  onSubmit,
  onCancel,
  isSubmitting = false,
}: DefectFormProps) {
  const [formData, setFormData] = useState<DefectFormData>({
    severity: '',
    title: '',
    description: '',
    location: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: keyof DefectFormData, value: string) => {
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

    if (!formData.severity) {
      newErrors.severity = 'Severity is required';
    }

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Severity */}
      <FormField
        label="Severity"
        required
        error={errors.severity}
      >
        <Select
          value={formData.severity}
          onChange={(e) => handleChange('severity', e.target.value)}
          options={SEVERITY_OPTIONS}
          disabled={isSubmitting}
        />
        {formData.severity && (
          <div
            className="mt-2 p-2 rounded text-xs text-white"
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
        helpText="Short description of the defect"
      >
        <TextInput
          value={formData.title}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="e.g., Hydraulic fluid leak on boom cylinder"
          disabled={isSubmitting}
        />
      </FormField>

      {/* Description */}
      <FormField
        label="Description"
        required
        error={errors.description}
        helpText="Detailed description of the defect"
      >
        <TextArea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Provide detailed information about the defect, location, and any relevant observations..."
          rows={4}
          disabled={isSubmitting}
        />
      </FormField>

      {/* Location (optional) */}
      <FormField
        label="Location"
        helpText="Specific location on the equipment where defect was found"
      >
        <TextInput
          value={formData.location || ''}
          onChange={(e) => handleChange('location', e.target.value)}
          placeholder="e.g., Left rear boom cylinder"
          disabled={isSubmitting}
        />
      </FormField>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 border-t" style={{ borderColor: '#e5e7eb' }}>
        <Button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          variant="secondary"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          variant="primary"
        >
          {isSubmitting ? 'Adding Defect...' : 'Add Defect'}
        </Button>
      </div>
    </form>
  );
}
