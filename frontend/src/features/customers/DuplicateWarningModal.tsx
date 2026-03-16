/**
 * DuplicateWarningModal Component
 *
 * Modal dialog shown when potential duplicate customers are detected.
 * Displays matches with confidence scores and allows user to select existing or create new.
 */

import { type DuplicateMatch } from '@/api/customers.api';

interface DuplicateWarningModalProps {
  matches: DuplicateMatch[];
  onSelectExisting: (customerId: string) => void;
  onCreateNew: () => void;
  onCancel: () => void;
  isOpen: boolean;
}

const CONFIDENCE_COLORS = {
  VERY_HIGH: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'bg-red-100 text-red-800' },
  HIGH: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', badge: 'bg-orange-100 text-orange-800' },
  MEDIUM: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', badge: 'bg-yellow-100 text-yellow-800' },
  LOW: { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', badge: 'bg-gray-100 text-gray-800' },
};

const CONFIDENCE_LABELS = {
  VERY_HIGH: 'Very High',
  HIGH: 'High',
  MEDIUM: 'Medium',
  LOW: 'Low',
};

export function DuplicateWarningModal({
  matches,
  onSelectExisting,
  onCreateNew,
  onCancel,
  isOpen,
}: DuplicateWarningModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Potential Duplicate Customers Found
                </h2>
                <p className="mt-1 text-sm text-gray-600">
                  We found {matches.length} similar customer{matches.length > 1 ? 's' : ''} that may already exist in the system.
                </p>
              </div>
              <button
                onClick={onCancel}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Matches List */}
          <div className="px-6 py-4 max-h-96 overflow-y-auto">
            <div className="space-y-3">
              {matches.map((match) => {
                const colors = CONFIDENCE_COLORS[match.confidence];
                return (
                  <div
                    key={match.customer.id}
                    className={`border rounded-lg p-4 ${colors.border} ${colors.bg} hover:shadow-md transition-shadow`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">{match.customer.name}</h3>
                          <span className={`px-2 py-0.5 text-xs font-medium rounded ${colors.badge}`}>
                            {CONFIDENCE_LABELS[match.confidence]} Match
                          </span>
                          <span className="text-xs text-gray-500">
                            ({Math.round(match.score * 100)}% similar)
                          </span>
                        </div>
                        {match.customer.legal_name && (
                          <p className="text-sm text-gray-600">Legal: {match.customer.legal_name}</p>
                        )}
                      </div>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mb-3">
                      {match.customer.usdot_number && (
                        <div>
                          <span className="text-gray-500">USDOT:</span>
                          <span className={`ml-2 font-medium ${match.match_details.usdot_match ? 'text-red-600' : 'text-gray-900'}`}>
                            {match.customer.usdot_number}
                            {match.match_details.usdot_match && ' ✓'}
                          </span>
                        </div>
                      )}
                      {match.customer.mc_number && (
                        <div>
                          <span className="text-gray-500">MC#:</span>
                          <span className={`ml-2 font-medium ${match.match_details.mc_match ? 'text-red-600' : 'text-gray-900'}`}>
                            {match.customer.mc_number}
                            {match.match_details.mc_match && ' ✓'}
                          </span>
                        </div>
                      )}
                      {(match.customer.city || match.customer.state) && (
                        <div className="col-span-2">
                          <span className="text-gray-500">Location:</span>
                          <span className="ml-2 text-gray-900">
                            {match.customer.city && `${match.customer.city}, `}
                            {match.customer.state}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Match Details (Expandable Info) */}
                    {match.match_details.selection_count > 0 && (
                      <div className="text-xs text-gray-500 mb-3">
                        <svg className="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        Used {match.match_details.selection_count} time{match.match_details.selection_count > 1 ? 's' : ''}
                      </div>
                    )}

                    {/* Action Button */}
                    <button
                      onClick={() => onSelectExisting(match.customer.id)}
                      className="w-full px-4 py-2 text-sm font-medium text-white rounded transition-colors"
                      style={{ backgroundColor: '#7ed321' }}
                    >
                      Use This Customer
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
            <div className="flex items-center justify-between">
              <button
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={onCreateNew}
                className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
                style={{ backgroundColor: '#7ed321' }}
              >
                Create New Customer Anyway
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              Creating a duplicate may cause confusion. Please verify before proceeding.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
