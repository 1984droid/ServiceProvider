/**
 * USDOT Profile API Client
 *
 * API functions for USDOT profile lookup and management.
 */

import { apiClient } from '@/lib/axios';

export interface USDOTProfile {
  id: string;
  customer?: string | null;
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

export const usdotApi = {
  /**
   * Lookup USDOT profile by USDOT number
   * Checks DB first, then calls FMCSA API if not found
   */
  async lookupByUSDOT(usdot: string, forceRefresh: boolean = false, customerId?: string): Promise<USDOTProfile> {
    const params: any = { usdot, force_refresh: forceRefresh };
    if (customerId) {
      params.customer_id = customerId;
    }
    const response = await apiClient.get<USDOTProfile>(
      `/usdot-profiles/lookup_by_usdot/`,
      { params }
    );
    return response.data;
  },

  /**
   * Lookup USDOT profile by MC number
   */
  async lookupByMC(mc: string): Promise<USDOTProfile> {
    // API should support MC lookup too
    const response = await apiClient.get<USDOTProfile>(
      `/usdot-profiles/lookup_by_mc/`,
      { params: { mc } }
    );
    return response.data;
  },

  /**
   * Get USDOT profile by ID
   */
  async get(id: string): Promise<USDOTProfile> {
    const response = await apiClient.get<USDOTProfile>(`/usdot-profiles/${id}/`);
    return response.data;
  },

  /**
   * List all USDOT profiles
   */
  async list(): Promise<USDOTProfile[]> {
    const response = await apiClient.get<USDOTProfile[]>('/usdot-profiles/');
    return response.data;
  },
};
