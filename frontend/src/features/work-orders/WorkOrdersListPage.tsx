/**
 * WorkOrdersListPage
 *
 * List view of all work orders with filtering and search
 * Displays work order summary cards with status, priority, and quick actions
 */

import { useState, useEffect } from 'react';
import { workOrdersApi, type WorkOrder } from '@/api/workOrders.api';

interface WorkOrdersListPageProps {
  onNavigateToDetail?: (workOrderId: string) => void;
  onNavigateToCreate?: () => void;
}

export function WorkOrdersListPage({ onNavigateToDetail, onNavigateToCreate }: WorkOrdersListPageProps) {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadWorkOrders();
  }, [statusFilter, priorityFilter, searchQuery]);

  const loadWorkOrders = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (searchQuery) params.search = searchQuery;

      const data = await workOrdersApi.list(params);
      setWorkOrders(data.results || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load work orders');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'ON_HOLD':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'EMERGENCY':
        return 'bg-red-100 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'NORMAL':
        return 'bg-blue-100 text-blue-800';
      case 'LOW':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading work orders...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadWorkOrders}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Work Orders</h1>
              <p className="text-sm text-gray-600 mt-1">
                Manage service work orders and track progress
              </p>
            </div>
            {onNavigateToCreate && (
              <button
                onClick={onNavigateToCreate}
                data-testid="create-work-order-btn"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Work Order
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="bg-white rounded-lg shadow p-4 space-y-4">
          {/* Search */}
          <div>
            <label htmlFor="work-order-search" className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              id="work-order-search"
              type="text"
              placeholder="Search by work order number, title, or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              data-testid="work-order-search"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Filters Row */}
          <div className="flex gap-4">
            {/* Status Filter */}
            <div className="flex-1">
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                id="status-filter"
                value={statusFilter || ''}
                onChange={(e) => setStatusFilter(e.target.value || null)}
                data-testid="status-filter"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="DRAFT">Draft</option>
                <option value="PENDING">Pending</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="ON_HOLD">On Hold</option>
                <option value="COMPLETED">Completed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div className="flex-1">
              <label htmlFor="priority-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                id="priority-filter"
                value={priorityFilter || ''}
                onChange={(e) => setPriorityFilter(e.target.value || null)}
                data-testid="priority-filter"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Priorities</option>
                <option value="LOW">Low</option>
                <option value="NORMAL">Normal</option>
                <option value="HIGH">High</option>
                <option value="EMERGENCY">Emergency</option>
              </select>
            </div>

            {/* Clear Filters */}
            {(statusFilter || priorityFilter || searchQuery) && (
              <div className="flex items-end">
                <button
                  onClick={() => {
                    setStatusFilter(null);
                    setPriorityFilter(null);
                    setSearchQuery('');
                  }}
                  className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Clear All
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Work Orders List */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        {workOrders.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <p className="text-gray-600 font-medium">No work orders found</p>
            <p className="text-sm text-gray-500 mt-1">
              {statusFilter || priorityFilter
                ? 'Try adjusting your filters'
                : 'Work orders will appear here when created'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {workOrders.map((wo) => (
              <div
                key={wo.id}
                onClick={() => onNavigateToDetail?.(wo.id)}
                data-testid="work-order-card"
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 hover:border-blue-300"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {wo.work_order_number}
                        </h3>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(
                            wo.status
                          )}`}
                        >
                          {wo.status.replace('_', ' ')}
                        </span>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(
                            wo.priority
                          )}`}
                        >
                          {wo.priority}
                        </span>
                      </div>
                      <p className="text-base text-gray-900 font-medium">
                        {wo.title || wo.description.substring(0, 100)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Asset Type:</span>
                      <span className="ml-2 text-gray-900 font-medium">
                        {wo.asset_type}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Source:</span>
                      <span className="ml-2 text-gray-900 font-medium">
                        {wo.source_type.replace('_', ' ')}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Created:</span>
                      <span className="ml-2 text-gray-900 font-medium">
                        {new Date(wo.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
