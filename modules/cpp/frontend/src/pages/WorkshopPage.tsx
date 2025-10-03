import React from 'react';

const WorkshopPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Workshop Management</h1>

      {/* Equipment List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Equipment Inventory</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Serial</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Last Test</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Next Test</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t">
                <td className="px-4 py-3">G1-2024-001234</td>
                <td className="px-4 py-3">PP Mask</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    Active
                  </span>
                </td>
                <td className="px-4 py-3">15.11.2024</td>
                <td className="px-4 py-3">15.11.2025</td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-3">PSS-2023-00567</td>
                <td className="px-4 py-3">SCBA</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                    Warning
                  </span>
                </td>
                <td className="px-4 py-3">01.09.2024</td>
                <td className="px-4 py-3">02.10.2025</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Maintenance Schedule */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-600 font-medium">Overdue</p>
          <p className="text-3xl font-bold text-red-700">5</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-600 font-medium">Due This Week</p>
          <p className="text-3xl font-bold text-yellow-700">8</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-600 font-medium">Due This Month</p>
          <p className="text-3xl font-bold text-blue-700">23</p>
        </div>
      </div>
    </div>
  );
};

export default WorkshopPage;
