import { create } from 'zustand';

interface SensorData {
  pressure_low: number;
  pressure_medium: number;
  pressure_high: number;
  timestamp: Date;
}

interface TestSession {
  testSessionId: string;
  status: 'initialized' | 'in_progress' | 'completed' | 'aborted';
  currentStep: number;
  totalSteps: number;
  deviceSerial: string;
}

interface TestState {
  currentSession: TestSession | null;
  sensorData: SensorData;
  isTestRunning: boolean;
  startTest: (session: TestSession) => void;
  updateStep: (stepId: number) => void;
  updateSensorData: (data: Partial<SensorData>) => void;
  completeTest: () => void;
  abortTest: () => void;
}

export const useTestStore = create<TestState>((set) => ({
  currentSession: null,
  sensorData: {
    pressure_low: 0,
    pressure_medium: 0,
    pressure_high: 0,
    timestamp: new Date(),
  },
  isTestRunning: false,
  startTest: (session) => {
    set({ currentSession: session, isTestRunning: true });
  },
  updateStep: (stepId) => {
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, currentStep: stepId }
        : null,
    }));
  },
  updateSensorData: (data) => {
    set((state) => ({
      sensorData: {
        ...state.sensorData,
        ...data,
        timestamp: new Date(),
      },
    }));
  },
  completeTest: () => {
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, status: 'completed' }
        : null,
      isTestRunning: false,
    }));
  },
  abortTest: () => {
    set((state) => ({
      currentSession: state.currentSession
        ? { ...state.currentSession, status: 'aborted' }
        : null,
      isTestRunning: false,
    }));
  },
}));
