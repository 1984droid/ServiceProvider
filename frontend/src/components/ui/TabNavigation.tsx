/**
 * TabNavigation - Reusable tab navigation component
 *
 * Atomic component for creating tabbed interfaces
 */

export interface Tab {
  key: string;
  label: string;
  count?: number;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (key: string) => void;
}

export function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="border-b border-gray-200">
      <div className="flex gap-4">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => onTabChange(tab.key)}
            className="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap"
            style={{
              borderColor: activeTab === tab.key ? '#7ed321' : 'transparent',
              color: activeTab === tab.key ? '#7ed321' : '#6b7280',
            }}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className="ml-2 text-xs" style={{
                color: activeTab === tab.key ? '#7ed321' : '#9ca3af'
              }}>
                ({tab.count})
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
