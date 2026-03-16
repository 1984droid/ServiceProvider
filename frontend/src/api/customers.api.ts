/**
 * Customer API Client
 *
 * API functions for customer management.
 */

import { apiClient } from '@/lib/axios';

export type Contact = {
  id: string;
  customer: string;
  first_name: string;
  last_name: string;
  full_name: string;
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
  created_at: string;
  updated_at: string;
}

export type USDOTProfile = {
  id: string;
  customer: string | null;
  usdot_number: string;
  mc_number: string;
  legal_name: string;
  dba_name: string;
  entity_type: string;
  physical_address: string;
  physical_city: string;
  physical_state: string;
  physical_zip: string;
  mailing_address: string;
  mailing_city: string;
  mailing_state: string;
  mailing_zip: string;
  phone: string;
  email: string;
  carrier_operation: string;
  cargo_carried: string;
  operation_classification: string[];
  safety_rating: string;
  out_of_service_date: string | null;
  total_power_units: number | null;
  total_drivers: number | null;
  raw_fmcsa_data: any;
  lookup_date: string;
  created_at: string;
  updated_at: string;
}

export type Customer = {
  id: string;
  name: string;
  legal_name: string;
  primary_contact?: string | null;
  is_active: boolean;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  usdot_number: string;
  mc_number: string;
  email?: string;
  phone?: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type CustomerDetail = Customer & {
  primary_contact_name: string | null;
  contacts: Contact[];
  usdot_profile: USDOTProfile | null;
};

export type CustomerCreateData = {
  name: string;
  legal_name?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  usdot_number?: string;
  mc_number?: string;
  notes?: string;
};

export type DuplicateCheckRequest = {
  name: string;
  legal_name?: string;
  usdot_number?: string;
  mc_number?: string;
  city?: string;
  state?: string;
  exclude_customer_id?: string;
};

export type MatchDetails = {
  total_score: number;
  base_score: number;
  name_similarity: number;
  legal_name_similarity: number;
  regulatory_match: boolean;
  usdot_match: boolean;
  mc_match: boolean;
  address_score: number;
  city_similarity: number;
  state_match: boolean;
  popularity_multiplier: number;
  selection_count: number;
};

export type DuplicateMatch = {
  customer: Customer;
  score: number;
  confidence: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';
  match_details: MatchDetails;
};

export type DuplicateCheckResponse = {
  found_duplicates: boolean;
  count: number;
  matches: DuplicateMatch[];
};

export const customersApi = {
  /**
   * Create a new customer
   */
  async create(data: CustomerCreateData): Promise<Customer> {
    const response = await apiClient.post<Customer>('/customers/', data);
    return response.data;
  },

  /**
   * List all customers
   */
  async list(): Promise<Customer[]> {
    const response = await apiClient.get<{ results: Customer[] }>('/customers/');
    return response.data.results;
  },

  /**
   * Get customer by ID
   */
  async get(id: string): Promise<Customer> {
    const response = await apiClient.get<Customer>(`/customers/${id}/`);
    return response.data;
  },

  /**
   * Get customer detail with contacts, assets, and USDOT data
   */
  async getDetail(id: string): Promise<CustomerDetail> {
    const response = await apiClient.get<CustomerDetail>(`/customers/${id}/`);
    return response.data;
  },

  /**
   * Update customer
   */
  async update(id: string, data: Partial<CustomerCreateData>): Promise<Customer> {
    const response = await apiClient.patch<Customer>(`/customers/${id}/`, data);
    return response.data;
  },

  /**
   * Delete customer
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/customers/${id}/`);
  },

  /**
   * Get contact by ID
   */
  async getContact(id: string): Promise<Contact> {
    const response = await apiClient.get<Contact>(`/contacts/${id}/`);
    return response.data;
  },

  /**
   * Update contact
   */
  async updateContact(id: string, data: Partial<Contact>): Promise<Contact> {
    const response = await apiClient.patch<Contact>(`/contacts/${id}/`, data);
    return response.data;
  },

  /**
   * Delete contact
   */
  async deleteContact(id: string): Promise<void> {
    await apiClient.delete(`/contacts/${id}/`);
  },

  /**
   * Check for duplicate customers
   */
  async checkDuplicates(data: DuplicateCheckRequest): Promise<DuplicateCheckResponse> {
    const response = await apiClient.post<DuplicateCheckResponse>('/customers/check_duplicates/', data);
    return response.data;
  },

  /**
   * Increment selection count for popularity tracking
   */
  async incrementSelection(id: string): Promise<Customer> {
    const response = await apiClient.post<Customer>(`/customers/${id}/increment_selection/`);
    return response.data;
  },
};
