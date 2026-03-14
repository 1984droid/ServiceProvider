/**
 * StepHeader
 *
 * Shared header component for all step types
 * Displays step title, standard reference, and progress
 */

interface StepHeaderProps {
  title: string;
  standardReference?: string;
  currentIndex: number;
  totalSteps: number;
  stepType?: string;
}

export function StepHeader({
  title,
  standardReference,
  currentIndex,
  totalSteps,
  stepType
}: StepHeaderProps) {
  return (
    <div className="mb-6">
      {/* Progress indicator */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium" style={{ color: '#6b7280' }}>
          Step {currentIndex + 1} of {totalSteps}
        </span>
        {stepType && (
          <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: '#e5e7eb', color: '#374151' }}>
            {stepType.replace(/_/g, ' ')}
          </span>
        )}
      </div>

      {/* Title */}
      <h2 className="text-2xl font-bold mb-2" style={{ color: '#111827' }}>
        {title}
      </h2>

      {/* Standard reference */}
      {standardReference && (
        <p className="text-sm" style={{ color: '#6b7280' }}>
          Reference: {standardReference}
        </p>
      )}
    </div>
  );
}
