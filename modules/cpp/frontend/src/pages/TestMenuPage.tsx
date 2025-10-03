import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const TestMenuPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedKind, setSelectedKind] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [deviceSerial, setDeviceSerial] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const deviceKinds = [
    { id: 1, name: 'PP Mask', description: 'Positive Pressure Mask' },
    { id: 2, name: 'NP Mask', description: 'Negative Pressure Mask' },
    { id: 3, name: 'SCBA', description: 'Self-Contained Breathing Apparatus' },
    { id: 4, name: 'CPS Suit', description: 'Chemical Protection Suit' },
  ];

  const deviceTypes = [
    { id: 1, name: 'Ultra Elite', category: 'PP Mask' },
    { id: 2, name: 'G1', category: 'PP Mask' },
    { id: 3, name: 'FPS 7000', category: 'PP Mask' },
  ];

  const handleStartTest = async () => {
    if (!selectedKind || !selectedType || !deviceSerial) {
      alert('Please select device kind, type, and enter serial number');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiService.initializeTest({
        device_kind_id: parseInt(selectedKind),
        device_type_id: parseInt(selectedType),
        test_kind_id: 3,
        scenario_id: 1,
        device_serial: deviceSerial,
      });

      navigate(`/test-execution/${response.test_session_id}`);
    } catch (error: any) {
      alert('Failed to initialize test: ' + (error.message || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Test Menu</h1>

      {/* Step 1: Kind of Device */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">1. Kind of Device</h2>
        <div className="grid grid-cols-2 gap-4">
          {deviceKinds.map((kind) => (
            <button
              key={kind.id}
              onClick={() => setSelectedKind(kind.id.toString())}
              className={`p-6 rounded-lg border-2 transition ${
                selectedKind === kind.id.toString()
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
              }`}
            >
              <div className="text-4xl mb-2">🔧</div>
              <h3 className="font-semibold text-lg">{kind.name}</h3>
              <p className="text-sm text-gray-600">{kind.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Device Type */}
      {selectedKind && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">2. Device Type</h2>
          <div className="space-y-2">
            {deviceTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedType(type.id.toString())}
                className={`w-full p-4 rounded-lg border-2 text-left transition ${
                  selectedType === type.id.toString()
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300'
                }`}
              >
                <h3 className="font-semibold">{type.name}</h3>
                <p className="text-sm text-gray-600">{type.category}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Device Serial */}
      {selectedType && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">3. Device Serial Number</h2>
          <div className="space-y-4">
            <input
              type="text"
              value={deviceSerial}
              onChange={(e) => setDeviceSerial(e.target.value)}
              placeholder="Scan QR code or enter serial number"
              className="w-full p-3 border border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
            />
            <p className="text-sm text-gray-600">
              Example: G1-2024-001234
            </p>
          </div>
        </div>
      )}

      {/* Start Test Button */}
      {deviceSerial && (
        <div className="flex justify-end space-x-4">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition"
          >
            Cancel
          </button>
          <button
            onClick={handleStartTest}
            disabled={isLoading}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition disabled:opacity-50"
          >
            {isLoading ? 'Initializing...' : 'Start Test'}
          </button>
        </div>
      )}
    </div>
  );
};

export default TestMenuPage;
