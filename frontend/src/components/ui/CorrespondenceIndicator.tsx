/**
 * CorrespondenceIndicator - Shows contact subscription preferences
 *
 * Atomic component for displaying what correspondence types a contact receives
 */

interface CorrespondenceIndicatorProps {
  subscriptions: {
    invoices: boolean;
    estimates: boolean;
    service_updates: boolean;
    inspection_reports: boolean;
  };
  size?: 'sm' | 'md';
}

export function CorrespondenceIndicator({ subscriptions, size = 'sm' }: CorrespondenceIndicatorProps) {
  const items = [
    { key: 'invoices', label: 'Invoices', enabled: subscriptions.invoices },
    { key: 'estimates', label: 'Estimates', enabled: subscriptions.estimates },
    { key: 'service_updates', label: 'Service Updates', enabled: subscriptions.service_updates },
    { key: 'inspection_reports', label: 'Inspection Reports', enabled: subscriptions.inspection_reports },
  ];

  const activeItems = items.filter(item => item.enabled);

  if (activeItems.length === 0) {
    return (
      <span className="text-xs text-gray-400 italic">
        No subscriptions
      </span>
    );
  }

  const textSize = size === 'sm' ? 'text-xs' : 'text-sm';

  return (
    <div className="flex flex-wrap gap-1">
      {activeItems.map(item => (
        <span
          key={item.key}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded ${textSize}`}
          style={{ backgroundColor: '#dcfce7', color: '#166534' }}
        >
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {item.label}
        </span>
      ))}
    </div>
  );
}
