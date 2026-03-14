/**
 * Authentication Hook
 *
 * Custom hook for authentication operations using TanStack Query.
 *
 * NOTE: This app uses custom state-based navigation, not React Router.
 * Navigation callbacks are handled by the caller, not by this hook.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/api/auth.api';
import type { LoginRequest, ChangePasswordRequest, RegisterRequest } from '@/api/auth.api';
import { useAuthStore } from '@/store/authStore';

export const AUTH_QUERY_KEYS = {
  currentUser: ['auth', 'currentUser'] as const,
  users: ['auth', 'users'] as const,
  user: (id: number) => ['auth', 'user', id] as const,
};

export function useAuth() {
  const queryClient = useQueryClient();
  const { user, isAuthenticated, setUser, setLoading, logout: clearAuthState } = useAuthStore();

  // Query: Get current user
  const { data: currentUser, isLoading } = useQuery({
    queryKey: AUTH_QUERY_KEYS.currentUser,
    queryFn: authApi.getCurrentUser,
    enabled: authApi.isAuthenticated(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
  });

  // Sync query data with auth store
  if (currentUser && currentUser !== user) {
    setUser(currentUser);
  } else if (!currentUser && isAuthenticated) {
    setLoading(false);
  }

  // Mutation: Login
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data) => {
      setUser(data.user);
      queryClient.setQueryData(AUTH_QUERY_KEYS.currentUser, data.user);
      // Navigation handled by caller (App.tsx watches isAuthenticated state)
    },
  });

  // Mutation: Logout
  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      clearAuthState();
      queryClient.clear();
      // Navigation handled by caller (App.tsx watches isAuthenticated state)
    },
  });

  // Mutation: Change Password
  const changePasswordMutation = useMutation({
    mutationFn: (data: ChangePasswordRequest) => authApi.changePassword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEYS.currentUser });
    },
  });

  // Mutation: Update Profile
  const updateProfileMutation = useMutation({
    mutationFn: (data: { first_name?: string; last_name?: string; email?: string }) =>
      authApi.updateProfile(data),
    onSuccess: (data) => {
      setUser(data);
      queryClient.setQueryData(AUTH_QUERY_KEYS.currentUser, data);
    },
  });

  // Mutation: Register User (admin only)
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEYS.users });
    },
  });

  return {
    // State
    user,
    isAuthenticated,
    isLoading: isLoading || useAuthStore.getState().isLoading,

    // Mutations
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,

    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,

    changePassword: changePasswordMutation.mutate,
    changePasswordAsync: changePasswordMutation.mutateAsync,
    isChangingPassword: changePasswordMutation.isPending,
    changePasswordError: changePasswordMutation.error,

    updateProfile: updateProfileMutation.mutate,
    updateProfileAsync: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
    updateProfileError: updateProfileMutation.error,

    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,

    // Helpers
    hasPermission: useAuthStore.getState().hasPermission,
    hasRole: useAuthStore.getState().hasRole,
    hasAnyRole: useAuthStore.getState().hasAnyRole,
  };
}
