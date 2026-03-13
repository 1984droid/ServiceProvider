/**
 * CustomerOverviewTab - Overview of customer information
 *
 * Shows:
 * - Key stats (contacts, assets, inspections)
 * - Company information
 * - Primary contact
 * - Recent activity
 */

import type { CustomerDetail } from '@/api/customers.api';
import type { Vehicle, Equipment } from '@/api/assets.api';
import { StatCard } from '@/components/ui/StatCard';
import { InfoSection } from '@/components/ui/InfoSection';
import { SectionHeader } from '@/components/ui/SectionHeader';

interface CustomerOverviewTabProps {
  customer: CustomerDetail;
  vehicles: Vehicle[];
  equipment: Equipment[];
}

export function CustomerOverviewTab({ customer, vehicles, equipment }: CustomerOverviewTabProps) {
  const activeVehicles = vehicles.filter(v => v.is_active).length;
  const activeEquipment = equipment.filter(e => e.is_active).length;

  const primaryContact = customer.contacts.find(c => c.is_primary);

  return (
    <div className="space-y-4">
      {/* Stats Grid - More compact */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Contacts"
          value={customer.contacts.length}
          subtitle={`${customer.contacts.filter(c => c.is_active).length} active`}
          variant="default"
        />
        <StatCard
          label="Vehicles"
          value={vehicles.length}
          subtitle={`${activeVehicles} active`}
          variant="info"
        />
        <StatCard
          label="Equipment"
          value={equipment.length}
          subtitle={`${activeEquipment} active`}
          variant="info"
        />
        <StatCard
          label="Status"
          value={customer.is_active ? 'Active' : 'Inactive'}
          variant={customer.is_active ? 'success' : 'danger'}
        />
      </div>

      {/* Company Information with Logo */}
      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex gap-4">
          {/* Logo Placeholder */}
          <div className="flex-shrink-0">
            <div
              className="flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
              style={{ width: '120px', height: '120px' }}
            >
              <div className="text-center">
                <svg className="w-8 h-8 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-xs text-gray-500 mt-1">Logo</p>
              </div>
            </div>
          </div>

          {/* Company Details - More compact */}
          <div className="flex-1 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">Business Name</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{customer.name || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">Legal Name</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{customer.legal_name || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">USDOT Number</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{customer.usdot_number || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">MC Number</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{customer.mc_number || '—'}</dd>
              </div>
            </div>

            {/* Address on one line */}
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Address</dt>
              <dd className="mt-0.5 text-sm text-gray-900">
                {[
                  customer.address_line1,
                  customer.address_line2,
                  customer.city,
                  customer.state,
                  customer.postal_code,
                  customer.country
                ].filter(Boolean).join(', ') || '—'}
              </dd>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Contact - More compact */}
      {primaryContact && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Primary Contact</h3>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Name</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{primaryContact.full_name}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Title</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{primaryContact.title || '—'}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Email</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{primaryContact.email || '—'}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Phone</dt>
              <dd className="mt-0.5 text-sm text-gray-900">
                {primaryContact.phone || '—'}
                {primaryContact.phone_extension && ` ext. ${primaryContact.phone_extension}`}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Mobile</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{primaryContact.mobile || '—'}</dd>
            </div>
          </div>
        </div>
      )}

      {/* Notes - More compact */}
      {customer.notes && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Internal Notes</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{customer.notes}</p>
        </div>
      )}
    </div>
  );
}
