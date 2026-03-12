/**
 * Authentication Store
 *
 * Global state management for authentication using Zustand.
 */

import { create } from 'zustand';
import type { UserProfile } from '@/api/auth.api';

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: UserProfile | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) =>
    set({
      user,
      isAuthenticated: !!user,
      isLoading: false,
    }),

  setLoading: (loading) =>
    set({
      isLoading: loading,
    }),

  logout: () =>
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),

  hasPermission: (permission) => {
    const { user } = get();
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.permissions.includes(permission);
  },

  hasRole: (role) => {
    const { user } = get();
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.roles.includes(role);
  },

  hasAnyRole: (roles) => {
    const { user } = get();
    if (!user) return false;
    if (user.is_superuser) return true;
    return roles.some((role) => user.roles.includes(role));
  },
}));
