/**
 * ChoiceMultiField Atom
 *
 * Reusable multiple choice component (checkbox group)
 * Used for CHOICE_MULTI field type in inspection templates
 */

interface ChoiceMultiFieldProps {
  value: string[];
  onChange: (value: string[]) => void;
  options: string[];
  disabled?: boolean;
}

export function ChoiceMultiField({
  value,
  onChange,
  options,
  disabled = false
}: ChoiceMultiFieldProps) {

  const handleToggle = (option: string) => {
    if (value.includes(option)) {
      onChange(value.filter(v => v !== option));
    } else {
      onChange([...value, option]);
    }
  };

  return (
    <div className="space-y-2">
      {options.map((option) => (
        <label
          key={option}
          className="flex items-center gap-2 cursor-pointer"
        >
          <input
            type="checkbox"
            checked={value.includes(option)}
            onChange={() => handleToggle(option)}
            disabled={disabled}
            className="w-4 h-4 rounded"
            style={{ accentColor: '#7ed321' }}
          />
          <span style={{ color: disabled ? '#9ca3af' : '#374151' }}>
            {option}
          </span>
        </label>
      ))}
    </div>
  );
}
