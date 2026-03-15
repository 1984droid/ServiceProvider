/**
 * StepDefectsList
 *
 * Display and manage defects within an inspection step
 * Shows defects added during step execution
 * Allows edit/delete before inspection finalization
 */

import type { DefectData } from './defectTypes';

interface StepDefectsListProps {
  defects: DefectData[];
  onEdit: (defect: DefectData) => void;
  onDelete: (defectId: string) => void;
  disabled?: boolean;
}

const SEVERITY_COLORS: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  SAFE: {
    bg: '#d1fae5',
    border: '#10b981',
    text: '#065f46',
    icon: '✓',
  },
  MINOR: {
    bg: '#fef3c7',
    border: '#f59e0b',
    text: '#92400e',
    icon: '!',
  },
  SERVICE_REQUIRED: {
    bg: '#fed7aa',
    border: '#ea580c',
    text: '#7c2d12',
    icon: '⚠',
  },
  UNSAFE_OUT_OF_SERVICE: {
    bg: '#fee2e2',
    border: '#dc2626',
    text: '#991b1b',
    icon: '✖',
  },
};

export function StepDefectsList({
  defects,
  onEdit,
  onDelete,
  disabled = false,
}: StepDefectsListProps) {
  if (defects.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 space-y-3">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-gray-900">
          Defects Documented ({defects.length})
        </h4>
      </div>

      <div className="space-y-3">
        {defects.map((defect, index) => {
          const severityStyle = SEVERITY_COLORS[defect.severity];

          return (
            <div
              key={defect.defect_id}
              className="p-4 rounded-lg border-l-4"
              style={{
                backgroundColor: severityStyle.bg,
                borderLeftColor: severityStyle.border,
              }}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span
                    className="text-sm font-bold px-2 py-0.5 rounded"
                    style={{
                      backgroundColor: severityStyle.border,
                      color: 'white',
                    }}
                  >
                    {severityStyle.icon} {defect.severity.replace('_', ' ')}
                  </span>
                  {defect.photo_evidence && defect.photo_evidence.length > 0 && (
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-200 text-gray-700">
                      📷 {defect.photo_evidence.length} photo(s)
                    </span>
                  )}
                </div>
                {!disabled && (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => onEdit(defect)}
                      className="text-xs px-2 py-1 text-blue-600 hover:bg-blue-100 rounded transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        if (window.confirm('Delete this defect?')) {
                          onDelete(defect.defect_id);
                        }
                      }}
                      className="text-xs px-2 py-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>

              {/* Title */}
              <h5 className="font-semibold text-base mb-2" style={{ color: severityStyle.text }}>
                {defect.title}
              </h5>

              {/* Description */}
              <p className="text-sm mb-2" style={{ color: severityStyle.text }}>
                {defect.description}
              </p>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-2 text-sm">
                {defect.component && (
                  <div>
                    <span className="font-medium" style={{ color: severityStyle.text }}>Component: </span>
                    <span style={{ color: severityStyle.text }}>{defect.component}</span>
                  </div>
                )}
                {defect.location && (
                  <div>
                    <span className="font-medium" style={{ color: severityStyle.text }}>Location: </span>
                    <span style={{ color: severityStyle.text }}>{defect.location}</span>
                  </div>
                )}
              </div>

              {/* Corrective Action */}
              {defect.corrective_action && (
                <div className="mt-2 p-2 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.5)' }}>
                  <div className="text-xs font-medium mb-1" style={{ color: severityStyle.text }}>
                    Corrective Action:
                  </div>
                  <div className="text-sm" style={{ color: severityStyle.text }}>
                    {defect.corrective_action}
                  </div>
                </div>
              )}

              {/* Standard Reference */}
              {defect.standard_reference && (
                <div className="mt-2 text-xs" style={{ color: severityStyle.text }}>
                  <span className="font-medium">Standard: </span>
                  {defect.standard_reference}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
