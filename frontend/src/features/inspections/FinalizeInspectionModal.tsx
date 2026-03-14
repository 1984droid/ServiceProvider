/**
 * FinalizeInspectionModal
 *
 * Modal for finalizing an inspection with signature capture
 * Displays completion status, defect summary, and signature pad
 * Calls finalize API endpoint with signature data
 */

import { useState } from 'react';
import { SignatureCapture } from './SignatureCapture';

interface FinalizeInspectionModalProps {
  inspectionId: string;
  completionStatus: {
    total_steps: number;
    completed_steps: number;
    required_steps: number;
    required_completed: number;
    ready_to_finalize: boolean;
  };
  defectSummary: {
    total_defects: number;
    by_severity: {
      CRITICAL: number;
      MAJOR: number;
      MINOR: number;
      ADVISORY: number;
    };
  };
  onFinalize: (signatureData: string | null) => Promise<void>;
  onCancel: () => void;
  isOpen: boolean;
}

export function FinalizeInspectionModal({
  inspectionId,
  completionStatus,
  defectSummary,
  onFinalize,
  onCancel,
  isOpen,
}: FinalizeInspectionModalProps) {
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFinalize = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await onFinalize(signatureData);
    } catch (err: any) {
      setError(err.message || 'Failed to finalize inspection');
      setIsSubmitting(false);
    }
  };

  const canFinalize = completionStatus.ready_to_finalize;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Finalize Inspection
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Review completion status and sign to finalize this inspection
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-6">
          {/* Completion Status */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Completion Status
            </h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Total Steps:</span>
                <span className="font-medium text-gray-900">
                  {completionStatus.completed_steps} /{' '}
                  {completionStatus.total_steps}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Required Steps:</span>
                <span className="font-medium text-gray-900">
                  {completionStatus.required_completed} /{' '}
                  {completionStatus.required_steps}
                </span>
              </div>
              <div className="pt-2 border-t border-gray-200">
                {canFinalize ? (
                  <div className="flex items-center gap-2 text-green-700">
                    <svg
                      className="w-5 h-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-sm font-medium">
                      Ready to finalize
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-yellow-700">
                    <svg
                      className="w-5 h-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-sm font-medium">
                      Not all required steps completed
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Defect Summary */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Defects Found
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              {defectSummary.total_defects > 0 ? (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700">Total Defects:</span>
                    <span className="font-medium text-gray-900">
                      {defectSummary.total_defects}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200">
                    {defectSummary.by_severity.CRITICAL > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-red-600 text-white text-xs font-bold rounded">
                          CRITICAL
                        </span>
                        <span className="text-sm font-medium">
                          {defectSummary.by_severity.CRITICAL}
                        </span>
                      </div>
                    )}
                    {defectSummary.by_severity.MAJOR > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-orange-600 text-white text-xs font-bold rounded">
                          MAJOR
                        </span>
                        <span className="text-sm font-medium">
                          {defectSummary.by_severity.MAJOR}
                        </span>
                      </div>
                    )}
                    {defectSummary.by_severity.MINOR > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-yellow-600 text-white text-xs font-bold rounded">
                          MINOR
                        </span>
                        <span className="text-sm font-medium">
                          {defectSummary.by_severity.MINOR}
                        </span>
                      </div>
                    )}
                    {defectSummary.by_severity.ADVISORY > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-blue-600 text-white text-xs font-bold rounded">
                          ADVISORY
                        </span>
                        <span className="text-sm font-medium">
                          {defectSummary.by_severity.ADVISORY}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-green-700">
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm font-medium">
                    No defects found - Inspection passed
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Signature Capture */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Inspector Signature *
            </h3>
            <SignatureCapture onSignatureChange={setSignatureData} />
          </div>

          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex gap-2">
              <svg
                className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              <div className="text-sm text-yellow-800">
                <p className="font-medium">Warning: This action is permanent</p>
                <p className="mt-1">
                  Once finalized, this inspection cannot be edited or modified.
                  Ensure all information is accurate before proceeding.
                </p>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex gap-2">
                <svg
                  className="w-5 h-5 text-red-600 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleFinalize}
            disabled={!canFinalize || !signatureData || isSubmitting}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Finalizing...</span>
              </>
            ) : (
              'Finalize Inspection'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
