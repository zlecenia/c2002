import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { apiService } from '../services/api';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useScanner, setUseScanner] = useState(true);
  
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await apiService.login(username, password);
      login(response.user, response.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 to-dark-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">CONNECT 500</h1>
          <p className="text-gray-400">MASKTRONIC</p>
          <p className="text-primary-400 mt-4">Connect++ Operator Login</p>
        </div>

        {/* Login Card */}
        <div className="bg-dark-700 rounded-lg shadow-xl p-8">
          <div className="mb-6">
            <div className="flex space-x-2 mb-4">
              <button
                onClick={() => setUseScanner(true)}
                className={`flex-1 py-2 px-4 rounded ${
                  useScanner
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-600 text-gray-400'
                }`}
              >
                QR/Barcode
              </button>
              <button
                onClick={() => setUseScanner(false)}
                className={`flex-1 py-2 px-4 rounded ${
                  !useScanner
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-600 text-gray-400'
                }`}
              >
                Keyboard
              </button>
            </div>
          </div>

          {useScanner ? (
            // Scanner Mode
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📷</div>
              <p className="text-gray-300 mb-4">Scan your QR code or Barcode</p>
              <p className="text-sm text-gray-500">
                Connect USB scanner and scan your operator ID
              </p>
              <div className="mt-8">
                <input
                  type="text"
                  placeholder="Scan here..."
                  className="w-full p-3 bg-dark-800 border border-dark-600 rounded text-white text-center"
                  autoFocus
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      // Simulate scan
                      setUsername('operator');
                      setPassword('demo');
                      handleLogin(e as any);
                    }
                  }}
                />
              </div>
            </div>
          ) : (
            // Keyboard Mode
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label className="block text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full p-3 bg-dark-800 border border-dark-600 rounded text-white focus:border-primary-500 focus:outline-none"
                  placeholder="Enter username"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full p-3 bg-dark-800 border border-dark-600 rounded text-white focus:border-primary-500 focus:outline-none"
                  placeholder="Enter password"
                  required
                />
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded text-red-200 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded transition disabled:opacity-50"
              >
                {isLoading ? 'Logging in...' : 'Login'}
              </button>
            </form>
          )}

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-dark-600">
            <p className="text-xs text-gray-500 text-center">
              Demo: Press Enter in scan field or use "operator" / "demo"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
