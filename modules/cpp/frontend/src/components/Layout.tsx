import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import SensorPanel from './SensorPanel';

const Layout: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header Bar */}
      <header className="bg-dark-800 text-white px-6 py-3 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">CONNECT 500</h1>
            <span className="text-gray-300">MASKTRONIC</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Status: ONLINE
            </span>
          </div>
        </div>
      </header>

      {/* Main Layout - 3 Columns */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Menu (20%) */}
        <aside className="w-1/5 bg-dark-700 text-white p-6 overflow-y-auto">
          <nav className="space-y-2">
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 rounded hover:bg-dark-600 transition"
            >
              ... Logout
            </button>
            
            <Link
              to="/"
              className="block px-4 py-2 rounded hover:bg-dark-600 transition"
            >
              Dashboard
            </Link>
            
            <Link
              to="/test-menu"
              className="block px-4 py-2 rounded hover:bg-dark-600 transition"
            >
              Test Menu
            </Link>
            
            <Link
              to="/workshop"
              className="block px-4 py-2 rounded hover:bg-dark-600 transition"
            >
              Workshop
            </Link>
            
            <Link
              to="/reports"
              className="block px-4 py-2 rounded hover:bg-dark-600 transition"
            >
              Test Reports
            </Link>
          </nav>

          {/* User Info */}
          <div className="mt-8 pt-4 border-t border-dark-600">
            <p className="text-sm text-gray-300">Operator:</p>
            <p className="font-semibold">{user.username}</p>
            <p className="text-xs text-gray-400 mt-1">{user.role}</p>
          </div>
        </aside>

        {/* Center - Main Content (55%) */}
        <main className="flex-1 overflow-y-auto p-6 bg-white">
          <Outlet />
        </main>

        {/* Right Sidebar - Sensors (25%) */}
        <aside className="w-1/4 bg-dark-700 text-white p-6 overflow-y-auto">
          <SensorPanel />
        </aside>
      </div>

      {/* Status Bar */}
      <footer className="bg-dark-800 text-white px-6 py-2 text-sm">
        <div className="flex items-center justify-between">
          <span>OPERATOR: {user.username}</span>
          <span>{new Date().toLocaleString('pl-PL')}</span>
          <span>192.168.1.10:8080</span>
          <span>Device Status: Ready</span>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
