/**
 * DefectsList
 *
 * List component for displaying multiple defects
 * Features:
 * - Group by severity
 * - Filter by severity/status
 * - Multi-select capability
 * - Summary statistics
 */

import { useState } from 'react';
import { DefectCard } from './DefectCard';
import { DefectBadge } from './DefectBadge';

interface Defect {
  id: string;
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY';
  status: 'OPEN' | 'WORK_ORDER_CREATED' | 'RESOLVED';
  title: string;
  description?: string;
  step_key: string;
  defect_details?: any;
  created_at: string;
}

interface DefectsListProps {
  defects: Defect[];
  groupBySeverity?: boolean;
  allowMultiSelect?: boolean;
  selectedDefects?: string[];
  onSelectionChange?: (selectedIds: string[]) => void;
  showStepInfo?: boolean;
}

export function DefectsList({
  defects,
  groupBySeverity = true,
  allowMultiSelect = false,
  selectedDefects = [],
  onSelectionChange,
  showStepInfo = true,
}: DefectsListProps) {
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  // Filter defects
  const filteredDefects = defects.filter((defect) => {
    if (filterSeverity && defect.severity !== filterSeverity) return false;
    if (filterStatus && defect.status !== filterStatus) return false;
    return true;
  });

  // Group by severity
  const groupedDefects = groupBySeverity
    ? {
        CRITICAL: filteredDefects.filter((d) => d.severity === 'CRITICAL'),
        MAJOR: filteredDefects.filter((d) => d.severity === 'MAJOR'),
        MINOR: filteredDefects.filter((d) => d.severity === 'MINOR'),
        ADVISORY: filteredDefects.filter((d) => d.severity === 'ADVISORY'),
      }
    : { ALL: filteredDefects };

  // Calculate summary
  const summary = {
    total: defects.length,
    critical: defects.filter((d) => d.severity === 'CRITICAL').length,
    major: defects.filter((d) => d.severity === 'MAJOR').length,
    minor: defects.filter((d) => d.severity === 'MINOR').length,
    advisory: defects.filter((d) => d.severity === 'ADVISORY').length,
    open: defects.filter((d) => d.status === 'OPEN').length,
    workOrderCreated: defects.filter((d) => d.status === 'WORK_ORDER_CREATED')
      .length,
    resolved: defects.filter((d) => d.status === 'RESOLVED').length,
  };

  const handleDefectSelect = (defectId: string) => {
    if (!allowMultiSelect || !onSelectionChange) return;

    const newSelection = selectedDefects.includes(defectId)
      ? selectedDefects.filter((id) => id !== defectId)
      : [...selectedDefects, defectId];

    onSelectionChange(newSelection);
  };

  const handleSelectAll = () => {
    if (!onSelectionChange) return;
    onSelectionChange(
      selectedDefects.length === filteredDefects.length
        ? []
        : filteredDefects.map((d) => d.id)
    );
  };

  if (defects.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
        <div className="text-gray-400 mb-2">
          <svg
            className="w-12 h-12 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-gray-600 font-medium">No defects found</p>
        <p className="text-sm text-gray-500 mt-1">
          This inspection passed all checks
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {summary.total} Defect{summary.total !== 1 ? 's' : ''} Found
            </h3>
            <div className="flex items-center gap-4 mt-2">
              {summary.critical > 0 && (
                <button
                  onClick={() =>
                    setFilterSeverity(
                      filterSeverity === 'CRITICAL' ? null : 'CRITICAL'
                    )
                  }
                  className={`flex items-center gap-2 px-2 py-1 rounded transition-colors ${
                    filterSeverity === 'CRITICAL'
                      ? 'bg-red-100'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <DefectBadge severity="CRITICAL" size="sm" />
                  <span className="text-sm font-medium text-gray-700">
                    {summary.critical}
                  </span>
                </button>
              )}
              {summary.major > 0 && (
                <button
                  onClick={() =>
                    setFilterSeverity(
                      filterSeverity === 'MAJOR' ? null : 'MAJOR'
                    )
                  }
                  className={`flex items-center gap-2 px-2 py-1 rounded transition-colors ${
                    filterSeverity === 'MAJOR'
                      ? 'bg-orange-100'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <DefectBadge severity="MAJOR" size="sm" />
                  <span className="text-sm font-medium text-gray-700">
                    {summary.major}
                  </span>
                </button>
              )}
              {summary.minor > 0 && (
                <button
                  onClick={() =>
                    setFilterSeverity(
                      filterSeverity === 'MINOR' ? null : 'MINOR'
                    )
                  }
                  className={`flex items-center gap-2 px-2 py-1 rounded transition-colors ${
                    filterSeverity === 'MINOR'
                      ? 'bg-yellow-100'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <DefectBadge severity="MINOR" size="sm" />
                  <span className="text-sm font-medium text-gray-700">
                    {summary.minor}
                  </span>
                </button>
              )}
              {summary.advisory > 0 && (
                <button
                  onClick={() =>
                    setFilterSeverity(
                      filterSeverity === 'ADVISORY' ? null : 'ADVISORY'
                    )
                  }
                  className={`flex items-center gap-2 px-2 py-1 rounded transition-colors ${
                    filterSeverity === 'ADVISORY'
                      ? 'bg-blue-100'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <DefectBadge severity="ADVISORY" size="sm" />
                  <span className="text-sm font-medium text-gray-700">
                    {summary.advisory}
                  </span>
                </button>
              )}
            </div>
          </div>

          {allowMultiSelect && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                {selectedDefects.length} selected
              </span>
              <button
                onClick={handleSelectAll}
                className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors"
              >
                {selectedDefects.length === filteredDefects.length
                  ? 'Deselect All'
                  : 'Select All'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Status Filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Status:</span>
        <button
          onClick={() => setFilterStatus(null)}
          className={`px-3 py-1 text-sm rounded transition-colors ${
            filterStatus === null
              ? 'bg-gray-900 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({summary.total})
        </button>
        <button
          onClick={() =>
            setFilterStatus(filterStatus === 'OPEN' ? null : 'OPEN')
          }
          className={`px-3 py-1 text-sm rounded transition-colors ${
            filterStatus === 'OPEN'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Open ({summary.open})
        </button>
        <button
          onClick={() =>
            setFilterStatus(
              filterStatus === 'WORK_ORDER_CREATED'
                ? null
                : 'WORK_ORDER_CREATED'
            )
          }
          className={`px-3 py-1 text-sm rounded transition-colors ${
            filterStatus === 'WORK_ORDER_CREATED'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Work Order Created ({summary.workOrderCreated})
        </button>
        <button
          onClick={() =>
            setFilterStatus(filterStatus === 'RESOLVED' ? null : 'RESOLVED')
          }
          className={`px-3 py-1 text-sm rounded transition-colors ${
            filterStatus === 'RESOLVED'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Resolved ({summary.resolved})
        </button>
      </div>

      {/* Defects List */}
      <div className="space-y-6">
        {Object.entries(groupedDefects).map(([severity, defectsInGroup]) => {
          if (defectsInGroup.length === 0) return null;

          return (
            <div key={severity}>
              {groupBySeverity && (
                <div className="flex items-center gap-2 mb-3">
                  <DefectBadge
                    severity={severity as any}
                    size="md"
                  />
                  <span className="text-sm font-medium text-gray-600">
                    {defectsInGroup.length} defect
                    {defectsInGroup.length !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
              <div className="space-y-3">
                {defectsInGroup.map((defect) => (
                  <DefectCard
                    key={defect.id}
                    defect={defect}
                    showStepInfo={showStepInfo}
                    onSelect={allowMultiSelect ? handleDefectSelect : undefined}
                    selected={selectedDefects.includes(defect.id)}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {filteredDefects.length === 0 && defects.length > 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No defects match the selected filters</p>
        </div>
      )}
    </div>
  );
}
