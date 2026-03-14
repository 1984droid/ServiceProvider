/**
 * NumberInput Atom
 *
 * Reusable number input component with validation
 * Used for NUMBER field type in inspection templates
 */

import { InputHTMLAttributes } from 'react';

interface NumberInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'value'> {
  value: number | null;
  onChange: (value: number | null) => void;
  error?: boolean;
  min?: number;
  max?: number;
  precision?: number;
}

export function NumberInput({
  value,
  onChange,
  error,
  min,
  max,
  precision,
  className = '',
  disabled,
  ...props
}: NumberInputProps) {

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (val === '') {
      onChange(null);
      return;
    }

    const num = Number(val);
    if (!isNaN(num)) {
      onChange(num);
    }
  };

  return (
    <input
      {...props}
      type="number"
      value={value ?? ''}
      onChange={handleChange}
      min={min}
      max={max}
      step={precision !== undefined ? Math.pow(10, -precision) : undefined}
      disabled={disabled}
      className={`w-full px-4 py-2 rounded-lg border ${className}`}
      style={{
        borderColor: error ? '#ef4444' : '#d1d5db',
        fontSize: '15px',
        outline: 'none'
      }}
    />
  );
}
