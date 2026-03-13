/**
 * Login Page
 *
 * Clean, professional login screen for 1920x1080 displays.
 */

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    login({ username, password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#f9fafb' }}>
      <div style={{ width: '420px' }}>
        {/* Logo */}
        <div className="text-center mb-12">
          <img
            src="/logo.png"
            alt="Advantage Fleet"
            className="mx-auto"
            style={{ height: '100px', width: 'auto' }}
          />
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-md" style={{ padding: '48px 40px' }}>
          {loginError && (
            <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
              <p className="text-sm font-medium" style={{ color: '#dc2626' }}>
                Invalid credentials
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-5">
              <label htmlFor="username" className="block text-sm font-semibold mb-2" style={{ color: '#111827' }}>
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border"
                style={{
                  borderColor: '#d1d5db',
                  fontSize: '15px',
                  outline: 'none'
                }}
                required
                autoComplete="username"
                autoFocus
              />
            </div>

            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-semibold mb-2" style={{ color: '#111827' }}>
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border"
                style={{
                  borderColor: '#d1d5db',
                  fontSize: '15px',
                  outline: 'none'
                }}
                required
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full py-3 rounded-lg font-semibold text-white transition-colors"
              style={{
                backgroundColor: isLoggingIn ? '#9ca3af' : '#7ed321',
                cursor: isLoggingIn ? 'not-allowed' : 'pointer',
                fontSize: '15px'
              }}
              onMouseEnter={(e) => {
                if (!isLoggingIn) {
                  e.currentTarget.style.backgroundColor = '#6bb51d';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoggingIn) {
                  e.currentTarget.style.backgroundColor = '#7ed321';
                }
              }}
            >
              {isLoggingIn ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo hint */}
          <div className="mt-8 pt-6 border-t text-center" style={{ borderColor: '#e5e7eb' }}>
            <p className="text-xs" style={{ color: '#9ca3af' }}>
              Demo: <span style={{ color: '#6b7280' }}>admin / admin</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
