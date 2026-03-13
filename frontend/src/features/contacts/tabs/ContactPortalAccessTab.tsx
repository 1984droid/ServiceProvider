/**
 * ContactPortalAccessTab - Manage portal access for contact
 *
 * This tab will be used to configure customer portal access at the contact level.
 * Currently a placeholder for future functionality.
 */

import type { Contact } from '@/api/customers.api';

interface ContactPortalAccessTabProps {
  contact: Contact;
  onDataRefreshed: () => void;
}

export function ContactPortalAccessTab({ contact }: ContactPortalAccessTabProps) {
  return (
    <div className="space-y-4">
      {/* Coming Soon Banner */}
      <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
        <div className="flex items-start gap-4">
          <svg className="w-8 h-8 text-blue-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-lg font-semibold text-blue-900">Customer Portal Access Coming Soon</h3>
            <p className="mt-2 text-sm text-blue-800">
              Portal access will be configured at the contact level, allowing each contact to have their own login credentials
              and access permissions to view their customer's information, service history, invoices, and more.
            </p>
          </div>
        </div>
      </div>

      {/* Planned Features */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Planned Features</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center mt-0.5">
              <span className="text-xs text-gray-600">1</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Portal Account Creation</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Create and manage portal login credentials for this contact
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center mt-0.5">
              <span className="text-xs text-gray-600">2</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Access Permissions</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Configure what information and features this contact can access
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center mt-0.5">
              <span className="text-xs text-gray-600">3</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Login History</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Track when and from where this contact has logged into the portal
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center mt-0.5">
              <span className="text-xs text-gray-600">4</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Notification Preferences</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Configure portal-specific notification preferences
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center mt-0.5">
              <span className="text-xs text-gray-600">5</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Two-Factor Authentication</p>
              <p className="text-xs text-gray-600 mt-0.5">
                Enable additional security for portal access
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Current Contact Info */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Contact Email</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-900">{contact.email || 'No email address'}</p>
            <p className="text-xs text-gray-500 mt-0.5">
              {contact.email ? 'This email will be used for portal access' : 'Email required for portal access'}
            </p>
          </div>
          {!contact.email && (
            <span className="px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-800">
              Email Required
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
