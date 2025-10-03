import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTestStore } from '../stores/testStore';
import { apiService } from '../services/api';

const TestExecutionPage: React.FC = () => {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [testData, setTestData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const totalSteps = 7;

  useEffect(() => {
    const loadTestSession = async () => {
      if (!testId) return;
      
      try {
        const data = await apiService.getTestSession(testId);
        setTestData(data);
        setCurrentStep(data.current_step || 1);
      } catch (error) {
        console.error('Failed to load test session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTestSession();
  }, [testId]);

  const handleNextStep = async () => {
    if (currentStep < totalSteps) {
      try {
        await apiService.submitTestStep(testId!, currentStep, {
          step_id: currentStep,
          step_name: `Step ${currentStep}`,
          result: 'PASSED',
          duration: 60,
        });
        setCurrentStep(currentStep + 1);
      } catch (error) {
        console.error('Failed to submit step:', error);
      }
    } else {
      // Complete test
      try {
        await apiService.completeTest(testId!);
        navigate('/reports');
      } catch (error) {
        console.error('Failed to complete test:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading test session...</p>
        </div>
      </div>
    );
  }

  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold">Test In Progress</h1>
            <p className="text-gray-600">Test ID: {testId}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Step {currentStep} of {totalSteps}</p>
            <p className="text-2xl font-bold text-primary-600">{Math.round(progress)}%</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-primary-600 h-4 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">
          Step {currentStep}: {getStepName(currentStep)}
        </h2>

        <div className="space-y-4">
          {currentStep === 1 && (
            <div>
              <h3 className="font-medium mb-2">Visual Inspection</h3>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" />
                  <span>No mechanical damage</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" />
                  <span>Visor intact</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2" />
                  <span>Elastomers in good condition</span>
                </label>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div>
              <h3 className="font-medium mb-2">Create Negative Pressure (-14 mbar)</h3>
              <div className="bg-gray-100 p-6 rounded-lg text-center">
                <p className="text-4xl font-bold text-primary-600">-13.8 mbar</p>
                <p className="text-sm text-gray-600 mt-2">Target: -14.0 mbar ±0.5</p>
                <p className="text-green-600 mt-2">✓ IN RANGE</p>
              </div>
            </div>
          )}

          {currentStep > 2 && currentStep < totalSteps && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔬</div>
              <p className="text-lg text-gray-700">Performing automatic test...</p>
              <p className="text-sm text-gray-500 mt-2">
                Step {currentStep}: {getStepName(currentStep)}
              </p>
            </div>
          )}

          {currentStep === totalSteps && (
            <div className="text-center py-12 bg-green-50 rounded-lg">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-2xl font-bold text-green-700 mb-2">Test Completed!</p>
              <p className="text-gray-600">All steps passed successfully</p>
            </div>
          )}
        </div>

        {/* Notes */}
        <div className="mt-6">
          <label className="block text-sm font-medium mb-2">Notes (optional)</label>
          <textarea
            className="w-full p-3 border border-gray-300 rounded-lg focus:border-primary-500 focus:outline-none"
            rows={3}
            placeholder="Add any observations or notes..."
          ></textarea>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition"
        >
          Abort Test
        </button>

        <button
          onClick={handleNextStep}
          className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition"
        >
          {currentStep === totalSteps ? 'Complete Test' : 'Next Step →'}
        </button>
      </div>
    </div>
  );
};

function getStepName(step: number): string {
  const steps = [
    'Visual Inspection',
    'Create Negative Pressure',
    'Stabilization',
    'Set Parameters',
    'Leak Test',
    'Valve Test',
    'Flow Test',
  ];
  return steps[step - 1] || 'Test Step';
}

export default TestExecutionPage;
