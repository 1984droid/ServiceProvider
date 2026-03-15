/**
 * InspectionsListPage
 *
 * Display list of inspection runs with filtering
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useEffect, useState } from 'react';
import { inspectionsApi, type InspectionRun } from '@/api/inspections.api';

interface InspectionsListPageProps {
  onViewInspection: (inspectionId: string) => void;
}

export function InspectionsListPage({ onViewInspection }: InspectionsListPageProps) {
  const [inspections, setInspections] = useState<InspectionRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadInspections();
  }, []);

  const loadInspections = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await inspectionsApi.list();
      setInspections(data.inspections);
    } catch (err: any) {
      setError(err.message || 'Failed to load inspections');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredInspections = (inspections || []).filter(inspection => {
    const matchesSearch =
      inspection.template_key?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inspection.program_key?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inspection.inspector_name?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || inspection.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return { bg: '#dcfce7', text: '#166534' };
      case 'IN_PROGRESS':
        return { bg: '#fef9c3', text: '#854d0e' };
      case 'DRAFT':
        return { bg: '#f3f4f6', text: '#6b7280' };
      default:
        return { bg: '#f3f4f6', text: '#6b7280' };
    }
  };

  const getPassFailBadge = (passFailStatus: string | null) => {
    if (!passFailStatus) return null;

    return (
      <span
        className="px-2 py-1 text-xs font-medium rounded-full"
        style={{
          backgroundColor: passFailStatus === 'PASS' ? '#dcfce7' : '#fee2e2',
          color: passFailStatus === 'PASS' ? '#166534' : '#991b1b',
        }}
      >
        {passFailStatus}
      </span>
    );
  };

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
            Inspections
          </h1>
          <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
            View and manage inspection runs
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <input
          type="text"
          placeholder="Search by template, program, or inspector..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        >
          <option value="all">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="COMPLETED">Completed</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="font-medium" style={{ color: '#dc2626' }}>
            {error}
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <svg className="animate-spin h-8 w-8 mx-auto mb-3" style={{ color: '#7ed321' }} fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm" style={{ color: '#6b7280' }}>Loading inspections...</p>
        </div>
      )}

      {/* Inspections Table */}
      {!isLoading && !error && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="border-b" style={{ backgroundColor: '#f9fafb', borderColor: '#e5e7eb' }}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Template
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Asset Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Inspector
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Started
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Result
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: '#e5e7eb' }}>
              {filteredInspections.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: '#6b7280' }}>
                    {searchTerm || statusFilter !== 'all' ? 'No inspections match your filters' : 'No inspections yet.'}
                  </td>
                </tr>
              ) : (
                filteredInspections.map((inspection) => {
                  const statusColors = getStatusColor(inspection.status);
                  return (
                    <tr key={inspection.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <p className="text-sm font-medium" style={{ color: '#111827' }}>
                          {inspection.template_key}
                        </p>
                        {inspection.program_key && (
                          <p className="text-xs" style={{ color: '#6b7280' }}>
                            {inspection.program_key}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                        {inspection.asset_type}
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                        {inspection.inspector_name || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                        {new Date(inspection.started_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="px-2 py-1 text-xs font-medium rounded-full"
                          style={{
                            backgroundColor: statusColors.bg,
                            color: statusColors.text,
                          }}
                        >
                          {inspection.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {getPassFailBadge(inspection.pass_fail)}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => onViewInspection(inspection.id)}
                          className="text-sm font-medium hover:underline"
                          style={{ color: '#7ed321' }}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Count */}
      {!isLoading && !error && filteredInspections.length > 0 && (
        <div className="mt-4 text-sm" style={{ color: '#6b7280' }}>
          Showing {filteredInspections.length} of {inspections.length} inspections
        </div>
      )}
    </div>
  );
}
