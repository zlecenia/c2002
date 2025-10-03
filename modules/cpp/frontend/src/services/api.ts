import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth-storage');
        if (token) {
          try {
            const authData = JSON.parse(token);
            if (authData.state?.token) {
              config.headers.Authorization = `Bearer ${authData.state.token}`;
            }
          } catch (e) {
            console.error('Error parsing auth token:', e);
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Redirect to login
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // System endpoints
  async startSystem(deviceIp: string) {
    const response = await this.client.post('/tests/system/start', { device_ip: deviceIp });
    return response.data;
  }

  async runDiagnostic() {
    const response = await this.client.post('/tests/system/diagnostic');
    return response.data;
  }

  // Test endpoints
  async initializeTest(testData: any) {
    const response = await this.client.post('/tests/initialize', testData);
    return response.data;
  }

  async getTestSession(testSessionId: string) {
    const response = await this.client.get(`/tests/${testSessionId}`);
    return response.data;
  }

  async submitTestStep(testSessionId: string, stepId: number, stepData: any) {
    const response = await this.client.post(`/tests/${testSessionId}/step/${stepId}`, stepData);
    return response.data;
  }

  async completeTest(testSessionId: string) {
    const response = await this.client.post(`/tests/${testSessionId}/complete`);
    return response.data;
  }

  async getTestReport(testSessionId: string) {
    const response = await this.client.get(`/tests/${testSessionId}/report`);
    return response.data;
  }

  // Mock login for demo
  async login(username: string, password: string) {
    // Mock implementation
    return {
      access_token: 'mock-jwt-token',
      user: {
        id: 1,
        username,
        role: 'operator',
        full_name: 'Robert Arendt',
      },
    };
  }
}

export const apiService = new ApiService();
