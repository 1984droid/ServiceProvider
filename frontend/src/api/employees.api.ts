/**
 * Employees API Client
 *
 * API functions for employee management and user access control.
 */

import { apiClient } from '@/lib/axios';

// Employee Types
export interface Employee {
  id: string;
  user: string | null;
  employee_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  base_department: string;
  base_department_name: string;
  floating_departments: string[];
  floating_department_names: string[];
  all_departments: Array<{
    id: string;
    name: string;
    code: string;
  }>;
  title: string;
  hire_date: string | null;
  termination_date: string | null;
  is_active: boolean;
  certifications: Array<{
    standard: string;
    cert_number: string;
    expiry: string;
    issued_by?: string;
    issued_date?: string;
  }>;
  skills: string[];
  settings: Record<string, any>;
  has_user_account: boolean;
  user_info: {
    id: string;
    username: string;
    is_active: boolean;
    last_login: string | null;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Employee[];
}

export interface CreateEmployeeRequest {
  employee_number: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  base_department: string;
  floating_departments?: string[];
  title?: string;
  hire_date?: string;
  certifications?: Array<{
    standard: string;
    cert_number: string;
    expiry: string;
    issued_by?: string;
    issued_date?: string;
  }>;
  skills?: string[];
}

export interface CreateUserResponse {
  message: string;
  username: string;
  employee_id: string;
  user_id: string;
  temporary_password?: string;
  password_note?: string;
}

export interface RevokeUserResponse {
  message: string;
  employee_id: string;
  note?: string;
}

export const employeesApi = {
  /**
   * List all employees with optional filtering
   */
  async list(params?: {
    is_active?: boolean;
    base_department?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<EmployeeListResponse> {
    const response = await apiClient.get<EmployeeListResponse>('/employees/', {
      params
    });
    return response.data;
  },

  /**
   * Get active employees only
   */
  async listActive(): Promise<Employee[]> {
    const response = await apiClient.get<Employee[]>('/employees/active/');
    return response.data;
  },

  /**
   * Get a single employee by ID
   */
  async get(id: string): Promise<Employee> {
    const response = await apiClient.get<Employee>(`/employees/${id}/`);
    return response.data;
  },

  /**
   * Create a new employee
   */
  async create(data: CreateEmployeeRequest): Promise<Employee> {
    const response = await apiClient.post<Employee>('/employees/', data);
    return response.data;
  },

  /**
   * Update an employee
   */
  async update(id: string, data: Partial<CreateEmployeeRequest>): Promise<Employee> {
    const response = await apiClient.patch<Employee>(`/employees/${id}/`, data);
    return response.data;
  },

  /**
   * Delete/deactivate an employee
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/employees/${id}/`);
  },

  /**
   * Create a user account for an employee (grant login access)
   */
  async createUser(employeeId: string, data?: {
    username?: string;
    password?: string;
  }): Promise<CreateUserResponse> {
    const response = await apiClient.post<CreateUserResponse>(
      `/employees/${employeeId}/create_user/`,
      data || {}
    );
    return response.data;
  },

  /**
   * Revoke user account access for an employee
   */
  async revokeUser(employeeId: string, deleteUser: boolean = false): Promise<RevokeUserResponse> {
    const response = await apiClient.post<RevokeUserResponse>(
      `/employees/${employeeId}/revoke_user/`,
      { delete_user: deleteUser }
    );
    return response.data;
  },
};
