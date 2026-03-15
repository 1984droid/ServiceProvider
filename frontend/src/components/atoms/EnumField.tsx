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
  options: string[] | Array<{ value: string; label: string }>;
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

  // Handle both string[] and {value, label}[] formats
  const selectOptions = [
    { value: '', label: placeholder },
    ...options.map(opt =>
      typeof opt === 'string'
        ? { value: opt, label: opt }
        : { value: opt.value, label: opt.label }
    )
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
