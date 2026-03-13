/**
 * SectionHeader - Reusable section header with optional actions
 *
 * Atomic component for consistent section headers
 */

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function SectionHeader({ title, subtitle, action }: SectionHeaderProps) {
  return (
    <div className="flex items-start justify-between pb-3 border-b border-gray-200">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          {title}
        </h2>
        {subtitle && (
          <p className="mt-1 text-xs text-gray-500">
            {subtitle}
          </p>
        )}
      </div>
      {action && (
        <div>
          {action}
        </div>
      )}
    </div>
  );
}
