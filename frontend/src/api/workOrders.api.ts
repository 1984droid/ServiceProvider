/**
 * Work Orders API Client
 *
 * API methods for work order management
 */

import { apiClient } from '@/lib/axios';

export interface WorkOrderLine {
  id: string;
  line_number: number;
  verb: string;
  noun: string;
  service_location?: string;
  description?: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  estimated_hours?: number;
  actual_hours?: number;
  assigned_to?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkOrder {
  id: string;
  work_order_number: string;
  customer: string;
  customer_name?: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  status: 'DRAFT' | 'PENDING' | 'IN_PROGRESS' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY';
  source_type: 'INSPECTION_DEFECT' | 'MAINTENANCE_SCHEDULE' | 'CUSTOMER_REQUEST' | 'BREAKDOWN' | 'MANUAL';
  source_id?: string;
  title: string;
  description: string;
  department?: string;
  assigned_to?: string;
  scheduled_date?: string;
  due_date?: string;
  approval_status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED';
  lines?: WorkOrderLine[];
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  customer: string;
  display_name: string;
  is_active: boolean;
}

export interface CreateWorkOrderData {
  customer: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY';
  source_type: 'INSPECTION_DEFECT' | 'MAINTENANCE_SCHEDULE' | 'CUSTOMER_REQUEST' | 'BREAKDOWN' | 'MANUAL';
  source_id?: string;
  department?: string;
  scheduled_date?: string;
  due_date?: string;
  lines: Array<{
    verb: string;
    noun: string;
    service_location?: string;
    description?: string;
    estimated_hours?: number;
  }>;
}

export const workOrdersApi = {
  /**
   * List all work orders with optional filters
   */
  async list(params?: {
    status?: string;
    priority?: string;
    customer?: string;
    asset_type?: string;
    search?: string;
  }): Promise<{ results: WorkOrder[]; count: number }> {
    const response = await apiClient.get('/work-orders/', { params });
    return response.data;
  },

  /**
   * Get single work order by ID
   */
  async get(id: string): Promise<WorkOrder> {
    const response = await apiClient.get(`/work-orders/${id}/`);
    return response.data;
  },

  /**
   * Create a new work order
   */
  async create(data: CreateWorkOrderData): Promise<WorkOrder> {
    const response = await apiClient.post('/work-orders/', data);
    return response.data;
  },

  /**
   * Get available assets for a customer by asset type
   */
  async getAvailableAssets(customerId: string, assetType: 'VEHICLE' | 'EQUIPMENT'): Promise<{ count: number; assets: Asset[] }> {
    const response = await apiClient.get('/work-orders/available_assets/', {
      params: { customer: customerId, asset_type: assetType }
    });
    return response.data;
  },

  /**
   * Create work order from inspection defects
   */
  async createFromInspection(data: {
    inspection_id: string;
    defect_ids?: string[];
    group_by_location?: boolean;
    min_severity?: 'ADVISORY' | 'MINOR' | 'MAJOR' | 'CRITICAL';
    department_id?: string;
    auto_approve?: boolean;
  }): Promise<{ count: number; work_orders: WorkOrder[] }> {
    const response = await apiClient.post('/work-orders/from_inspection/', data);
    return response.data;
  },

  /**
   * Create work order from single defect
   */
  async createFromDefect(data: {
    defect_id: string;
    department_id?: string;
    auto_approve?: boolean;
  }): Promise<WorkOrder> {
    const response = await apiClient.post('/work-orders/from_defect/', data);
    return response.data;
  },

  /**
   * Request approval for work order
   */
  async requestApproval(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/request_approval/`);
    return response.data;
  },

  /**
   * Approve work order
   */
  async approve(id: string, approved_by: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/approve/`, {
      approved_by,
    });
    return response.data;
  },

  /**
   * Reject work order
   */
  async reject(id: string, rejected_reason?: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/reject/`, {
      rejected_reason,
    });
    return response.data;
  },

  /**
   * Start work order
   */
  async start(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/start/`);
    return response.data;
  },

  /**
   * Complete work order
   */
  async complete(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/complete/`);
    return response.data;
  },
};
