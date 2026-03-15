/**
 * InspectionExecutePage
 *
 * Main page for executing an inspection
 * Loads inspection run and template, orchestrates step navigation
 * Integrated with useStepData hook for data management
 */

import { useState, useEffect } from 'react';
import { inspectionsApi, type InspectionRun } from '@/api/inspections.api';
import { InspectionHeader } from './InspectionHeader';
import { InspectionStepper } from './InspectionStepper';
import { InspectionActions } from './InspectionActions';
import { StepRenderer } from './steps/StepRenderer';
import { useStepData } from './hooks/useStepData';

interface InspectionExecutePageProps {
  inspectionId: string;
  onExit: () => void;
}

// Template structure based on AF_INSPECTION_TEMPLATE
interface TemplateField {
  field_id: string;
  type: string;
  label: string;
  required?: boolean;
  help_text?: string;
  values?: string[];
  enum_ref?: string;
  min?: number;
  max?: number;
  precision?: number;
}

interface TemplateStep {
  step_id: string;
  type: string;
  title: string;
  description?: string;
  standard_reference?: string;
  fields: TemplateField[];
  measurement_set_ref?: string;
}

interface InspectionTemplate {
  template_key: string;
  name: string;
  domain?: string;
  standard_code?: string;
  steps: TemplateStep[];
  enums?: Record<string, string[]>;
  measurement_sets?: Record<string, {
    title: string;
    fields: TemplateField[];
  }>;
}

export function InspectionExecutePage({
  inspectionId,
  onExit,
}: InspectionExecutePageProps) {
  const [inspectionRun, setInspectionRun] = useState<InspectionRun | null>(null);
  const [template, setTemplate] = useState<InspectionTemplate | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    loadInspectionData();
  }, [inspectionId]);

  const loadInspectionData = async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      // Load inspection run
      const runData = await inspectionsApi.get(inspectionId);
      setInspectionRun(runData);

      // Use template_snapshot from the inspection run (already contains full template)
      const templateSnapshot = runData.template_snapshot;

      // Transform to expected format: extract procedure.steps to steps
      const transformedTemplate = {
        template_key: templateSnapshot.template?.template_key || '',
        name: templateSnapshot.template?.name || 'Unknown Template',
        domain: templateSnapshot.template?.intent?.domain,
        standard_code: templateSnapshot.template?.standard?.code,
        steps: templateSnapshot.procedure?.steps || [],
        enums: templateSnapshot.enums || {},
        measurement_sets: templateSnapshot.measurement_sets || {},
      };

      setTemplate(transformedTemplate);
    } catch (err: any) {
      setLoadError(err.message || 'Failed to load inspection');
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize step data hook (only after template is loaded)
  const stepData = useStepData({
    inspectionId,
    steps: template?.steps || [],
    existingStepData: inspectionRun?.step_data || {},
    enumValues: template?.enums || {},
    measurementSets: template?.measurement_sets || {},
  });

  const handleStepClick = (index: number) => {
    stepData.setCurrentStep(index);
    setCurrentStepIndex(index);
  };

  const handlePrevious = async () => {
    if (currentStepIndex > 0) {
      // Auto-save current step before moving (Milestone 6 will add auto-save)
      if (stepData.isDirty) {
        try {
          await stepData.saveCurrentStep(false); // Don't validate on navigation
        } catch (err) {
          // Continue navigation even if save fails
          console.error('Failed to auto-save step:', err);
        }
      }

      const newIndex = currentStepIndex - 1;
      stepData.setCurrentStep(newIndex);
      setCurrentStepIndex(newIndex);
    }
  };

  const handleNext = async () => {
    if (template && currentStepIndex < template.steps.length - 1) {
      // Validate current step before allowing navigation
      const isValid = stepData.validateCurrentStep();
      if (!isValid) {
        return; // Block navigation if validation fails
      }

      // Auto-save current step before moving
      if (stepData.isDirty) {
        try {
          await stepData.saveCurrentStep(false); // Don't validate on navigation (already validated above)
        } catch (err) {
          // Continue navigation even if save fails
          console.error('Failed to auto-save step:', err);
        }
      }

      const newIndex = currentStepIndex + 1;
      stepData.setCurrentStep(newIndex);
      setCurrentStepIndex(newIndex);
    }
  };

  const handleSaveDraft = async () => {
    try {
      await stepData.saveCurrentStep(false);
    } catch (err: any) {
      // Error is already set in stepData.error
      console.error('Failed to save draft:', err);
    }
  };

  const handleSaveAndExit = async () => {
    try {
      // Save current step
      if (stepData.isDirty) {
        await stepData.saveCurrentStep(false);
      }
      onExit();
    } catch (err: any) {
      alert(`Failed to save: ${err.message}`);
    }
  };

  const handleComplete = async () => {
    // TODO: Add validation in Milestone 7
    // TODO: Add finalize API call in Milestone 7
    console.log('Complete inspection - will implement in Milestone 7');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading inspection...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (loadError || !inspectionRun || !template) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Inspection</h3>
          <p className="text-sm text-gray-600 mb-4">{loadError || 'Inspection not found'}</p>
          <button
            onClick={onExit}
            className="px-4 py-2 text-sm font-medium text-white rounded"
            style={{ backgroundColor: '#7ed321' }}
          >
            Back to Inspections
          </button>
        </div>
      </div>
    );
  }

  // Get current step
  const currentStep = template.steps[currentStepIndex];

  // Calculate completion percentage
  const completionPercent = inspectionRun.completion_status?.percent_complete || 0;

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0">
        <InspectionHeader
          assetInfo={inspectionRun.asset_info || null}
          templateName={template.name}
          inspectorName={inspectionRun.inspector_name || 'Unknown'}
          status={inspectionRun.status}
          currentStep={currentStepIndex}
          totalSteps={template.steps.length}
          completionPercent={completionPercent}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Step Navigation */}
        <div className="flex-shrink-0">
          <InspectionStepper
            steps={template.steps}
            currentStepIndex={currentStepIndex}
            onStepClick={handleStepClick}
            completedSteps={stepData.completedSteps}
          />
        </div>

        {/* Center - Current Step Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {stepData.error && (
            <div className="mb-4 p-3 rounded" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>
              <p className="text-sm">{stepData.error}</p>
            </div>
          )}
          <StepRenderer
            step={currentStep}
            currentIndex={currentStepIndex}
            totalSteps={template.steps.length}
            values={stepData.stepValues}
            onChange={stepData.setFieldValue}
            errors={stepData.validationErrors}
            enumValues={template.enums || {}}
            measurementSets={template.measurement_sets || {}}
            inspectionId={inspectionId}
            templateKey={inspectionRun?.template_key}
          />
        </div>
      </div>

      {/* Footer - Actions */}
      <div className="flex-shrink-0">
        <InspectionActions
          currentStepIndex={currentStepIndex}
          totalSteps={template.steps.length}
          onPrevious={handlePrevious}
          onNext={handleNext}
          onSaveDraft={handleSaveDraft}
          onSaveAndExit={handleSaveAndExit}
          onComplete={handleComplete}
          isSaving={stepData.isSaving}
          isDirty={stepData.isDirty}
          lastSaved={stepData.lastSaved}
          canProceed={stepData.isCurrentStepValid}
        />
      </div>
    </div>
  );
}
