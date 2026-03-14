/**
 * BooleanField Atom
 *
 * Reusable boolean input component (checkbox or radio buttons)
 * Used for BOOLEAN field type in inspection templates
 */

interface BooleanFieldProps {
  value: boolean | null;
  onChange: (value: boolean) => void;
  label?: string;
  disabled?: boolean;
  mode?: 'checkbox' | 'yesno' | 'passifail';
}

export function BooleanField({
  value,
  onChange,
  label,
  disabled = false,
  mode = 'checkbox'
}: BooleanFieldProps) {

  if (mode === 'checkbox') {
    return (
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={value === true}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="w-5 h-5 rounded"
          style={{ accentColor: '#7ed321' }}
        />
        {label && <span style={{ color: disabled ? '#9ca3af' : '#374151' }}>{label}</span>}
      </label>
    );
  }

  // Yes/No or Pass/Fail radio buttons
  const options = mode === 'passifail'
    ? [{ label: 'Pass', value: true }, { label: 'Fail', value: false }]
    : [{ label: 'Yes', value: true }, { label: 'No', value: false }];

  return (
    <div className="flex gap-4">
      {options.map((option) => (
        <label
          key={option.label}
          className="flex items-center gap-2 cursor-pointer"
        >
          <input
            type="radio"
            checked={value === option.value}
            onChange={() => onChange(option.value)}
            disabled={disabled}
            className="w-4 h-4"
            style={{ accentColor: '#7ed321' }}
          />
          <span style={{ color: disabled ? '#9ca3af' : '#374151' }}>
            {option.label}
          </span>
        </label>
      ))}
    </div>
  );
}
