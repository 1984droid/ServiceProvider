/**
 * VehicleCreatePage
 *
 * Two-step vehicle creation process:
 * 1. VIN lookup (optional)
 * 2. Vehicle form (pre-populated from VIN decode if found)
 *
 * Follows same pattern as CustomerCreatePage
 */

import { useState } from 'react';
import { VehicleForm, type VehicleFormData } from './VehicleForm';
import { VINSearch } from './VINSearch';
import { vehiclesApi } from '@/api/assets.api';
import { type VINDecodeResult } from '@/api/vin.api';

type Step = 'lookup' | 'form';

interface VehicleCreatePageProps {
  onSuccess: (vehicleId: string) => void;
  onCancel: () => void;
}

export function VehicleCreatePage({ onSuccess, onCancel }: VehicleCreatePageProps) {
  const [step, setStep] = useState<Step>('lookup');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [initialData, setInitialData] = useState<Partial<VehicleFormData>>({});

  const handleVINFound = (data: VINDecodeResult) => {
    // Map VIN decode data to vehicle form data
    setInitialData({
      vin: data.vin,
      year: data.model_year,
      make: data.make,
      model: data.model,
      vehicle_type: data.vehicle_type,
      body_class: data.body_class,
    });
    setStep('form');
  };

  const handleSkipLookup = () => {
    setInitialData({});
    setStep('form');
  };

  const handleSubmit = async (data: VehicleFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const vehicle = await vehiclesApi.create(data);
      setSuccess(true);
      // Navigate to the new vehicle after brief delay
      setTimeout(() => {
        onSuccess(vehicle.id);
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to create vehicle');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (step === 'form' && !success) {
      // Go back to lookup step
      setStep('lookup');
      setInitialData({});
    } else {
      // Go back to assets list
      onCancel();
    }
  };

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6">
        <button
          onClick={onCancel}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Assets
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Create Vehicle</h1>
        <p className="mt-1 text-sm text-gray-600">
          {step === 'lookup'
            ? 'Look up vehicle information by VIN or enter manually'
            : 'Complete vehicle information'}
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded">
          <div className="flex gap-3">
            <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <div>
              <p className="text-sm font-medium text-green-900">Vehicle created successfully!</p>
              <p className="mt-1 text-sm text-green-800">Redirecting to vehicle details...</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded">
          <div className="flex gap-3">
            <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-900">Error creating vehicle</p>
              <p className="mt-1 text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Step Content */}
      {step === 'lookup' && (
        <VINSearch
          onVINFound={handleVINFound}
          onSkip={handleSkipLookup}
        />
      )}

      {step === 'form' && (
        <div className="max-w-2xl mx-auto">
          <VehicleForm
            initialData={initialData}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isSubmitting={isSubmitting}
            submitLabel="Create Vehicle"
          />
        </div>
      )}
    </div>
  );
}
