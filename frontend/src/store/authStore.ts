import { create } from 'zustand';
import type { AuthStatus } from '../types/auth';
import * as authApi from '../api/auth';

interface AuthState {
  status: AuthStatus | null;
  loading: boolean;
  error: string | null;
  fetchStatus: () => Promise<void>;
  login: (code: string) => Promise<boolean>;
  saveManualToken: (token: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: null,
  loading: false,
  error: null,

  fetchStatus: async () => {
    set({ loading: true, error: null });
    try {
      const status = await authApi.getAuthStatus();
      set({ status, loading: false });
    } catch (e) {
      set({ loading: false, error: 'Failed to fetch auth status' });
    }
  },

  login: async (code: string) => {
    set({ loading: true, error: null });
    try {
      const result = await authApi.submitCallback(code);
      if (result.success) {
        const status = await authApi.getAuthStatus();
        set({ status, loading: false });
        return true;
      }
      set({ loading: false, error: result.message });
      return false;
    } catch (e) {
      set({ loading: false, error: 'Login failed' });
      return false;
    }
  },

  saveManualToken: async (token: string) => {
    set({ loading: true, error: null });
    try {
      const result = await authApi.submitManualToken(token);
      if (result.success) {
        const status = await authApi.getAuthStatus();
        set({ status, loading: false });
        return true;
      }
      set({ loading: false, error: result.message });
      return false;
    } catch (e) {
      set({ loading: false, error: 'Failed to save token' });
      return false;
    }
  },

  logout: async () => {
    await authApi.deleteToken();
    set({ status: { authenticated: false, expires_at: null, created_at: null, has_refresh_token: false, status: 'no_token' } });
  },
}));
