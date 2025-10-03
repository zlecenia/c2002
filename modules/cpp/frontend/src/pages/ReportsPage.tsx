import React from 'react';

const ReportsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Test Reports</h1>

      {/* Statistics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Last 30 Days</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-gray-800">324</p>
            <p className="text-sm text-gray-600">Total Tests</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">318</p>
            <p className="text-sm text-gray-600">Passed</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">2</p>
            <p className="text-sm text-gray-600">Warnings</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">4</p>
            <p className="text-sm text-gray-600">Failed</p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t">
          <p className="text-lg font-medium text-center">
            Pass Rate: <span className="text-primary-600">98.1%</span>
          </p>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Device</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Operator</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Result</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Duration</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t">
                <td className="px-4 py-3">29.09 12:05</td>
                <td className="px-4 py-3">G1-001234</td>
                <td className="px-4 py-3">r.arendt</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    PASSED
                  </span>
                </td>
                <td className="px-4 py-3">42 min</td>
                <td className="px-4 py-3">
                  <button className="text-primary-600 hover:text-primary-700 text-sm">
                    View Report
                  </button>
                </td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-3">28.09 15:20</td>
                <td className="px-4 py-3">FPS-00123</td>
                <td className="px-4 py-3">r.arendt</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                    WARNING
                  </span>
                </td>
                <td className="px-4 py-3">35 min</td>
                <td className="px-4 py-3">
                  <button className="text-primary-600 hover:text-primary-700 text-sm">
                    View Report
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
