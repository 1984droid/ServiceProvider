/**
 * InspectionExecutePage
 *
 * Main page for executing an inspection
 * Loads inspection run and template, orchestrates step navigation
 * Read-only for now (saving in Milestone 4)
 */

import { useState, useEffect } from 'react';
import { inspectionsApi, type InspectionRun } from '@/api/inspections.api';
import { InspectionHeader } from './InspectionHeader';
import { InspectionStepper } from './InspectionStepper';
import { InspectionActions } from './InspectionActions';
import { StepRenderer } from './steps/StepRenderer';

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
  const [error, setError] = useState<string | null>(null);

  // Step data state (will be enhanced in Milestone 4)
  const [stepValues, setStepValues] = useState<Record<string, any>>({});
  const [completedSteps] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadInspectionData();
  }, [inspectionId]);

  const loadInspectionData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Load inspection run
      const runData = await inspectionsApi.get(inspectionId);
      setInspectionRun(runData);

      // Load template
      const templateData = await inspectionsApi.getTemplate(runData.template_key);
      setTemplate(templateData);
    } catch (err: any) {
      setError(err.message || 'Failed to load inspection');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStepClick = (index: number) => {
    setCurrentStepIndex(index);
  };

  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  const handleNext = () => {
    if (template && currentStepIndex < template.steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
    }
  };

  const handleSaveAndExit = () => {
    // TODO: Implement in Milestone 4 (manual save)
    console.log('Save and exit - will implement in Milestone 4');
    onExit();
  };

  const handleComplete = () => {
    // TODO: Implement in Milestone 7 (validation + completion)
    console.log('Complete inspection - will implement in Milestone 7');
  };

  const handleFieldChange = (fieldId: string, value: any) => {
    setStepValues(prev => ({
      ...prev,
      [fieldId]: value,
    }));
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
  if (error || !inspectionRun || !template) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Inspection</h3>
          <p className="text-sm text-gray-600 mb-4">{error || 'Inspection not found'}</p>
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
            completedSteps={completedSteps}
          />
        </div>

        {/* Center - Current Step Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <StepRenderer
            step={currentStep}
            currentIndex={currentStepIndex}
            totalSteps={template.steps.length}
            values={stepValues}
            onChange={handleFieldChange}
            enumValues={template.enums || {}}
            measurementSets={template.measurement_sets || {}}
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
          onSaveAndExit={handleSaveAndExit}
          onComplete={handleComplete}
        />
      </div>
    </div>
  );
}
