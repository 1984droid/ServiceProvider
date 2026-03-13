/**
 * ContactOverviewTab - Contact overview information
 */

import type { Contact } from '@/api/customers.api';
import { StatCard } from '@/components/ui/StatCard';
import { CorrespondenceIndicator } from '@/components/ui/CorrespondenceIndicator';

interface ContactOverviewTabProps {
  contact: Contact;
  onNavigateToCustomer: (customerId: string) => void;
  onDataRefreshed: () => void;
}

export function ContactOverviewTab({
  contact,
  onNavigateToCustomer,
}: ContactOverviewTabProps) {
  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Status"
          value={contact.is_active ? 'Active' : 'Inactive'}
          variant={contact.is_active ? 'success' : 'danger'}
        />
        <StatCard
          label="Contact Type"
          value={contact.is_automated ? 'Automated' : 'Person'}
          variant={contact.is_automated ? 'info' : 'default'}
        />
        <StatCard
          label="Primary Contact"
          value={contact.is_primary ? 'Yes' : 'No'}
          variant={contact.is_primary ? 'success' : 'default'}
        />
        <StatCard
          label="Portal Access"
          value="Not Configured"
          variant="default"
          subtitle="Coming soon"
        />
      </div>

      {/* Contact Information */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Contact Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">First Name</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{contact.first_name}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Last Name</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{contact.last_name}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Title</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{contact.title || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Email</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{contact.email || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Phone</dt>
            <dd className="mt-0.5 text-sm text-gray-900">
              {contact.phone || '—'}
              {contact.phone_extension && ` ext. ${contact.phone_extension}`}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Mobile</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{contact.mobile || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Correspondence Preferences */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Correspondence Preferences</h3>
        <div className="grid grid-cols-4 gap-3">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-xs text-gray-700">Invoices</span>
            {contact.receive_invoices ? (
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-xs text-gray-700">Estimates</span>
            {contact.receive_estimates ? (
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-xs text-gray-700">Updates</span>
            {contact.receive_service_updates ? (
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-xs text-gray-700">Reports</span>
            {contact.receive_inspection_reports ? (
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>
        </div>
      </div>

      {/* Customer Link */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Customer</h3>
        <button
          onClick={() => onNavigateToCustomer(contact.customer)}
          className="text-sm font-medium hover:underline"
          style={{ color: '#7ed321' }}
        >
          View Customer Details
        </button>
      </div>

      {/* Notes */}
      {contact.notes && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Notes</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{contact.notes}</p>
        </div>
      )}

      {/* Metadata */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Record Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Contact ID</dt>
            <dd className="mt-0.5 text-xs text-gray-900 font-mono">{contact.id}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Created</dt>
            <dd className="mt-0.5 text-xs text-gray-900">{formatDateTime(contact.created_at)}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Last Updated</dt>
            <dd className="mt-0.5 text-xs text-gray-900">{formatDateTime(contact.updated_at)}</dd>
          </div>
        </div>
      </div>
    </div>
  );
}
