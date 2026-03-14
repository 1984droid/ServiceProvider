/**
 * Inspections API Client
 *
 * API functions for inspection templates and inspection run management.
 */

import { apiClient } from '@/lib/axios';

// Inspection Template Types
export interface InspectionTemplate {
  template_key: string;
  name: string;
  status: 'DRAFT' | 'PUBLISHED' | 'DEPRECATED';
  standard_code?: string;
  standard_revision?: string;
  inspection_kind?: string;
  domain?: string;
  tags?: string[];
  step_count?: number;
  rule_count?: number;
  required_capabilities?: string[] | null;

  // Legacy fields for backwards compatibility
  key?: string;
  version?: string;
  description?: string;
  equipment_types?: string[];
  vehicle_types?: string[];
  published?: boolean;
  standard_reference?: string;
}

export interface TemplateListResponse {
  count: number;
  templates: InspectionTemplate[];
}

// Inspection Run Types
export interface InspectionRun {
  id: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  asset_info?: {
    type: string;
    id: string;
    vin?: string;
    unit_number?: string;
    serial_number?: string;
    asset_number?: string;
    year?: number;
    make?: string;
    model?: string;
    manufacturer?: string;
    equipment_type?: string;
  };
  customer: string;
  template_key: string;
  program_key?: string;
  status: 'DRAFT' | 'IN_PROGRESS' | 'COMPLETED';
  started_at: string;
  finalized_at?: string | null;
  inspector_name?: string;
  inspector_signature?: string;
  defect_count?: number;
  critical_defect_count?: number;
  completion_status?: {
    total_steps: number;
    completed_steps: number;
    required_steps: number;
    completed_required_steps: number;
    percent_complete: number;
    is_ready_to_finalize: boolean;
  };
  pass_fail?: 'PASS' | 'FAIL' | null;
  created_at: string;
  updated_at: string;
}

export interface CreateInspectionRequest {
  template_key: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  inspector_name?: string;
}

export const inspectionsApi = {
  // ===== Templates =====

  /**
   * List all available inspection templates
   */
  async listTemplates(): Promise<TemplateListResponse> {
    const response = await apiClient.get<TemplateListResponse>('/templates/');
    return response.data;
  },

  /**
   * Get a specific template by key
   */
  async getTemplate(key: string): Promise<any> {
    const response = await apiClient.get(`/templates/${key}/`);
    return response.data;
  },

  /**
   * Get templates for a specific equipment type
   */
  async getTemplatesForEquipment(equipmentType: string): Promise<TemplateListResponse> {
    const response = await apiClient.get<TemplateListResponse>('/templates/for_equipment/', {
      params: { equipment_type: equipmentType }
    });
    return response.data;
  },

  /**
   * Get templates applicable to a specific asset (uses standards-based filtering)
   */
  async getTemplatesForAsset(assetType: 'vehicle' | 'equipment', assetId: string): Promise<TemplateListResponse> {
    const response = await apiClient.get<TemplateListResponse>('/templates/for_asset/', {
      params: {
        asset_type: assetType.toLowerCase(),
        asset_id: assetId
      }
    });
    return response.data;
  },

  // ===== Inspection Runs =====

  /**
   * List all inspection runs
   */
  async list(params?: {
    customer?: string;
    asset_type?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ count: number; results: InspectionRun[] }> {
    const response = await apiClient.get<{ count: number; results: InspectionRun[] }>('/inspections/', { params });
    return response.data;
  },

  /**
   * Get a specific inspection run
   */
  async get(id: string): Promise<InspectionRun> {
    const response = await apiClient.get<InspectionRun>(`/inspections/${id}/`);
    return response.data;
  },

  /**
   * Create a new inspection run
   */
  async create(data: CreateInspectionRequest): Promise<InspectionRun> {
    const response = await apiClient.post<InspectionRun>('/inspections/', data);
    return response.data;
  },

  /**
   * Delete an inspection run (DRAFT only)
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/inspections/${id}/`);
  },

  /**
   * Get inspection review data (read-only view with defects)
   */
  async getReview(id: string): Promise<{
    inspection: InspectionRun & { template_snapshot: any; step_responses: any };
    completion: any;
    defects: {
      count: number;
      items: any[];
      summary: any;
    };
  }> {
    const response = await apiClient.get(`/inspections/${id}/review/`);
    return response.data;
  },

  /**
   * Finalize an inspection (make immutable)
   */
  async finalize(id: string, signatureData?: string | null): Promise<{ message: string; inspection: InspectionRun }> {
    const response = await apiClient.post(`/inspections/${id}/finalize/`, {
      signature_data: signatureData,
      force: false,
    });
    return response.data;
  },
};
