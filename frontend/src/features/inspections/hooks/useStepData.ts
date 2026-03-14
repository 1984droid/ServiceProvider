/**
 * useStepData Hook
 *
 * Manages step field values for inspection execution
 * Handles loading existing step data and saving to backend
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/axios';

interface TemplateField {
  field_id: string;
  type: string;
  required?: boolean;
}

interface TemplateStep {
  step_id: string;
  fields: TemplateField[];
}

interface UseStepDataOptions {
  inspectionId: string;
  steps: TemplateStep[];
  existingStepData?: Record<string, Record<string, any>>;
}

interface UseStepDataReturn {
  stepValues: Record<string, any>;
  allStepValues: Record<string, Record<string, any>>;
  completedSteps: Set<number>;
  isDirty: boolean;
  isSaving: boolean;
  error: string | null;
  lastSaved: Date | null;
  setFieldValue: (fieldId: string, value: any) => void;
  setCurrentStep: (stepIndex: number) => void;
  saveCurrentStep: (validate?: boolean) => Promise<void>;
  saveAllSteps: () => Promise<void>;
  loadStepData: () => Promise<void>;
}

export function useStepData({
  inspectionId,
  steps,
  existingStepData = {},
}: UseStepDataOptions): UseStepDataReturn {
  // All step values keyed by step_id -> { field_id: value }
  const [allStepValues, setAllStepValues] = useState<Record<string, Record<string, any>>>(existingStepData);

  // Current step index
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // Completed steps (have all required fields filled)
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  // Track if current step has unsaved changes
  const [isDirty, setIsDirty] = useState(false);

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Get current step
  const currentStep = steps[currentStepIndex];
  const currentStepId = currentStep?.step_id;

  // Get current step values
  const stepValues = allStepValues[currentStepId] || {};

  // Load step data from backend
  const loadStepData = async () => {
    try {
      const response = await apiClient.get(`/inspections/${inspectionId}/`);
      const loadedStepData = response.data.step_data || {};
      setAllStepValues(loadedStepData);

      // Calculate completed steps
      updateCompletedSteps(loadedStepData);
    } catch (err: any) {
      console.error('Failed to load step data:', err);
      setError(err.message || 'Failed to load step data');
    }
  };

  // Update which steps are completed
  const updateCompletedSteps = (stepData: Record<string, Record<string, any>>) => {
    const completed = new Set<number>();

    steps.forEach((step, index) => {
      const values = stepData[step.step_id] || {};
      const isComplete = step.fields.every(field => {
        if (!field.required) return true;
        const value = values[field.field_id];

        // Check if value is present based on field type
        if (value === null || value === undefined) return false;
        if (typeof value === 'string' && value.trim() === '') return false;
        if (Array.isArray(value) && value.length === 0) return false;

        return true;
      });

      if (isComplete) {
        completed.add(index);
      }
    });

    setCompletedSteps(completed);
  };

  // Set field value
  const setFieldValue = (fieldId: string, value: any) => {
    setAllStepValues(prev => ({
      ...prev,
      [currentStepId]: {
        ...(prev[currentStepId] || {}),
        [fieldId]: value,
      },
    }));
    setIsDirty(true);
  };

  // Change current step
  const setCurrentStep = (stepIndex: number) => {
    setCurrentStepIndex(stepIndex);
    setIsDirty(false);
  };

  // Save current step to backend
  const saveCurrentStep = async (validate: boolean = true) => {
    if (!currentStep) return;

    setIsSaving(true);
    setError(null);

    try {
      await apiClient.patch(`/inspections/${inspectionId}/save_step/`, {
        step_key: currentStep.step_id,
        field_data: stepValues,
        validate,
      });

      setIsDirty(false);
      setLastSaved(new Date());

      // Update completed steps
      updateCompletedSteps(allStepValues);
    } catch (err: any) {
      console.error('Failed to save step:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to save step');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  // Save all steps at once
  const saveAllSteps = async () => {
    setIsSaving(true);
    setError(null);

    try {
      // Save each step sequentially
      for (const step of steps) {
        const values = allStepValues[step.step_id] || {};
        if (Object.keys(values).length > 0) {
          await apiClient.patch(`/inspections/${inspectionId}/save_step/`, {
            step_key: step.step_id,
            field_data: values,
            validate: false, // Don't validate when bulk saving
          });
        }
      }

      setIsDirty(false);
      setLastSaved(new Date());
      updateCompletedSteps(allStepValues);
    } catch (err: any) {
      console.error('Failed to save all steps:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to save');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  // Load step data on mount
  useEffect(() => {
    loadStepData();
  }, [inspectionId]);

  // Update completed steps when values change
  useEffect(() => {
    updateCompletedSteps(allStepValues);
  }, [allStepValues, steps]);

  // Auto-save every 30 seconds if dirty
  useEffect(() => {
    if (!isDirty || !currentStep) return;

    const autoSaveTimer = setTimeout(async () => {
      try {
        await saveCurrentStep(false); // Auto-save without validation
      } catch (err) {
        console.error('Auto-save failed:', err);
        // Don't throw - let user continue working
      }
    }, 30000); // 30 seconds

    return () => clearTimeout(autoSaveTimer);
  }, [isDirty, currentStep, allStepValues]);

  return {
    stepValues,
    allStepValues,
    completedSteps,
    isDirty,
    isSaving,
    error,
    lastSaved,
    setFieldValue,
    setCurrentStep,
    saveCurrentStep,
    saveAllSteps,
    loadStepData,
  };
}
