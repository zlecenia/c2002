import React, { useEffect } from 'react';
import { useTestStore } from '../stores/testStore';
import { useWebSocket } from '../hooks/useWebSocket';

const SensorPanel: React.FC = () => {
  const sensorData = useTestStore((state) => state.sensorData);
  const { isConnected } = useWebSocket();

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 border-b border-dark-600 pb-2">
          DATA SENSORS
        </h3>
        
        {/* Connection Status */}
        <div className="mb-4 flex items-center">
          <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>

        {/* Pressure Sensors */}
        <div className="space-y-4">
          <div className="bg-dark-800 p-4 rounded">
            <p className="text-sm text-gray-400 mb-1">PRESSURE LOW</p>
            <p className="text-2xl font-bold text-primary-400">
              {sensorData.pressure_low.toFixed(1)} <span className="text-sm">mbar</span>
            </p>
          </div>

          <div className="bg-dark-800 p-4 rounded">
            <p className="text-sm text-gray-400 mb-1">PRESSURE MEDIUM</p>
            <p className="text-2xl font-bold text-primary-400">
              {sensorData.pressure_medium.toFixed(1)} <span className="text-sm">bar</span>
            </p>
          </div>

          <div className="bg-dark-800 p-4 rounded">
            <p className="text-sm text-gray-400 mb-1">PRESSURE HIGH</p>
            <p className="text-2xl font-bold text-primary-400">
              {sensorData.pressure_high.toFixed(1)} <span className="text-sm">bar</span>
            </p>
          </div>
        </div>

        {/* Device Photo/QR Placeholder */}
        <div className="mt-6 bg-dark-800 p-4 rounded text-center">
          <div className="h-32 flex items-center justify-center border-2 border-dashed border-dark-600 rounded">
            <p className="text-gray-500">Photo/QR Scanner</p>
          </div>
        </div>

        {/* Device Status */}
        <div className="mt-6 bg-dark-800 p-4 rounded">
          <p className="text-sm text-gray-400 mb-1">CONNECT 500</p>
          <p className="text-lg font-semibold text-primary-400">Status: Ready</p>
          <p className="text-xs text-gray-500 mt-2">
            Last update: {sensorData.timestamp.toLocaleTimeString('pl-PL')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SensorPanel;
