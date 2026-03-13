/**
 * FormField Molecule
 *
 * Combines label, input, and error message into a single form field component.
 */

import { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  required?: boolean;
  error?: string;
  children: ReactNode;
  htmlFor?: string;
}

export function FormField({ label, required, error, children, htmlFor }: FormFieldProps) {
  return (
    <div className="mb-5">
      <label htmlFor={htmlFor} className="block text-sm font-semibold mb-2" style={{ color: '#111827' }}>
        {label}
        {required && <span style={{ color: '#ef4444' }}> *</span>}
      </label>
      {children}
      {error && (
        <p className="mt-1 text-sm" style={{ color: '#ef4444' }}>
          {error}
        </p>
      )}
    </div>
  );
}
