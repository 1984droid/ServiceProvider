/**
 * VIN API Client
 *
 * API functions for VIN decoding via NHTSA vPIC
 */

import { apiClient } from '@/lib/axios';

export interface VINDecodeResult {
  vin: string;
  model_year: number | null;
  make: string;
  model: string;
  manufacturer: string;
  vehicle_type: string;
  body_class: string;
  engine_model: string;
  engine_configuration: string;
  engine_cylinders: number | null;
  displacement_liters: string | null;
  fuel_type_primary: string;
  fuel_type_secondary: string;
  gvwr: string;
  gvwr_min_lbs: number | null;
  gvwr_max_lbs: number | null;
  abs: string;
  airbag_locations: string;
  plant_city: string;
  plant_state: string;
  plant_country: string;
  error_code: string;
  error_text: string;
}

export const vinApi = {
  /**
   * Decode a VIN using NHTSA vPIC API
   */
  async decode(vin: string): Promise<VINDecodeResult> {
    const response = await apiClient.post<VINDecodeResult>('/vin/decode/', { vin });
    return response.data;
  },
};
