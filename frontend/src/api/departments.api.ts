/**
 * Departments API Client
 */

import { apiClient } from '@/lib/axios';

export interface Department {
  id: string;
  name: string;
  code: string;
  description: string;
  manager: string | null;
  manager_name: string | null;
  is_active: boolean;
  allows_floating: boolean;
  employee_count?: number;
  total_employee_count?: number;
  created_at: string;
  updated_at: string;
}

export const departmentsApi = {
  /**
   * List all departments
   */
  async list(params?: {
    is_active?: boolean;
    search?: string;
  }): Promise<Department[]> {
    const response = await apiClient.get<Department[]>('/departments/', {
      params
    });
    return response.data;
  },

  /**
   * Get a single department
   */
  async get(id: string): Promise<Department> {
    const response = await apiClient.get<Department>(`/departments/${id}/`);
    return response.data;
  },
};
