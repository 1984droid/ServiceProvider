/**
 * StatCard - Reusable statistic display card
 *
 * Atomic component for displaying key metrics and statistics
 */

interface StatCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

export function StatCard({ label, value, subtitle, icon, variant = 'default' }: StatCardProps) {
  const variantStyles = {
    default: { bg: '#ffffff', border: '#e5e7eb', text: '#111827', label: '#6b7280' },
    success: { bg: '#f0fdf4', border: '#bbf7d0', text: '#15803d', label: '#166534' },
    warning: { bg: '#fefce8', border: '#fef08a', text: '#854d0e', label: '#a16207' },
    danger: { bg: '#fef2f2', border: '#fecaca', text: '#dc2626', label: '#991b1b' },
    info: { bg: '#dbeafe', border: '#93c5fd', text: '#1e40af', label: '#1e3a8a' },
  };

  const colors = variantStyles[variant];

  return (
    <div
      className="p-4 rounded-lg border"
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wide" style={{ color: colors.label }}>
            {label}
          </p>
          <p className="mt-2 text-2xl font-bold" style={{ color: colors.text }}>
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs" style={{ color: colors.label }}>
              {subtitle}
            </p>
          )}
        </div>
        {icon && (
          <div style={{ color: colors.text }}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
