/**
 * Select Atom
 *
 * Reusable select component with consistent styling.
 */

import { SelectHTMLAttributes } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
  options: { value: string; label: string }[];
}

export function Select({ error, options, className = '', ...props }: SelectProps) {
  return (
    <select
      {...props}
      className={`w-full px-4 py-2 rounded-lg border ${className}`}
      style={{
        borderColor: error ? '#ef4444' : '#d1d5db',
        fontSize: '15px',
        outline: 'none',
        backgroundColor: 'white'
      }}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
