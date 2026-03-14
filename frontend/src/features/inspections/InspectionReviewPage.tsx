/**
 * InspectionReviewPage
 *
 * Read-only view of completed inspection before finalization
 * Displays all step responses, completion status, and defects
 */

import { useState, useEffect } from 'react';
import { inspectionsApi } from '@/api/inspections.api';
import { InspectionHeader } from './InspectionHeader';
import { StepRenderer } from './steps/StepRenderer';

interface InspectionReviewPageProps {
  inspectionId: string;
  onExit: () => void;
  onFinalize?: () => void;
}

interface DefectSummary {
  total: number;
  critical: number;
  major: number;
  minor: number;
  advisory: number;
}

export function InspectionReviewPage({
  inspectionId,
  onExit,
  onFinalize,
}: InspectionReviewPageProps) {
  const [reviewData, setReviewData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedStepIndex, setSelectedStepIndex] = useState(0);

  useEffect(() => {
    loadReviewData();
  }, [inspectionId]);

  const loadReviewData = async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const data = await inspectionsApi.getReview(inspectionId);
      setReviewData(data);
    } catch (err: any) {
      setLoadError(err.message || 'Failed to load inspection review');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading inspection review...</p>
        </div>
      </div>
    );
  }

  if (loadError || !reviewData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{loadError || 'Failed to load review'}</p>
          <button
            onClick={onExit}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Back to List
          </button>
        </div>
      </div>
    );
  }

  const { inspection, completion, defects } = reviewData;
  const template = inspection.template_snapshot?.template || {};
  const steps = inspection.template_snapshot?.procedure?.steps || [];
  const currentStep = steps[selectedStepIndex];

  // Get step response for current step
  const stepResponse = inspection.step_responses?.[currentStep?.step_id] || {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <InspectionHeader
        assetInfo={inspection.asset_info}
        templateName={template.name || 'Unknown Template'}
        inspectorName={inspection.inspector_name || 'Unknown'}
        status={inspection.status}
        currentStep={selectedStepIndex + 1}
        totalSteps={steps.length}
        completionPercent={completion.percent_complete || 0}
      />

      {/* Review Banner */}
      <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div>
            <h2 className="text-lg font-semibold text-blue-900">Inspection Review</h2>
            <p className="text-sm text-blue-700">
              Read-only view • {completion.completed_required_steps} of {completion.required_steps} required steps completed
            </p>
          </div>
          <div className="flex gap-3">
            {completion.is_ready_to_finalize && onFinalize && (
              <button
                onClick={onFinalize}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 font-medium"
              >
                Finalize Inspection
              </button>
            )}
            <button
              onClick={onExit}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Exit Review
            </button>
          </div>
        </div>
      </div>

      {/* Defects Summary */}
      {defects.count > 0 && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-6 py-4">
          <div className="max-w-6xl mx-auto">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              {defects.count} Defect{defects.count !== 1 ? 's' : ''} Found
            </h3>
            <div className="flex gap-6">
              {defects.summary.critical > 0 && (
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-red-600 text-white text-xs font-bold rounded">
                    CRITICAL
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    {defects.summary.critical}
                  </span>
                </div>
              )}
              {defects.summary.major > 0 && (
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-orange-600 text-white text-xs font-bold rounded">
                    MAJOR
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    {defects.summary.major}
                  </span>
                </div>
              )}
              {defects.summary.minor > 0 && (
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-yellow-600 text-white text-xs font-bold rounded">
                    MINOR
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    {defects.summary.minor}
                  </span>
                </div>
              )}
              {defects.summary.advisory > 0 && (
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-blue-600 text-white text-xs font-bold rounded">
                    ADVISORY
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    {defects.summary.advisory}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-6xl mx-auto py-6 px-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Step Navigation Sidebar */}
          <div className="col-span-3">
            <div className="bg-white rounded-lg shadow p-4 sticky top-6">
              <h3 className="font-semibold text-gray-900 mb-3">Steps</h3>
              <div className="space-y-1">
                {steps.map((step: any, index: number) => {
                  const isCompleted = inspection.step_responses?.[step.step_id];
                  const isSelected = index === selectedStepIndex;

                  return (
                    <button
                      key={step.step_id}
                      onClick={() => setSelectedStepIndex(index)}
                      className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                        isSelected
                          ? 'bg-blue-100 text-blue-900 font-medium'
                          : isCompleted
                          ? 'bg-green-50 text-green-900 hover:bg-green-100'
                          : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-xs">
                          {isCompleted ? '✓' : index + 1}
                        </span>
                        <span className="truncate">{step.title}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Step Content */}
          <div className="col-span-9">
            {currentStep ? (
              <div className="bg-white rounded-lg shadow p-6">
                <StepRenderer
                  step={currentStep}
                  currentIndex={selectedStepIndex}
                  totalSteps={steps.length}
                  values={stepResponse || {}}
                  onChange={() => {}} // Read-only, no changes allowed
                  errors={{}}
                  disabled={true} // All fields disabled for read-only mode
                  enumValues={inspection.template_snapshot?.enums || {}}
                  measurementSets={inspection.template_snapshot?.measurement_sets || {}}
                  inspectionId={inspectionId}
                />

                {/* Step Defects */}
                {defects.items.filter((d: any) => d.step_key === currentStep.step_id).length > 0 && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-3">
                      Defects Found in This Step
                    </h4>
                    <div className="space-y-3">
                      {defects.items
                        .filter((d: any) => d.step_key === currentStep.step_id)
                        .map((defect: any) => (
                          <div
                            key={defect.id}
                            className="p-4 border border-gray-200 rounded-lg bg-gray-50"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span
                                    className={`px-2 py-1 text-xs font-bold rounded ${
                                      defect.severity === 'CRITICAL'
                                        ? 'bg-red-600 text-white'
                                        : defect.severity === 'MAJOR'
                                        ? 'bg-orange-600 text-white'
                                        : defect.severity === 'MINOR'
                                        ? 'bg-yellow-600 text-white'
                                        : 'bg-blue-600 text-white'
                                    }`}
                                  >
                                    {defect.severity}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {defect.status}
                                  </span>
                                </div>
                                <h5 className="font-medium text-gray-900">
                                  {defect.title}
                                </h5>
                                {defect.description && (
                                  <p className="text-sm text-gray-600 mt-1">
                                    {defect.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                No step selected
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
