import client from './client';
import type { AuthStatus, TokenValidation } from '../types/auth';

export const getAuthStatus = () =>
  client.get<AuthStatus>('/auth/status').then(r => r.data);

export const getLoginUrl = () =>
  client.get<{ url: string; error?: string }>('/auth/login-url').then(r => r.data);

export const submitCallback = (code: string) =>
  client.post('/auth/callback', { code }).then(r => r.data);

export const submitManualToken = (access_token: string, refresh_token?: string, expires_in?: number) =>
  client.post('/auth/manual-token', { access_token, refresh_token, expires_in }).then(r => r.data);

export const refreshToken = () =>
  client.post('/auth/refresh').then(r => r.data);

export const validateToken = () =>
  client.post<TokenValidation>('/auth/validate').then(r => r.data);

export const deleteToken = () =>
  client.delete('/auth/token').then(r => r.data);
