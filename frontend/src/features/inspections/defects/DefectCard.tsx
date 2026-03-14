/**
 * DefectCard
 *
 * Card component for displaying a single defect with all details
 * Shows severity, status, title, description, photos, and metadata
 */

import { DefectBadge } from './DefectBadge';

interface Defect {
  id: string;
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY';
  status: 'OPEN' | 'WORK_ORDER_CREATED' | 'RESOLVED';
  title: string;
  description?: string;
  step_key: string;
  defect_details?: {
    location?: string;
    photos?: string[];
    measurements?: Record<string, any>;
    [key: string]: any;
  };
  created_at: string;
}

interface DefectCardProps {
  defect: Defect;
  showStepInfo?: boolean;
  onSelect?: (defectId: string) => void;
  selected?: boolean;
}

export function DefectCard({
  defect,
  showStepInfo = false,
  onSelect,
  selected = false,
}: DefectCardProps) {
  const statusColors = {
    OPEN: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    WORK_ORDER_CREATED: 'bg-blue-100 text-blue-800 border-blue-300',
    RESOLVED: 'bg-green-100 text-green-800 border-green-300',
  };

  return (
    <div
      className={`p-4 border rounded-lg transition-all ${
        selected
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      } ${onSelect ? 'cursor-pointer' : ''}`}
      onClick={() => onSelect?.(defect.id)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <DefectBadge severity={defect.severity} />
            <span
              className={`px-2 py-0.5 text-xs font-medium rounded border ${
                statusColors[defect.status]
              }`}
            >
              {defect.status.replace('_', ' ')}
            </span>
            {showStepInfo && (
              <span className="text-xs text-gray-500">
                Step: {defect.step_key}
              </span>
            )}
          </div>
          <h4 className="font-semibold text-gray-900 text-base">
            {defect.title}
          </h4>
        </div>
        {onSelect && (
          <input
            type="checkbox"
            checked={selected}
            onChange={() => onSelect(defect.id)}
            className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300"
            onClick={(e) => e.stopPropagation()}
          />
        )}
      </div>

      {/* Description */}
      {defect.description && (
        <p className="text-sm text-gray-700 mb-3">{defect.description}</p>
      )}

      {/* Defect Details */}
      {defect.defect_details && (
        <div className="space-y-2">
          {/* Location */}
          {defect.defect_details.location && (
            <div className="text-sm">
              <span className="font-medium text-gray-700">Location: </span>
              <span className="text-gray-600">
                {defect.defect_details.location}
              </span>
            </div>
          )}

          {/* Photos */}
          {defect.defect_details.photos &&
            defect.defect_details.photos.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">
                  Photos ({defect.defect_details.photos.length})
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {defect.defect_details.photos.map((photo, index) => (
                    <div
                      key={index}
                      className="aspect-square bg-gray-100 rounded border border-gray-200 overflow-hidden"
                    >
                      <img
                        src={photo}
                        alt={`Defect photo ${index + 1}`}
                        className="w-full h-full object-cover hover:scale-110 transition-transform cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Open lightbox/modal for full-size view
                          window.open(photo, '_blank');
                        }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Measurements */}
          {defect.defect_details.measurements && (
            <div className="text-sm">
              <div className="font-medium text-gray-700 mb-1">
                Measurements:
              </div>
              <div className="bg-gray-50 p-2 rounded border border-gray-200">
                <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                  {JSON.stringify(defect.defect_details.measurements, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Metadata */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="text-xs text-gray-500">
          Created: {new Date(defect.created_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
