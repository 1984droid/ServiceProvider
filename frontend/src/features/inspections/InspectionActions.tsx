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
  onSaveDraft: () => void;
  onSaveAndExit: () => void;
  onComplete: () => void;
  isSaving?: boolean;
  isCompleting?: boolean;
  isDirty?: boolean;
  lastSaved?: Date | null;
  canProceed?: boolean; // For validation in Milestone 7
  disabled?: boolean;
}

export function InspectionActions({
  currentStepIndex,
  totalSteps,
  onPrevious,
  onNext,
  onSaveDraft,
  onSaveAndExit,
  onComplete,
  isSaving = false,
  isCompleting = false,
  isDirty = false,
  lastSaved = null,
  canProceed = true,
  disabled = false,
}: InspectionActionsProps) {

  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === totalSteps - 1;

  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return '';
    const now = new Date();
    const diff = Math.floor((now.getTime() - lastSaved.getTime()) / 1000);

    if (diff < 60) return 'Saved just now';
    if (diff < 3600) return `Saved ${Math.floor(diff / 60)} min ago`;
    return `Saved at ${lastSaved.toLocaleTimeString()}`;
  };

  return (
    <div className="border-t p-1.5" style={{ borderColor: '#e5e7eb', backgroundColor: 'white' }}>
      <div className="flex items-center justify-between">
        {/* Left Side - Previous Button */}
        <div>
          {!isFirstStep && (
            <button
              onClick={onPrevious}
              disabled={disabled || isSaving || isCompleting}
              className="px-2.5 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1.5"
              style={{
                backgroundColor: 'white',
                border: '1px solid #d1d5db',
                color: disabled || isSaving || isCompleting ? '#9ca3af' : '#374151',
                cursor: disabled || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
          )}
        </div>

        {/* Center - Save Buttons and Status */}
        <div className="flex items-center gap-3">
          {/* Save Draft Button */}
          <button
            onClick={onSaveDraft}
            disabled={disabled || isSaving || isCompleting || !isDirty}
            className="px-2.5 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1.5"
            style={{
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              color: disabled || isSaving || isCompleting || !isDirty ? '#9ca3af' : '#374151',
              cursor: disabled || isSaving || isCompleting || !isDirty ? 'not-allowed' : 'pointer',
            }}
            title={!isDirty ? 'No unsaved changes' : 'Save current step'}
          >
            {isSaving ? (
              <>
                <div className="inline-block animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-gray-900"></div>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Save Draft
              </>
            )}
          </button>

          {/* Save Status Indicator */}
          {!isSaving && lastSaved && (
            <div className="flex items-center gap-2 text-xs" style={{ color: isDirty ? '#f59e0b' : '#10b981' }}>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                {isDirty ? (
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                ) : (
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                )}
              </svg>
              <span>{isDirty ? 'Unsaved changes' : formatLastSaved()}</span>
            </div>
          )}

          {/* Save & Exit Button */}
          <button
            onClick={onSaveAndExit}
            disabled={disabled || isSaving || isCompleting}
            className="px-2.5 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1.5"
            style={{
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              color: disabled || isSaving || isCompleting ? '#9ca3af' : '#374151',
              cursor: disabled || isSaving || isCompleting ? 'not-allowed' : 'pointer',
            }}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Save & Exit
          </button>
        </div>

        {/* Right Side - Next or Complete Button */}
        <div>
          {isLastStep ? (
            <button
              onClick={onComplete}
              disabled={disabled || !canProceed || isSaving || isCompleting}
              className="px-4 py-1.5 text-xs font-medium text-white rounded transition-colors flex items-center gap-1.5"
              style={{
                backgroundColor: disabled || !canProceed || isSaving || isCompleting ? '#9ca3af' : '#7ed321',
                cursor: disabled || !canProceed || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              {isCompleting ? (
                <>
                  <div className="inline-block animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white"></div>
                  Completing...
                </>
              ) : (
                <>
                  Complete Inspection
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={onNext}
              disabled={disabled || !canProceed || isSaving || isCompleting}
              className="px-2.5 py-1.5 text-xs font-medium text-white rounded transition-colors flex items-center gap-1.5"
              style={{
                backgroundColor: disabled || !canProceed || isSaving || isCompleting ? '#9ca3af' : '#7ed321',
                cursor: disabled || !canProceed || isSaving || isCompleting ? 'not-allowed' : 'pointer',
              }}
            >
              Next
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
