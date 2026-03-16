/**
 * Vocabulary API Client
 *
 * API functions for work order vocabulary management.
 */

import { apiClient } from '@/lib/axios';

export interface Vocabulary {
  verbs: string[];
  nouns: {
    category: string;
    items: string[];
  }[];
  service_locations: string[];
}

export interface VocabularySuggestion {
  verb?: string;
  noun?: string;
  service_location?: string;
  confidence?: number;
}

export const vocabularyApi = {
  /**
   * Get all vocabulary
   */
  async getAll(): Promise<Vocabulary> {
    const response = await apiClient.get('/vocabulary/');
    return response.data;
  },

  /**
   * Get all verbs
   */
  async getVerbs(): Promise<{ verbs: string[] }> {
    const response = await apiClient.get('/vocabulary/verbs/');
    return response.data;
  },

  /**
   * Get all nouns, optionally filtered by category
   */
  async getNouns(category?: string): Promise<{ nouns: string[] }> {
    const params = category ? { category } : {};
    const response = await apiClient.get('/vocabulary/nouns/', { params });
    return response.data;
  },

  /**
   * Get all service locations
   */
  async getServiceLocations(): Promise<{ service_locations: string[] }> {
    const response = await apiClient.get('/vocabulary/service_locations/');
    return response.data;
  },

  /**
   * Get vocabulary suggestions from description
   */
  async suggest(description: string): Promise<VocabularySuggestion> {
    const response = await apiClient.post('/vocabulary/suggest/', {
      description,
    });
    return response.data;
  },
};
