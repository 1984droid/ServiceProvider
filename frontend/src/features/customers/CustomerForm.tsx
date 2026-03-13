/**
 * CustomerForm Organism
 *
 * Complete customer creation/edit form with validation.
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useState, FormEvent } from 'react';
import { TextInput } from '@/components/atoms/TextInput';
import { TextArea } from '@/components/atoms/TextArea';
import { Select } from '@/components/atoms/Select';
import { FormField } from '@/components/molecules/FormField';
import { type CustomerCreateData } from '@/api/customers.api';

interface CustomerFormProps {
  onSubmit: (data: CustomerCreateData) => void | Promise<void>;
  isSubmitting?: boolean;
  initialData?: Partial<CustomerCreateData>;
}

const US_STATES = [
  { value: '', label: 'Select State' },
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' },
];

export function CustomerForm({ onSubmit, isSubmitting = false, initialData = {} }: CustomerFormProps) {
  const [formData, setFormData] = useState<CustomerCreateData>({
    name: initialData.name || '',
    legal_name: initialData.legal_name || '',
    address_line1: initialData.address_line1 || '',
    address_line2: initialData.address_line2 || '',
    city: initialData.city || '',
    state: initialData.state || '',
    postal_code: initialData.postal_code || '',
    country: initialData.country || 'US',
    usdot_number: initialData.usdot_number || '',
    mc_number: initialData.mc_number || '',
    notes: initialData.notes || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Business name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    await onSubmit(formData);
  };

  const handleChange = (field: keyof CustomerCreateData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Business Information */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4" style={{ color: '#111827' }}>
          Business Information
        </h3>
        <div className="grid grid-cols-2 gap-6">
          <FormField label="Business Name" required error={errors.name} htmlFor="name">
            <TextInput
              id="name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              error={!!errors.name}
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="Legal Name" htmlFor="legal_name">
            <TextInput
              id="legal_name"
              value={formData.legal_name}
              onChange={(e) => handleChange('legal_name', e.target.value)}
              disabled={isSubmitting}
            />
          </FormField>
        </div>
      </div>

      {/* Address */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4" style={{ color: '#111827' }}>
          Address
        </h3>
        <div className="space-y-5">
          <FormField label="Address Line 1" htmlFor="address_line1">
            <TextInput
              id="address_line1"
              value={formData.address_line1}
              onChange={(e) => handleChange('address_line1', e.target.value)}
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="Address Line 2" htmlFor="address_line2">
            <TextInput
              id="address_line2"
              value={formData.address_line2}
              onChange={(e) => handleChange('address_line2', e.target.value)}
              disabled={isSubmitting}
            />
          </FormField>

          <div className="grid grid-cols-3 gap-6">
            <FormField label="City" htmlFor="city">
              <TextInput
                id="city"
                value={formData.city}
                onChange={(e) => handleChange('city', e.target.value)}
                disabled={isSubmitting}
              />
            </FormField>

            <FormField label="State" htmlFor="state">
              <Select
                id="state"
                value={formData.state}
                onChange={(e) => handleChange('state', e.target.value)}
                options={US_STATES}
                disabled={isSubmitting}
              />
            </FormField>

            <FormField label="Postal Code" htmlFor="postal_code">
              <TextInput
                id="postal_code"
                value={formData.postal_code}
                onChange={(e) => handleChange('postal_code', e.target.value)}
                disabled={isSubmitting}
              />
            </FormField>
          </div>
        </div>
      </div>

      {/* Regulatory */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4" style={{ color: '#111827' }}>
          Regulatory Information
        </h3>
        <div className="grid grid-cols-2 gap-6">
          <FormField label="USDOT Number" htmlFor="usdot_number">
            <TextInput
              id="usdot_number"
              value={formData.usdot_number}
              onChange={(e) => handleChange('usdot_number', e.target.value)}
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="MC Number" htmlFor="mc_number">
            <TextInput
              id="mc_number"
              value={formData.mc_number}
              onChange={(e) => handleChange('mc_number', e.target.value)}
              disabled={isSubmitting}
            />
          </FormField>
        </div>
      </div>

      {/* Notes */}
      <div className="mb-8">
        <FormField label="Internal Notes" htmlFor="notes">
          <TextArea
            id="notes"
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            disabled={isSubmitting}
          />
        </FormField>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-4">
        <button
          type="button"
          className="px-6 py-2 rounded-lg border font-medium"
          style={{
            borderColor: '#d1d5db',
            color: '#374151',
          }}
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-6 py-2 rounded-lg font-medium text-white"
          style={{
            backgroundColor: isSubmitting ? '#9ca3af' : '#7ed321',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
          }}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Customer'}
        </button>
      </div>
    </form>
  );
}
