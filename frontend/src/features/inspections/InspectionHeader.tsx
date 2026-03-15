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

  // Get asset thumbnail icon
  const getAssetIcon = () => {
    if (!assetInfo) return null;

    const iconColor = '#7ed321';

    if (assetInfo.type === 'VEHICLE') {
      return (
        <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke={iconColor} strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" />
        </svg>
      );
    } else {
      return (
        <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke={iconColor} strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
        </svg>
      );
    }
  };

  return (
    <div className="border-b" style={{ borderColor: '#e5e7eb', backgroundColor: 'white' }}>
      <div className="px-4 py-2">
        <div className="flex items-center gap-3">
          {/* Asset Thumbnail */}
          <div className="flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#f0fdf4' }}>
            <svg className={assetInfo?.type === 'VEHICLE' ? "w-7 h-7" : "w-7 h-7"} fill="none" viewBox="0 0 24 24" stroke="#7ed321" strokeWidth={1.5}>
              {assetInfo?.type === 'VEHICLE' ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
              )}
            </svg>
          </div>

          {/* Asset & Template Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold truncate" style={{ color: '#111827' }}>
                {getAssetName()}
              </h1>
              <span
                className="px-1.5 py-0.5 text-xs font-medium rounded-full whitespace-nowrap"
                style={{ backgroundColor: statusColor.bg, color: statusColor.text }}
              >
                {status.replace(/_/g, ' ')}
              </span>
            </div>
            <p className="text-xs truncate" style={{ color: '#6b7280' }}>
              {templateName}
            </p>
          </div>

          {/* Progress & Inspector - Condensed */}
          <div className="flex-shrink-0 text-right">
            <div className="flex items-center gap-1.5 justify-end">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="#6b7280">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span className="text-xs" style={{ color: '#6b7280' }}>
                {inspectorName}
              </span>
            </div>
            <div className="text-xs font-medium" style={{ color: '#6b7280' }}>
              Step {currentStep + 1}/{totalSteps} · {completionPercent}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
