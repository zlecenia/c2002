import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const DashboardPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Welcome, {user?.fullName || user?.username}!
        </h1>
        <p className="text-primary-100">Operator Dashboard - Connect++ (CPP)</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          to="/test-menu"
          className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition border-2 border-transparent hover:border-primary-500"
        >
          <div className="text-4xl mb-2">🧪</div>
          <h3 className="font-semibold text-lg mb-1">Start Testing</h3>
          <p className="text-sm text-gray-600">Begin a new device test</p>
        </Link>

        <Link
          to="/workshop"
          className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition border-2 border-transparent hover:border-primary-500"
        >
          <div className="text-4xl mb-2">🔧</div>
          <h3 className="font-semibold text-lg mb-1">Workshop</h3>
          <p className="text-sm text-gray-600">Equipment & maintenance</p>
        </Link>

        <Link
          to="/reports"
          className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition border-2 border-transparent hover:border-primary-500"
        >
          <div className="text-4xl mb-2">📊</div>
          <h3 className="font-semibold text-lg mb-1">Reports</h3>
          <p className="text-sm text-gray-600">View test history</p>
        </Link>

        <div className="bg-white p-6 rounded-lg shadow border-2 border-gray-200">
          <div className="text-4xl mb-2">📱</div>
          <h3 className="font-semibold text-lg mb-1">Quick Scan</h3>
          <p className="text-sm text-gray-600">Scan device QR code</p>
        </div>
      </div>

      {/* Statistics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Today's Statistics</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-primary-600">15</p>
            <p className="text-sm text-gray-600">Tests Today</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">14</p>
            <p className="text-sm text-gray-600">Passed</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">1</p>
            <p className="text-sm text-gray-600">Warnings</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">0</p>
            <p className="text-sm text-gray-600">Failed</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Tests</h2>
        <div className="space-y-2">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <div>
              <p className="font-medium">G1-2024-001234</p>
              <p className="text-sm text-gray-600">PP Mask - Standard Test</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
              PASSED
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <div>
              <p className="font-medium">PSS-2023-00567</p>
              <p className="text-sm text-gray-600">SCBA - Extended Test</p>
            </div>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
              WARNING
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
