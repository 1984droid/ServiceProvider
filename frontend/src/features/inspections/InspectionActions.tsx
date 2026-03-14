/**
 * InspectionActions
 *
 * Action buttons for inspection execution
 * Previous/Next/Save & Exit/Complete Inspection
 */

interface InspectionActionsProps {
  currentStepIndex: number;
  totalSteps: number;
  onPrevious: () => void;
  onNext: () => void;
  onSaveAndExit: () => void;
  onComplete: () => void;
  isSaving?: boolean;
  isCompleting?: boolean;
  canProceed?: boolean; // For validation in Milestone 7
  disabled?: boolean;
}

export function InspectionActions({
  currentStepIndex,
  totalSteps,
  onPrevious,
  onNext,
  onSaveAndExit,
  onComplete,
  isSaving = false,
  isCompleting = false,
  canProceed = true,
  disabled = false,
}: InspectionActionsProps) {

  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === totalSteps - 1;

  return (
    <div className="border-t" style={{ borderColor: '#e5e7eb', backgroundColor: 'white' }}>
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Left Side - Previous Button */}
        <div>
          {!isFirstStep && (
            <button
              onClick={onPrevious}
              disabled={disabled || isSaving || isCompleting}
              className="px-4 py-2 text-sm font-medium rounded transition-colors flex items-center gap-2"
              style={{
                backgroundColor: 'white',
                border: '1px solid #d1d5db',
                color: disabled || isSaving || isCompleting ? '#9ca3af' : '#374151',
                cursor: disabled || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
          )}
        </div>

        {/* Center - Save & Exit Button */}
        <div>
          <button
            onClick={onSaveAndExit}
            disabled={disabled || isSaving || isCompleting}
            className="px-4 py-2 text-sm font-medium rounded transition-colors flex items-center gap-2"
            style={{
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              color: disabled || isSaving || isCompleting ? '#9ca3af' : '#374151',
              cursor: disabled || isSaving || isCompleting ? 'not-allowed' : 'pointer',
            }}
          >
            {isSaving ? (
              <>
                <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Save & Exit
              </>
            )}
          </button>
        </div>

        {/* Right Side - Next or Complete Button */}
        <div>
          {isLastStep ? (
            <button
              onClick={onComplete}
              disabled={disabled || !canProceed || isSaving || isCompleting}
              className="px-6 py-2 text-sm font-medium text-white rounded transition-colors flex items-center gap-2"
              style={{
                backgroundColor: disabled || !canProceed || isSaving || isCompleting ? '#9ca3af' : '#7ed321',
                cursor: disabled || !canProceed || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              {isCompleting ? (
                <>
                  <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Completing...
                </>
              ) : (
                <>
                  Complete Inspection
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={onNext}
              disabled={disabled || !canProceed || isSaving || isCompleting}
              className="px-4 py-2 text-sm font-medium text-white rounded transition-colors flex items-center gap-2"
              style={{
                backgroundColor: disabled || !canProceed || isSaving || isCompleting ? '#9ca3af' : '#7ed321',
                cursor: disabled || !canProceed || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              Next
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
