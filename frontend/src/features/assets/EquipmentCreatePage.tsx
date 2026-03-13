/**
 * EquipmentCreatePage
 *
 * Equipment creation page with form
 * Follows same pattern as VehicleCreatePage
 */

import { useState } from 'react';
import { EquipmentForm, type EquipmentFormData } from './EquipmentForm';
import { equipmentApi } from '@/api/assets.api';

interface EquipmentCreatePageProps {
  onSuccess?: (equipmentId: string) => void;
  onCancel?: () => void;
}

export function EquipmentCreatePage({ onSuccess, onCancel }: EquipmentCreatePageProps = {}) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (data: EquipmentFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const formDataWithDefaults = {
        ...data,
        photo: null,
        equipment_data: {},
      };
      const equipment = await equipmentApi.create(formDataWithDefaults);
      setSuccess(true);
      // Navigate to the equipment list after brief delay
      setTimeout(() => {
        if (onSuccess) {
          onSuccess(equipment.id);
        }
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to create equipment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6">
        <button
          onClick={handleCancel}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Assets
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Create Equipment</h1>
        <p className="mt-1 text-sm text-gray-600">
          Add new equipment to the system
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
              <p className="text-sm font-medium text-green-900">Equipment created successfully!</p>
              <p className="mt-1 text-sm text-green-800">Redirecting to equipment list...</p>
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
              <p className="text-sm font-medium text-red-900">Error creating equipment</p>
              <p className="mt-1 text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Form */}
      <div className="max-w-2xl mx-auto">
        <EquipmentForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
          submitLabel="Create Equipment"
        />
      </div>
    </div>
  );
}
