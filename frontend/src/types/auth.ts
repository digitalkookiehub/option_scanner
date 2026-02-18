export interface AuthStatus {
  authenticated: boolean;
  expires_at: string | null;
  created_at: string | null;
  has_refresh_token: boolean;
  status: string;
}

export interface TokenValidation {
  valid: boolean;
  profile: Record<string, unknown> | null;
  error: string | null;
}
