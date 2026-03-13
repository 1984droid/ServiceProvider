/**
 * Assets API Client
 *
 * API functions for vehicle and equipment management.
 */

import { apiClient } from '@/lib/axios';

export interface VINDecodeData {
  id: string;
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
  decoded_at: string;
  created_at: string;
  updated_at: string;
}

export interface Vehicle {
  id: string;
  customer: string;
  vin: string;
  unit_number: string;
  license_plate: string;
  year: number | null;
  make: string;
  model: string;
  body_type: string;
  is_active: boolean;
  odometer_miles: number | null;
  engine_hours: number | null;
  capabilities: string[];
  photo: string | null;
  notes: string;
  vin_decode_data?: VINDecodeData | null;
  created_at: string;
  updated_at: string;
}

export interface Equipment {
  id: string;
  customer: string;
  serial_number: string;
  asset_number: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  year: number | null;
  is_active: boolean;
  engine_hours: number | null;
  cycles: number | null;
  mounted_on_vehicle: string | null;
  capabilities: string[];
  equipment_data: Record<string, any>;
  photo: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

export const vehiclesApi = {
  async list(): Promise<Vehicle[]> {
    const response = await apiClient.get<{ results: Vehicle[] }>('/vehicles/');
    return response.data.results;
  },

  async get(id: string): Promise<Vehicle> {
    const response = await apiClient.get<Vehicle>(`/vehicles/${id}/`);
    return response.data;
  },
};

export const equipmentApi = {
  async list(): Promise<Equipment[]> {
    const response = await apiClient.get<{ results: Equipment[] }>('/equipment/');
    return response.data.results;
  },

  async get(id: string): Promise<Equipment> {
    const response = await apiClient.get<Equipment>(`/equipment/${id}/`);
    return response.data;
  },
};
