/**
 * WorkOrderDetailPage
 *
 * Detailed view of a single work order
 * Shows all work order information, lines, linked defects, and actions
 */

import { useState, useEffect } from 'react';
import { workOrdersApi, type WorkOrder } from '@/api/workOrders.api';

interface WorkOrderDetailPageProps {
  workOrderId: string;
  onBack: () => void;
}

export function WorkOrderDetailPage({
  workOrderId,
  onBack,
}: WorkOrderDetailPageProps) {
  const [workOrder, setWorkOrder] = useState<WorkOrder | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWorkOrder();
  }, [workOrderId]);

  const loadWorkOrder = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await workOrdersApi.get(workOrderId);
      setWorkOrder(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load work order');
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
          <p className="mt-4 text-gray-600">Loading work order...</p>
        </div>
      </div>
    );
  }

  if (error || !workOrder) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Work order not found'}</p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Back to List
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
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={onBack}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {workOrder.work_order_number}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Work Order Details
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 text-sm font-medium rounded border ${getStatusColor(
                workOrder.status
              )}`}
            >
              {workOrder.status.replace('_', ' ')}
            </span>
            <span
              className={`px-3 py-1 text-sm font-medium rounded ${getPriorityColor(
                workOrder.priority
              )}`}
            >
              {workOrder.priority} Priority
            </span>
            <span className="px-3 py-1 text-sm bg-gray-100 text-gray-800 rounded">
              {workOrder.asset_type}
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {workOrder.title || 'Work Order Description'}
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">
                {workOrder.description}
              </p>
            </div>

            {/* Work Order Lines - placeholder for now */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Work Items
              </h2>
              <p className="text-sm text-gray-500">
                Work order line items will be displayed here
              </p>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-gray-500">Source Type</div>
                  <div className="text-gray-900 font-medium">
                    {workOrder.source_type.replace('_', ' ')}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Approval Status</div>
                  <div className="text-gray-900 font-medium">
                    {workOrder.approval_status.replace('_', ' ')}
                  </div>
                </div>
                {workOrder.scheduled_date && (
                  <div>
                    <div className="text-gray-500">Scheduled Date</div>
                    <div className="text-gray-900 font-medium">
                      {new Date(workOrder.scheduled_date).toLocaleDateString()}
                    </div>
                  </div>
                )}
                {workOrder.due_date && (
                  <div>
                    <div className="text-gray-500">Due Date</div>
                    <div className="text-gray-900 font-medium">
                      {new Date(workOrder.due_date).toLocaleDateString()}
                    </div>
                  </div>
                )}
                <div>
                  <div className="text-gray-500">Created</div>
                  <div className="text-gray-900 font-medium">
                    {new Date(workOrder.created_at).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Last Updated</div>
                  <div className="text-gray-900 font-medium">
                    {new Date(workOrder.updated_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Actions</h3>
              <div className="space-y-2">
                {workOrder.status === 'PENDING' && (
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
                    Start Work Order
                  </button>
                )}
                {workOrder.status === 'IN_PROGRESS' && (
                  <button className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium">
                    Complete Work Order
                  </button>
                )}
                {workOrder.approval_status === 'DRAFT' && (
                  <button className="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm font-medium">
                    Request Approval
                  </button>
                )}
                <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium">
                  Edit Work Order
                </button>
                <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium">
                  Print Work Order
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
