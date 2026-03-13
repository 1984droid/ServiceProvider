/**
 * CustomerUSDOTTab - FMCSA carrier lookup data
 *
 * Shows:
 * - USDOT/MC numbers
 * - Business information from FMCSA
 * - Address information
 * - Safety data
 * - Operational data
 */

import { useState } from 'react';
import type { CustomerDetail } from '@/api/customers.api';
import { usdotApi } from '@/api/usdot.api';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { InfoSection } from '@/components/ui/InfoSection';
import { Badge } from '@/components/ui/Badge';

interface CustomerUSDOTTabProps {
  customer: CustomerDetail;
  onDataRefreshed?: () => void;
}

export function CustomerUSDOTTab({ customer, onDataRefreshed }: CustomerUSDOTTabProps) {
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const profile = customer.usdot_profile;

  const handleLookup = async (forceRefresh: boolean = false) => {
    if (!customer.usdot_number) {
      setLookupError('Customer does not have a USDOT number');
      return;
    }

    setIsLookingUp(true);
    setLookupError(null);

    try {
      await usdotApi.lookupByUSDOT(customer.usdot_number, forceRefresh, customer.id);
      // Trigger parent to reload customer data to get the updated profile
      if (onDataRefreshed) {
        onDataRefreshed();
      }
    } catch (err: any) {
      setLookupError(err.response?.data?.error || err.message || 'Failed to lookup USDOT data');
    } finally {
      setIsLookingUp(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSafetyRatingVariant = (rating: string): 'success' | 'warning' | 'danger' | 'default' => {
    if (!rating) return 'default';
    const lower = rating.toLowerCase();
    if (lower.includes('satisfactory')) return 'success';
    if (lower.includes('conditional')) return 'warning';
    if (lower.includes('unsatisfactory')) return 'danger';
    return 'default';
  };

  if (!profile) {
    return (
      <div className="space-y-4">
        <div className="border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-4 text-lg font-semibold text-gray-900">USDOT Data Not Retrieved</h3>
            <p className="mt-2 text-sm text-gray-500">
              {customer.usdot_number
                ? 'Click below to retrieve FMCSA carrier data for this USDOT number.'
                : 'This customer does not have a USDOT number assigned.'}
            </p>
            {customer.usdot_number && (
              <div className="mt-6">
                <button
                  onClick={handleLookup}
                  disabled={isLookingUp}
                  className="px-6 py-2.5 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
                  style={{ backgroundColor: '#7ed321' }}
                >
                  {isLookingUp ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Looking up USDOT...
                    </span>
                  ) : (
                    `Lookup USDOT ${customer.usdot_number}`
                  )}
                </button>
              </div>
            )}
            {lookupError && (
              <div className="mt-4 p-3 rounded bg-red-50 border border-red-200">
                <p className="text-sm text-red-600">{lookupError}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Lookup Status Banner */}
      <div className="border border-gray-200 rounded-lg p-4 bg-green-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-gray-900">FMCSA Data Retrieved</p>
              <p className="text-xs text-gray-600">Last updated: {formatDateTime(profile.lookup_date)}</p>
            </div>
          </div>
          <button
            onClick={() => handleLookup(true)}
            disabled={isLookingUp}
            className="px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {isLookingUp ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
        {lookupError && (
          <div className="mt-3 p-2 rounded bg-red-50 border border-red-200">
            <p className="text-xs text-red-600">{lookupError}</p>
          </div>
        )}
      </div>

      {/* FMCSA Identifiers */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">FMCSA Identifiers</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">USDOT Number</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.usdot_number || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">MC Number</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.mc_number || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Entity Type</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.entity_type || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Carrier Operation</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.carrier_operation || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Business Information */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Business Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Legal Name</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.legal_name || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">DBA Name</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.dba_name || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Phone</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.phone || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Email</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{profile.email || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Addresses */}
      <div className="grid grid-cols-2 gap-3">
        {/* Physical Address */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Physical Address</h3>
          <div className="space-y-2">
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Address</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{profile.physical_address || '—'}</dd>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">City</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.physical_city || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">State</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.physical_state || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">Zip</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.physical_zip || '—'}</dd>
              </div>
            </div>
          </div>
        </div>

        {/* Mailing Address */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Mailing Address</h3>
          <div className="space-y-2">
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Address</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{profile.mailing_address || '—'}</dd>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">City</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.mailing_city || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">State</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.mailing_state || '—'}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase">Zip</dt>
                <dd className="mt-0.5 text-sm text-gray-900">{profile.mailing_zip || '—'}</dd>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Safety & Operational Data */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Safety & Operational Data</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Safety Rating</dt>
            <dd className="mt-1">
              {profile.safety_rating ? (
                <Badge
                  label={profile.safety_rating}
                  variant={getSafetyRatingVariant(profile.safety_rating)}
                  size="md"
                />
              ) : (
                <span className="text-sm text-gray-400 italic">Not rated</span>
              )}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Total Power Units</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {profile.total_power_units !== null ? profile.total_power_units : '—'}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Total Drivers</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {profile.total_drivers !== null ? profile.total_drivers : '—'}
            </dd>
          </div>
        </div>

        {profile.out_of_service_date && (
          <div className="mt-3 p-3 rounded bg-red-50 border border-red-200">
            <p className="text-xs font-medium text-red-900">
              Out of Service: {formatDate(profile.out_of_service_date)}
            </p>
          </div>
        )}
      </div>

      {/* Operational Classification */}
      {profile.operation_classification && profile.operation_classification.length > 0 && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Operation Classification</h3>
          <div className="flex flex-wrap gap-2">
            {profile.operation_classification.map((classification, index) => (
              <Badge key={index} label={classification} variant="info" size="md" />
            ))}
          </div>
        </div>
      )}

      {/* Cargo Carried */}
      {profile.cargo_carried && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Cargo Carried</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{profile.cargo_carried}</p>
        </div>
      )}
    </div>
  );
}
