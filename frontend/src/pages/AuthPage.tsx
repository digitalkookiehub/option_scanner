import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import * as authApi from '../api/auth';
import PageLayout from '../components/layout/PageLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function AuthPage() {
  const { status, loading, error, fetchStatus, saveManualToken, login, logout } = useAuthStore();
  const [manualToken, setManualToken] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [loginUrl, setLoginUrl] = useState<string | null>(null);
  const [loginUrlError, setLoginUrlError] = useState<string | null>(null);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{ valid: boolean; error?: string | null } | null>(null);

  useEffect(() => {
    fetchStatus();
    authApi.getLoginUrl().then((data) => {
      setLoginUrl(data.url || null);
      setLoginUrlError(data.error || null);
    }).catch(() => {});
  }, [fetchStatus]);

  const handleValidate = async () => {
    setValidating(true);
    try {
      const result = await authApi.validateToken();
      setValidationResult(result);
    } catch {
      setValidationResult({ valid: false, error: 'Validation request failed' });
    }
    setValidating(false);
  };

  return (
    <PageLayout>
      <div className="mx-auto w-full max-w-2xl space-y-6 p-6">
        <h2 className="text-2xl font-bold text-gray-900">Authentication & Token Management</h2>

        {/* Status Card */}
        <div className={`rounded-lg border p-4 ${status?.authenticated ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`}>
          <h3 className="font-semibold">{status?.authenticated ? 'Authenticated' : 'Not Authenticated'}</h3>
          {status?.authenticated && (
            <div className="mt-2 space-y-1 text-sm text-gray-700">
              <p>Status: {status.status}</p>
              {status.expires_at && <p>Expires: {status.expires_at}</p>}
              {status.created_at && <p>Created: {status.created_at}</p>}
              <p>Has Refresh Token: {status.has_refresh_token ? 'Yes' : 'No'}</p>
            </div>
          )}
        </div>

        {/* OAuth Login */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 font-semibold">OAuth2 Login</h3>
          {loginUrl ? (
            <a
              href={loginUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
            >
              Login with Upstox
            </a>
          ) : (
            <p className="rounded border border-yellow-300 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
              {loginUrlError || 'Configure UPSTOX_API_KEY and UPSTOX_REDIRECT_URL in backend/.env to enable OAuth login.'}
            </p>
          )}
          <div className="mt-3">
            <label className="block text-sm text-gray-600">Auth Code (from redirect URL):</label>
            <div className="mt-1 flex gap-2">
              <input
                type="text"
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                placeholder="Paste auth code here"
                className="flex-1 rounded border px-3 py-1.5 text-sm"
              />
              <button
                onClick={() => login(authCode)}
                disabled={!authCode || loading}
                className="rounded bg-green-600 px-4 py-1.5 text-sm text-white hover:bg-green-700 disabled:opacity-50"
              >
                Exchange
              </button>
            </div>
          </div>
        </div>

        {/* Manual Token */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 font-semibold">Manual Token Entry</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={manualToken}
              onChange={(e) => setManualToken(e.target.value)}
              placeholder="Paste access token"
              className="flex-1 rounded border px-3 py-1.5 text-sm"
            />
            <button
              onClick={() => saveManualToken(manualToken)}
              disabled={!manualToken || loading}
              className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Save Token
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleValidate}
            disabled={validating || !status?.authenticated}
            className="rounded bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {validating ? 'Validating...' : 'Validate Token'}
          </button>
          <button
            onClick={() => fetchStatus()}
            disabled={loading}
            className="rounded bg-gray-600 px-4 py-2 text-sm text-white hover:bg-gray-700 disabled:opacity-50"
          >
            Refresh Status
          </button>
          <button
            onClick={logout}
            disabled={!status?.authenticated}
            className="rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
          >
            Clear Token
          </button>
        </div>

        {/* Validation Result */}
        {validationResult && (
          <div className={`rounded-lg border p-4 ${validationResult.valid ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`}>
            <p className="font-medium">{validationResult.valid ? 'Token is valid' : 'Token is invalid'}</p>
            {validationResult.error && <p className="mt-1 text-sm text-red-600">{validationResult.error}</p>}
          </div>
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}
        {loading && <LoadingSpinner />}
      </div>
    </PageLayout>
  );
}
