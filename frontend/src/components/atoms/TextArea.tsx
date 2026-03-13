/**
 * TextArea Atom
 *
 * Reusable textarea component with consistent styling.
 */

import { TextareaHTMLAttributes } from 'react';

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export function TextArea({ error, className = '', ...props }: TextAreaProps) {
  return (
    <textarea
      {...props}
      className={`w-full px-4 py-2 rounded-lg border ${className}`}
      style={{
        borderColor: error ? '#ef4444' : '#d1d5db',
        fontSize: '15px',
        outline: 'none',
        minHeight: '100px',
        resize: 'vertical'
      }}
    />
  );
}
