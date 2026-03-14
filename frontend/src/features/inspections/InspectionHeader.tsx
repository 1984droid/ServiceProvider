/**
 * InspectionHeader
 *
 * Header component for inspection execution page
 * Displays asset info, template name, inspector, status, and progress
 */

interface AssetInfo {
  type: 'VEHICLE' | 'EQUIPMENT';
  vin?: string;
  unit_number?: string;
  year?: number;
  make?: string;
  model?: string;
  serial_number?: string;
  asset_number?: string;
  manufacturer?: string;
  equipment_type?: string;
}

interface InspectionHeaderProps {
  assetInfo: AssetInfo | null;
  templateName: string;
  inspectorName: string;
  status: string;
  currentStep: number;
  totalSteps: number;
  completionPercent: number;
}

export function InspectionHeader({
  assetInfo,
  templateName,
  inspectorName,
  status,
  currentStep,
  totalSteps,
  completionPercent
}: InspectionHeaderProps) {

  // Format asset display name
  const getAssetName = () => {
    if (!assetInfo) return 'Unknown Asset';

    if (assetInfo.type === 'VEHICLE') {
      if (assetInfo.unit_number) {
        return `${assetInfo.unit_number} - ${assetInfo.year} ${assetInfo.make} ${assetInfo.model}`;
      }
      return `VIN: ${assetInfo.vin?.substring(0, 8)}...`;
    } else {
      if (assetInfo.asset_number) {
        return `${assetInfo.asset_number} - ${assetInfo.manufacturer} ${assetInfo.model}`;
      }
      return `S/N: ${assetInfo.serial_number}`;
    }
  };

  // Status color mapping
  const getStatusColor = () => {
    switch (status) {
      case 'IN_PROGRESS':
        return { bg: '#dbeafe', text: '#1e40af' };
      case 'DRAFT':
        return { bg: '#fef3c7', text: '#92400e' };
      case 'COMPLETED':
        return { bg: '#dcfce7', text: '#166534' };
      default:
        return { bg: '#f3f4f6', text: '#374151' };
    }
  };

  const statusColor = getStatusColor();

  return (
    <div className="border-b" style={{ borderColor: '#e5e7eb', backgroundColor: 'white' }}>
      <div className="px-6 py-4">
        {/* Asset and Template Info */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
              {getAssetName()}
            </h1>
            <p className="text-sm mt-1" style={{ color: '#6b7280' }}>
              {templateName}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="px-3 py-1 text-sm font-medium rounded-full"
              style={{ backgroundColor: statusColor.bg, color: statusColor.text }}
            >
              {status.replace(/_/g, ' ')}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium" style={{ color: '#6b7280' }}>
              Progress: Step {currentStep + 1} of {totalSteps}
            </span>
            <span className="text-xs font-medium" style={{ color: '#6b7280' }}>
              {completionPercent}%
            </span>
          </div>
          <div className="w-full h-2 rounded-full" style={{ backgroundColor: '#e5e7eb' }}>
            <div
              className="h-2 rounded-full transition-all duration-300"
              style={{
                backgroundColor: '#7ed321',
                width: `${completionPercent}%`
              }}
            />
          </div>
        </div>

        {/* Inspector Info */}
        <div className="flex items-center gap-2 text-xs" style={{ color: '#6b7280' }}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span>Inspector: {inspectorName}</span>
        </div>
      </div>
    </div>
  );
}
