/**
 * InfoSection - Reusable key-value pair display
 *
 * Atomic component for displaying labeled information
 */

interface InfoItem {
  label: string;
  value: string | number | null | undefined;
  span?: 1 | 2; // Grid column span
}

interface InfoSectionProps {
  title?: string;
  items: InfoItem[];
  columns?: 1 | 2 | 3;
}

export function InfoSection({ title, items, columns = 2 }: InfoSectionProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
  };

  return (
    <div className="space-y-3">
      {title && (
        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
          {title}
        </h3>
      )}
      <div className={`grid ${gridCols[columns]} gap-4`}>
        {items.map((item, index) => (
          <div
            key={index}
            className={item.span === 2 ? 'col-span-2' : ''}
          >
            <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {item.label}
            </dt>
            <dd className="mt-1 text-sm text-gray-900">
              {item.value || <span className="text-gray-400 italic">Not provided</span>}
            </dd>
          </div>
        ))}
      </div>
    </div>
  );
}
