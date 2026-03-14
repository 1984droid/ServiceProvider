/**
 * Contacts API Client
 */

import { apiClient } from '@/lib/axios';

export interface Contact {
  id: string;
  customer: string;
  customer_name: string;
  full_name: string;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  phone: string;
  phone_extension: string;
  mobile: string;
  is_active: boolean;
  is_automated: boolean;
  is_primary: boolean;
  receive_invoices: boolean;
  receive_estimates: boolean;
  receive_service_updates: boolean;
  receive_inspection_reports: boolean;
  notes: string;
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

export interface CreateUserResponse {
  message: string;
  contact_id: string;
  username: string;
  temporary_password?: string;
  password_note?: string;
}

export interface RevokeUserResponse {
  message: string;
  contact_id: string;
}

export const contactsApi = {
  /**
   * Create user account for contact (customer portal access)
   */
  async createUser(contactId: string): Promise<CreateUserResponse> {
    const response = await apiClient.post<CreateUserResponse>(
      `/contacts/${contactId}/create_user/`,
      {}
    );
    return response.data;
  },

  /**
   * Revoke user account access for contact
   */
  async revokeUser(contactId: string, deleteUser: boolean = false): Promise<RevokeUserResponse> {
    const response = await apiClient.post<RevokeUserResponse>(
      `/contacts/${contactId}/revoke_user/`,
      { delete_user: deleteUser }
    );
    return response.data;
  },
};
