/**
 * EquipmentForm - Form for creating/editing equipment
 *
 * Reusable form component for equipment data entry
 * Follows same pattern as VehicleForm
 */

import { useState, useEffect } from 'react';
import { customersApi } from '@/api/customers.api';
import { vehiclesApi } from '@/api/assets.api';
import type { Customer } from '@/api/customers.api';
import type { Vehicle } from '@/api/assets.api';
import { FormField } from '@/components/molecules/FormField';
import { TextInput } from '@/components/atoms/TextInput';
import { Select } from '@/components/atoms/Select';
import { TextArea } from '@/components/atoms/TextArea';

export interface EquipmentFormData {
  customer: string;
  serial_number: string;
  asset_number: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  year: number | null;
  engine_hours: number | null;
  cycles: number | null;
  mounted_on_vehicle: string;
  is_active: boolean;
  notes: string;
  capabilities: string[];
}

interface EquipmentFormProps {
  initialData?: Partial<EquipmentFormData>;
  onSubmit: (data: EquipmentFormData) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitLabel?: string;
}

const EQUIPMENT_TYPE_CHOICES = [
  { value: '', label: 'Not Specified' },
  { value: 'A92_2_AERIAL', label: 'Aerial Device (ANSI A92.2)' },
  { value: 'A92_20_SCISSOR', label: 'Scissor Lift (ANSI A92.20)' },
  { value: 'A92_20_BOOM', label: 'Boom Lift (ANSI A92.20)' },
  { value: 'A92_3_VERTICAL', label: 'Vertical Mast Lift (ANSI A92.3)' },
  { value: 'B30_5_CRANE', label: 'Mobile Crane (ANSI/ASME B30.5)' },
  { value: 'B30_22_ARTICULATING', label: 'Articulating Boom Crane (B30.22)' },
  { value: 'DIGGER_DERRICK', label: 'Digger Derrick' },
  { value: 'FORKLIFT', label: 'Forklift' },
  { value: 'GENERATOR', label: 'Generator' },
  { value: 'COMPRESSOR', label: 'Air Compressor' },
  { value: 'WELDER', label: 'Welder' },
  { value: 'CRANE_BOOM_TRUCK', label: 'Crane/Boom Truck' },
];

const CAPABILITY_OPTIONS = [
  'AERIAL_DEVICE',
  'INSULATING_SYSTEM',
  'BARE_HAND_WORK_UNIT',
  'ARTICULATING_BOOM',
  'TELESCOPING_BOOM',
  'VERTICAL_TOWER',
  'EXTENSIBLE_BOOM',
  'PLATFORM_ROTATION',
  'JIB',
];

export function EquipmentForm({
  initialData = {},
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitLabel = 'Create Equipment',
}: EquipmentFormProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [loadingVehicles, setLoadingVehicles] = useState(true);
  const [formData, setFormData] = useState<EquipmentFormData>({
    customer: initialData.customer || '',
    serial_number: initialData.serial_number || '',
    asset_number: initialData.asset_number || '',
    equipment_type: initialData.equipment_type || '',
    manufacturer: initialData.manufacturer || '',
    model: initialData.model || '',
    year: initialData.year || null,
    engine_hours: initialData.engine_hours || null,
    cycles: initialData.cycles || null,
    mounted_on_vehicle: initialData.mounted_on_vehicle || '',
    is_active: initialData.is_active ?? true,
    notes: initialData.notes || '',
    capabilities: initialData.capabilities || [],
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadCustomers();
    loadVehicles();
  }, []);

  const loadCustomers = async () => {
    try {
      const data = await customersApi.list();
      setCustomers(data);
    } catch (err) {
      console.error('Failed to load customers:', err);
    } finally {
      setLoadingCustomers(false);
    }
  };

  const loadVehicles = async () => {
    try {
      const data = await vehiclesApi.list();
      setVehicles(data);
    } catch (err) {
      console.error('Failed to load vehicles:', err);
    } finally {
      setLoadingVehicles(false);
    }
  };

  const handleChange = (field: keyof EquipmentFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleCapabilityToggle = (capability: string) => {
    const capabilities = formData.capabilities.includes(capability)
      ? formData.capabilities.filter((c) => c !== capability)
      : [...formData.capabilities, capability];
    handleChange('capabilities', capabilities);
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customer) {
      newErrors.customer = 'Customer is required';
    }

    if (!formData.serial_number.trim()) {
      newErrors.serial_number = 'Serial number is required';
    }

    if (formData.year !== null && (formData.year < 1900 || formData.year > 2100)) {
      newErrors.year = 'Year must be between 1900 and 2100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const customerOptions = [
    { value: '', label: loadingCustomers ? 'Loading...' : 'Select a customer...' },
    ...customers.map((c) => ({ value: c.id, label: c.name })),
  ];

  const vehicleOptions = [
    { value: '', label: loadingVehicles ? 'Loading...' : 'Not mounted / Standalone' },
    ...vehicles.map((v) => ({
      value: v.id,
      label: `${v.unit_number} - ${v.year} ${v.make} ${v.model}`,
    })),
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-1">
      {/* Customer */}
      <FormField label="Customer" required error={errors.customer} htmlFor="customer">
        <Select
          id="customer"
          value={formData.customer}
          onChange={(e) => handleChange('customer', e.target.value)}
          disabled={loadingCustomers || isSubmitting}
          error={!!errors.customer}
          options={customerOptions}
        />
      </FormField>

      {/* Serial Number & Asset Number */}
      <div className="grid grid-cols-2 gap-4">
        <FormField label="Serial Number" required error={errors.serial_number} htmlFor="serial_number">
          <TextInput
            id="serial_number"
            value={formData.serial_number}
            onChange={(e) => handleChange('serial_number', e.target.value)}
            disabled={isSubmitting}
            error={!!errors.serial_number}
          />
        </FormField>

        <FormField label="Asset Number" htmlFor="asset_number">
          <TextInput
            id="asset_number"
            value={formData.asset_number}
            onChange={(e) => handleChange('asset_number', e.target.value)}
            disabled={isSubmitting}
          />
        </FormField>
      </div>

      {/* Equipment Type */}
      <FormField label="Equipment Type" htmlFor="equipment_type">
        <Select
          id="equipment_type"
          value={formData.equipment_type}
          onChange={(e) => handleChange('equipment_type', e.target.value)}
          disabled={isSubmitting}
          options={EQUIPMENT_TYPE_CHOICES}
        />
      </FormField>

      {/* Manufacturer, Model, Year */}
      <div className="grid grid-cols-3 gap-4">
        <FormField label="Manufacturer" htmlFor="manufacturer">
          <TextInput
            id="manufacturer"
            value={formData.manufacturer}
            onChange={(e) => handleChange('manufacturer', e.target.value)}
            disabled={isSubmitting}
          />
        </FormField>

        <FormField label="Model" htmlFor="model">
          <TextInput
            id="model"
            value={formData.model}
            onChange={(e) => handleChange('model', e.target.value)}
            disabled={isSubmitting}
          />
        </FormField>

        <FormField label="Year" error={errors.year} htmlFor="year">
          <TextInput
            id="year"
            type="number"
            value={formData.year?.toString() || ''}
            onChange={(e) => handleChange('year', e.target.value ? Number(e.target.value) : null)}
            disabled={isSubmitting}
            error={!!errors.year}
            min="1900"
            max="2100"
          />
        </FormField>
      </div>

      {/* Engine Hours & Cycles */}
      <div className="grid grid-cols-2 gap-4">
        <FormField label="Engine Hours" htmlFor="engine_hours">
          <TextInput
            id="engine_hours"
            type="number"
            value={formData.engine_hours?.toString() || ''}
            onChange={(e) => handleChange('engine_hours', e.target.value ? Number(e.target.value) : null)}
            disabled={isSubmitting}
            min="0"
          />
        </FormField>

        <FormField label="Cycles" htmlFor="cycles">
          <TextInput
            id="cycles"
            type="number"
            value={formData.cycles?.toString() || ''}
            onChange={(e) => handleChange('cycles', e.target.value ? Number(e.target.value) : null)}
            disabled={isSubmitting}
            min="0"
          />
        </FormField>
      </div>

      {/* Mounted On Vehicle */}
      <FormField label="Mounted On Vehicle" htmlFor="mounted_on_vehicle">
        <Select
          id="mounted_on_vehicle"
          value={formData.mounted_on_vehicle}
          onChange={(e) => handleChange('mounted_on_vehicle', e.target.value)}
          disabled={loadingVehicles || isSubmitting}
          options={vehicleOptions}
        />
      </FormField>

      {/* Capabilities */}
      <FormField label="Capabilities">
        <div className="grid grid-cols-3 gap-3">
          {CAPABILITY_OPTIONS.map((capability) => (
            <label key={capability} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.capabilities.includes(capability)}
                onChange={() => handleCapabilityToggle(capability)}
                disabled={isSubmitting}
                className="rounded"
                style={{ accentColor: '#7ed321' }}
              />
              <span style={{ color: '#374151' }}>{capability.replace(/_/g, ' ')}</span>
            </label>
          ))}
        </div>
      </FormField>

      {/* Active Status */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => handleChange('is_active', e.target.checked)}
          disabled={isSubmitting}
          className="rounded"
          style={{ accentColor: '#7ed321' }}
        />
        <label htmlFor="is_active" className="text-sm font-semibold" style={{ color: '#111827' }}>
          Active
        </label>
      </div>

      {/* Notes */}
      <FormField label="Notes" htmlFor="notes">
        <TextArea
          id="notes"
          value={formData.notes}
          onChange={(e) => handleChange('notes', e.target.value)}
          disabled={isSubmitting}
          rows={4}
        />
      </FormField>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 rounded-lg font-medium transition-colors"
          style={{
            backgroundColor: 'white',
            color: '#374151',
            border: '1px solid #d1d5db',
          }}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 rounded-lg font-medium text-white transition-colors"
          style={{
            backgroundColor: '#7ed321',
            opacity: isSubmitting ? 0.5 : 1,
          }}
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
}
