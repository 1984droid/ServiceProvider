/**
 * Authentication API Client
 *
 * All authentication-related API calls.
 */

import { apiClient, tokenManager } from '@/lib/axios';
import { API_CONFIG } from '@/config/api';

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserProfile;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string | null;
  employee: {
    id: string;
    employee_number: string;
    full_name: string;
    base_department: {
      id: string;
      name: string;
      code: string;
    } | null;
  } | null;
  roles: string[];
  permissions: string[];
}

export interface RegisterRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  employee_id?: string;
  roles?: string[];
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

// API Functions
export const authApi = {
  /**
   * Login with username and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      API_CONFIG.endpoints.auth.login,
      credentials
    );

    // Store tokens
    const { access, refresh } = response.data;
    tokenManager.setTokens(access, refresh);

    return response.data;
  },

  /**
   * Logout - blacklist refresh token
   */
  async logout(): Promise<void> {
    const refreshToken = tokenManager.getRefreshToken();
    if (refreshToken) {
      try {
        await apiClient.post(API_CONFIG.endpoints.auth.logout, {
          refresh: refreshToken,
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }

    // Clear tokens regardless of API call success
    tokenManager.clearTokens();
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(
      API_CONFIG.endpoints.auth.me
    );
    return response.data;
  },

  /**
   * Update current user profile (limited fields)
   */
  async updateProfile(data: {
    first_name?: string;
    last_name?: string;
    email?: string;
  }): Promise<UserProfile> {
    const response = await apiClient.patch<UserProfile>(
      API_CONFIG.endpoints.auth.me,
      data
    );
    return response.data;
  },

  /**
   * Change password
   */
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await apiClient.post(API_CONFIG.endpoints.auth.changePassword, data);
  },

  /**
   * Register new user (admin only)
   */
  async register(data: RegisterRequest): Promise<UserProfile> {
    const response = await apiClient.post<UserProfile>(
      API_CONFIG.endpoints.auth.register,
      data
    );
    return response.data;
  },

  /**
   * Get all users (admin only)
   */
  async getUsers(): Promise<UserProfile[]> {
    const response = await apiClient.get<UserProfile[]>(
      API_CONFIG.endpoints.auth.users
    );
    return response.data;
  },

  /**
   * Get user by ID (admin only)
   */
  async getUserById(id: number): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>(
      `${API_CONFIG.endpoints.auth.users}${id}/`
    );
    return response.data;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!tokenManager.getAccessToken();
  },
};
