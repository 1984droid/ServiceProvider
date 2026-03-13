/**
 * CustomerCreatePage
 *
 * Two-step customer creation process:
 * 1. USDOT/MC lookup (optional)
 * 2. Customer form (pre-populated from USDOT data if found)
 *
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useState } from 'react';
import { CustomerForm } from './CustomerForm';
import { USDOTSearch } from './USDOTSearch';
import { customersApi, type CustomerCreateData } from '@/api/customers.api';
import { type USDOTProfile } from '@/api/usdot.api';

type Step = 'lookup' | 'form';

interface CustomerCreatePageProps {
  onSuccess: () => void;
}

export function CustomerCreatePage({ onSuccess }: CustomerCreatePageProps) {
  const [step, setStep] = useState<Step>('lookup');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [initialData, setInitialData] = useState<Partial<CustomerCreateData>>({});

  const handleProfileFound = (profile: USDOTProfile) => {
    // Map USDOT profile data to customer form data
    setInitialData({
      name: profile.dba_name || profile.legal_name,
      legal_name: profile.legal_name,
      address_line1: profile.physical_address,
      city: profile.physical_city,
      state: profile.physical_state,
      postal_code: profile.physical_zip,
      usdot_number: profile.usdot_number,
      mc_number: profile.mc_number,
    });
    setStep('form');
  };

  const handleManualEntry = () => {
    setInitialData({});
    setStep('form');
  };

  const handleSubmit = async (data: CustomerCreateData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      await customersApi.create(data);
      setSuccess(true);
      // Navigate back to customer list after 2 seconds
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create customer');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
          Create Customer
        </h1>
        <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
          {step === 'lookup'
            ? 'Search for existing FMCSA data or enter manually'
            : 'Enter customer information'}
        </p>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold"
            style={{
              backgroundColor: step === 'lookup' ? '#7ed321' : '#e5e7eb',
              color: step === 'lookup' ? 'white' : '#6b7280'
            }}
          >
            1
          </div>
          <span className="text-sm font-medium" style={{ color: step === 'lookup' ? '#111827' : '#6b7280' }}>
            USDOT Lookup
          </span>
        </div>
        <div style={{ width: '50px', height: '2px', backgroundColor: '#e5e7eb' }} />
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold"
            style={{
              backgroundColor: step === 'form' ? '#7ed321' : '#e5e7eb',
              color: step === 'form' ? 'white' : '#6b7280'
            }}
          >
            2
          </div>
          <span className="text-sm font-medium" style={{ color: step === 'form' ? '#111827' : '#6b7280' }}>
            Customer Details
          </span>
        </div>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
          <p className="font-medium" style={{ color: '#15803d' }}>
            Customer created successfully!
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="font-medium" style={{ color: '#dc2626' }}>
            {error}
          </p>
        </div>
      )}

      {/* Content Card */}
      <div className="bg-white rounded-lg shadow-sm p-6" style={{ maxWidth: '800px' }}>
        {step === 'lookup' && (
          <USDOTSearch
            onProfileFound={handleProfileFound}
            onManualEntry={handleManualEntry}
          />
        )}

        {step === 'form' && (
          <div>
            {/* Back button */}
            <button
              onClick={() => setStep('lookup')}
              className="mb-4 text-xs font-medium hover:underline flex items-center gap-1"
              style={{ color: '#6b7280' }}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to USDOT Lookup
            </button>

            <CustomerForm
              onSubmit={handleSubmit}
              isSubmitting={isSubmitting}
              initialData={initialData}
            />
          </div>
        )}
      </div>
    </div>
  );
}
