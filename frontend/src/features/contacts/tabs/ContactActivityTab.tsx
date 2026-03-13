/**
 * ContactActivityTab - Activity history for contact
 *
 * Placeholder for future activity tracking functionality.
 */

import type { Contact } from '@/api/customers.api';

interface ContactActivityTabProps {
  contact: Contact;
}

export function ContactActivityTab({ contact }: ContactActivityTabProps) {
  return (
    <div className="space-y-4">
      {/* Coming Soon */}
      <div className="border border-gray-200 rounded-lg p-6">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-900">Activity History Coming Soon</h3>
          <p className="mt-2 text-sm text-gray-500 max-w-md mx-auto">
            This tab will show activity history for this contact, including portal logins, email communications,
            document views, and other interactions with your service provider system.
          </p>
        </div>
      </div>

      {/* Planned Activity Types */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Activity Types</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="border border-gray-200 rounded p-3">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Portal Logins</span>
            </div>
            <p className="text-xs text-gray-600">Track portal access history</p>
          </div>
          <div className="border border-gray-200 rounded p-3">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Email Communications</span>
            </div>
            <p className="text-xs text-gray-600">Invoices, estimates, updates sent</p>
          </div>
          <div className="border border-gray-200 rounded p-3">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Document Views</span>
            </div>
            <p className="text-xs text-gray-600">Documents viewed via portal</p>
          </div>
          <div className="border border-gray-200 rounded p-3">
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              <span className="text-sm font-medium text-gray-900">Record Changes</span>
            </div>
            <p className="text-xs text-gray-600">Updates to contact information</p>
          </div>
        </div>
      </div>
    </div>
  );
}
