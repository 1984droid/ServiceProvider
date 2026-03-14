/**
 * DefectBadge
 *
 * Visual severity badge for defects
 * Color-coded: CRITICAL (red), MAJOR (orange), MINOR (yellow), ADVISORY (blue)
 */

interface DefectBadgeProps {
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY';
  size?: 'sm' | 'md' | 'lg';
}

export function DefectBadge({ severity, size = 'md' }: DefectBadgeProps) {
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };

  const colorClasses = {
    CRITICAL: 'bg-red-600 text-white',
    MAJOR: 'bg-orange-600 text-white',
    MINOR: 'bg-yellow-600 text-white',
    ADVISORY: 'bg-blue-600 text-white',
  };

  return (
    <span
      className={`${sizeClasses[size]} ${colorClasses[severity]} font-bold rounded inline-block`}
    >
      {severity}
    </span>
  );
}
