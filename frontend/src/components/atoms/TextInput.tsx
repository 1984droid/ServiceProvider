/**
 * TextInput Atom
 *
 * Reusable text input component with consistent styling.
 */

import { InputHTMLAttributes } from 'react';

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export function TextInput({ error, className = '', ...props }: TextInputProps) {
  return (
    <input
      {...props}
      className={`w-full px-4 py-2 rounded-lg border ${className}`}
      style={{
        borderColor: error ? '#ef4444' : '#d1d5db',
        fontSize: '15px',
        outline: 'none'
      }}
    />
  );
}
