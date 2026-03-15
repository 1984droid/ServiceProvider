/**
 * FieldRenderer
 *
 * Routes to the correct field component based on field.type
 * Handles all 7 field types from inspection templates
 */

import { useEffect } from 'react';
import { FormField } from '@/components/molecules/FormField';
import { TextInput } from '@/components/atoms/TextInput';
import { TextArea } from '@/components/atoms/TextArea';
import { NumberInput } from '@/components/atoms/NumberInput';
import { BooleanField } from '@/components/atoms/BooleanField';
import { EnumField } from '@/components/atoms/EnumField';
import { ChoiceMultiField } from '@/components/atoms/ChoiceMultiField';
import { PhotoField } from '@/components/atoms/PhotoField';

interface SchemaField {
  field_id: string;
  label?: string;
  type: string;
  required?: boolean;
  enum_ref?: string;
  values?: string[] | Array<{ value: string; label: string }>;
  min?: number;
  max?: number;
  precision?: number;
  help_text?: string;
}

interface FieldRendererProps {
  field: SchemaField;
  value: any;
  onChange: (value: any) => void;
  error?: string;
  disabled?: boolean;
  enumValues?: Record<string, string[] | Array<{ value: string; label: string }>>; // enum_ref -> values lookup
}

export function FieldRenderer({
  field,
  value,
  onChange,
  error,
  disabled = false,
  enumValues = {}
}: FieldRendererProps) {

  const fieldType = field.type.toUpperCase();

  // Wide fields span 2 columns in grid layout
  const isWideField = fieldType === 'TEXT_AREA' || fieldType === 'TEXTAREA' || fieldType === 'PHOTO' || fieldType === 'ATTACHMENTS';

  // Render the appropriate input based on field type
  const renderInput = () => {
    switch (fieldType) {
      case 'BOOLEAN':
        return (
          <BooleanField
            value={value}
            onChange={onChange}
            disabled={disabled}
            mode="yesno"
          />
        );

      case 'TEXT':
        return (
          <TextInput
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            error={!!error}
            disabled={disabled}
          />
        );

      case 'TEXT_AREA':
      case 'TEXTAREA':
        return (
          <TextArea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            error={!!error}
            disabled={disabled}
            rows={4}
          />
        );

      case 'NUMBER':
        return (
          <NumberInput
            value={value}
            onChange={onChange}
            error={!!error}
            disabled={disabled}
            min={field.min}
            max={field.max}
            precision={field.precision}
          />
        );

      case 'ENUM':
        // Get enum values from either field.values or enum_ref lookup
        const options = field.values || (field.enum_ref ? enumValues[field.enum_ref] : []) || [];
        return (
          <EnumField
            value={value || ''}
            onChange={onChange}
            options={options}
            error={!!error}
            disabled={disabled}
          />
        );

      case 'CHOICE_MULTI':
        // Get options from either field.values or enum_ref lookup
        const multiOptions = field.values || (field.enum_ref ? enumValues[field.enum_ref] : []) || [];
        return (
          <ChoiceMultiField
            value={value || []}
            onChange={onChange}
            options={multiOptions}
            disabled={disabled}
          />
        );

      case 'PHOTO':
      case 'ATTACHMENTS':
        return (
          <PhotoField
            value={value || []}
            onChange={onChange}
            disabled={disabled}
            multiple={true}
          />
        );

      case 'DATE':
        // Auto-default to today's date if no value
        useEffect(() => {
          if (!value) {
            const today = new Date().toISOString().split('T')[0];
            onChange(today);
          }
        }, []);

        return (
          <input
            type="date"
            value={value || new Date().toISOString().split('T')[0]}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          />
        );

      default:
        return (
          <div className="p-3 border rounded" style={{ borderColor: '#fbbf24', backgroundColor: '#fef3c7' }}>
            <p className="text-sm" style={{ color: '#92400e' }}>
              Unsupported field type: {field.type}
            </p>
          </div>
        );
    }
  };

  return (
    <div className={isWideField ? 'col-span-2' : ''}>
      <FormField
        label={field.label || field.field_id}
        required={field.required}
        error={error}
        htmlFor={field.field_id}
      >
        {renderInput()}
        {field.help_text && !error && (
          <p className="mt-1 text-xs" style={{ color: '#6b7280' }}>
            {field.help_text}
          </p>
        )}
      </FormField>
    </div>
  );
}
