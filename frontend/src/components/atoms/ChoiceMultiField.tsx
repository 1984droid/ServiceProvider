/**
 * ChoiceMultiField Atom
 *
 * Reusable multiple choice component (checkbox group)
 * Used for CHOICE_MULTI field type in inspection templates
 */

interface ChoiceMultiFieldProps {
  value: string[];
  onChange: (value: string[]) => void;
  options: string[] | Array<{ value: string; label: string }>;
  disabled?: boolean;
}

export function ChoiceMultiField({
  value,
  onChange,
  options,
  disabled = false
}: ChoiceMultiFieldProps) {

  const handleToggle = (optionValue: string) => {
    if (value.includes(optionValue)) {
      onChange(value.filter(v => v !== optionValue));
    } else {
      onChange([...value, optionValue]);
    }
  };

  // Normalize options to {value, label} format
  const normalizedOptions = options.map(opt =>
    typeof opt === 'string'
      ? { value: opt, label: opt }
      : opt
  );

  return (
    <div className="space-y-2">
      {normalizedOptions.map((option) => (
        <label
          key={option.value}
          className="flex items-center gap-2 cursor-pointer"
        >
          <input
            type="checkbox"
            checked={value.includes(option.value)}
            onChange={() => handleToggle(option.value)}
            disabled={disabled}
            className="w-4 h-4 rounded"
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
