/**
 * CreateWorkOrderModal
 *
 * Modal for creating work orders from selected inspection defects
 * Allows multi-select of defects and configuration of work order settings
 */

import { useState } from 'react';
import { workOrdersApi } from '@/api/workOrders.api';
import { DefectsList } from './defects/DefectsList';

interface CreateWorkOrderModalProps {
  inspectionId: string;
  defects: any[];
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (workOrders: any[]) => void;
}

export function CreateWorkOrderModal({
  inspectionId,
  defects,
  isOpen,
  onClose,
  onSuccess,
}: CreateWorkOrderModalProps) {
  const [selectedDefects, setSelectedDefects] = useState<string[]>([]);
  const [groupByLocation, setGroupByLocation] = useState(true);
  const [minSeverity, setMinSeverity] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCreate = async () => {
    if (selectedDefects.length === 0) {
      setError('Please select at least one defect');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await workOrdersApi.createFromInspection({
        inspection_id: inspectionId,
        defect_ids: selectedDefects,
        group_by_location: groupByLocation,
        min_severity: minSeverity as any,
      });

      onSuccess(result.work_orders);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to create work orders');
      setIsSubmitting(false);
    }
  };

  // Filter defects based on severity
  const filteredDefects = defects.filter((d) => {
    if (!minSeverity) return true;
    const severityOrder = ['ADVISORY', 'MINOR', 'MAJOR', 'CRITICAL'];
    const minIndex = severityOrder.indexOf(minSeverity);
    const defectIndex = severityOrder.indexOf(d.severity);
    return defectIndex >= minIndex;
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Create Work Order from Defects
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Select defects to include in work order(s)
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {/* Configuration Options */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-4">
            <h3 className="text-sm font-semibold text-gray-900">Options</h3>

            {/* Group by Location */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="groupByLocation"
                checked={groupByLocation}
                onChange={(e) => setGroupByLocation(e.target.checked)}
                className="h-4 w-4 text-blue-600 rounded border-gray-300"
              />
              <label htmlFor="groupByLocation" className="ml-2 text-sm text-gray-700">
                Group defects by location (creates multiple work orders if needed)
              </label>
            </div>

            {/* Minimum Severity Filter */}
            <div>
              <label className="block text-sm text-gray-700 mb-2">
                Minimum Severity (optional)
              </label>
              <select
                value={minSeverity || ''}
                onChange={(e) => setMinSeverity(e.target.value || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Severities</option>
                <option value="ADVISORY">ADVISORY and above</option>
                <option value="MINOR">MINOR and above</option>
                <option value="MAJOR">MAJOR and above</option>
                <option value="CRITICAL">CRITICAL only</option>
              </select>
            </div>
          </div>

          {/* Defects List */}
          <div>
            <DefectsList
              defects={filteredDefects}
              groupBySeverity={true}
              allowMultiSelect={true}
              selectedDefects={selectedDefects}
              onSelectionChange={setSelectedDefects}
              showStepInfo={true}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex gap-2">
                <svg
                  className="w-5 h-5 text-red-600 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {selectedDefects.length} defect{selectedDefects.length !== 1 ? 's' : ''} selected
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={selectedDefects.length === 0 || isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <svg
                    className="animate-spin h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span>Creating...</span>
                </>
              ) : (
                'Create Work Order(s)'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
