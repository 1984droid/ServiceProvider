/**
 * EnumField Atom
 *
 * Reusable enum/choice input component (single selection)
 * Used for ENUM field type in inspection templates
 */

import { Select } from './Select';

interface EnumFieldProps {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  error?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function EnumField({
  value,
  onChange,
  options,
  error,
  disabled,
  placeholder = 'Select...'
}: EnumFieldProps) {

  const selectOptions = [
    { value: '', label: placeholder },
    ...options.map(opt => ({ value: opt, label: opt }))
  ];

  return (
    <Select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      options={selectOptions}
      error={error}
      disabled={disabled}
    />
  );
}
