/**
 * Badge - Reusable status/label badge component
 *
 * Atomic component for displaying status indicators and labels
 */

interface BadgeProps {
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
}

export function Badge({ label, variant = 'default', size = 'sm' }: BadgeProps) {
  const variantStyles = {
    default: { bg: '#f3f4f6', text: '#6b7280' },
    success: { bg: '#dcfce7', text: '#166534' },
    warning: { bg: '#fef9c3', text: '#854d0e' },
    danger: { bg: '#fee2e2', text: '#991b1b' },
    info: { bg: '#dbeafe', text: '#1e40af' },
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  const colors = variantStyles[variant];

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeStyles[size]}`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
      }}
    >
      {label}
    </span>
  );
}
