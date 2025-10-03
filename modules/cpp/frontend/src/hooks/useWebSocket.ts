import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useTestStore } from '../stores/testStore';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8080';

export const useWebSocket = (testSessionId?: string) => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const updateSensorData = useTestStore((state) => state.updateSensorData);

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    });

    socket.on('connection_established', (data) => {
      console.log('Connection established:', data);
    });

    socket.on('sensor_update', (data) => {
      console.log('Sensor update:', data);
      if (data.sensor_type === 'pressure_low') {
        updateSensorData({ pressure_low: data.value });
      } else if (data.sensor_type === 'pressure_medium') {
        updateSensorData({ pressure_medium: data.value });
      } else if (data.sensor_type === 'pressure_high') {
        updateSensorData({ pressure_high: data.value });
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [updateSensorData]);

  const sendSensorData = (sensorType: string, value: number, unit: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('sensor_data', {
        type: 'sensor_reading',
        test_session_id: testSessionId,
        data: {
          sensor_type: sensorType,
          value,
          unit,
        },
      });
    }
  };

  return {
    isConnected,
    sendSensorData,
  };
};
