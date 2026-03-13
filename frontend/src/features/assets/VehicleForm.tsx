/**
 * VehicleForm - Form for creating/editing vehicles
 *
 * Reusable form component for vehicle data entry
 */

import { useState, useEffect } from 'react';
import { customersApi } from '@/api/customers.api';
import type { Customer } from '@/api/customers.api';

export interface VehicleFormData {
  customer: string;
  vin: string;
  unit_number: string;
  year: number | null;
  make: string;
  model: string;
  vehicle_type: string;
  body_class: string;
  body_type: string;
  license_plate: string;
  odometer_miles: number | null;
  engine_hours: number | null;
  is_active: boolean;
  notes: string;
  capabilities: string[];
}

interface VehicleFormProps {
  initialData?: Partial<VehicleFormData>;
  onSubmit: (data: VehicleFormData) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitLabel?: string;
}

export function VehicleForm({
  initialData = {},
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitLabel = 'Create Vehicle',
}: VehicleFormProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [formData, setFormData] = useState<VehicleFormData>({
    customer: initialData.customer || '',
    vin: initialData.vin || '',
    unit_number: initialData.unit_number || '',
    year: initialData.year || null,
    make: initialData.make || '',
    model: initialData.model || '',
    vehicle_type: initialData.vehicle_type || '',
    body_class: initialData.body_class || '',
    body_type: initialData.body_type || '',
    license_plate: initialData.license_plate || '',
    odometer_miles: initialData.odometer_miles || null,
    engine_hours: initialData.engine_hours || null,
    is_active: initialData.is_active !== undefined ? initialData.is_active : true,
    notes: initialData.notes || '',
    capabilities: initialData.capabilities || [],
  });

  // Load customers on mount
  useEffect(() => {
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
    loadCustomers();
  }, []);

  const handleChange = (field: keyof VehicleFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Customer</h3>
        <select
          value={formData.customer}
          onChange={(e) => handleChange('customer', e.target.value)}
          disabled={loadingCustomers}
          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
          required
        >
          <option value="">
            {loadingCustomers ? 'Loading customers...' : 'Select a customer'}
          </option>
          {(customers || []).map(customer => (
            <option key={customer.id} value={customer.id}>
              {customer.name}
            </option>
          ))}
        </select>
      </div>

      {/* Vehicle Identification */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Vehicle Identification</h3>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              VIN <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.vin}
              onChange={(e) => handleChange('vin', e.target.value.toUpperCase())}
              placeholder="17-character VIN"
              maxLength={17}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono uppercase"
              required
              readOnly={!!initialData.vin}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Unit Number</label>
            <input
              type="text"
              value={formData.unit_number}
              onChange={(e) => handleChange('unit_number', e.target.value)}
              placeholder="e.g., UNIT-001"
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>
        </div>
      </div>

      {/* Vehicle Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Vehicle Details</h3>
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
              <input
                type="number"
                value={formData.year || ''}
                onChange={(e) => handleChange('year', e.target.value ? parseInt(e.target.value) : null)}
                placeholder="2024"
                min="1900"
                max="2100"
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Make</label>
              <input
                type="text"
                value={formData.make}
                onChange={(e) => handleChange('make', e.target.value)}
                placeholder="Freightliner"
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => handleChange('model', e.target.value)}
                placeholder="Cascadia"
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              />
            </div>
          </div>

          {/* VIN Decode Data (Read-only) */}
          {(formData.vehicle_type || formData.body_class) && (
            <div className="grid grid-cols-2 gap-3">
              {formData.vehicle_type && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Vehicle Type <span className="text-xs text-gray-500">(from VIN)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.vehicle_type}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-gray-50 text-gray-600"
                  />
                </div>
              )}
              {formData.body_class && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Body Class <span className="text-xs text-gray-500">(from VIN)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.body_class}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-gray-50 text-gray-600"
                  />
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Body Type</label>
            <select
              value={formData.body_type}
              onChange={(e) => handleChange('body_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="">None / As Delivered</option>
              <option value="SERVICE">Service Body</option>
              <option value="FLATBED">Flatbed</option>
              <option value="STAKE">Stake Body</option>
              <option value="DUMP">Dump Body</option>
              <option value="VAN">Van Body</option>
              <option value="BOX">Box/Cargo Body</option>
              <option value="REFUSE">Refuse Body</option>
              <option value="TANK">Tank Body</option>
              <option value="CRANE">Crane Body</option>
              <option value="TOW">Tow/Wrecker Body</option>
              <option value="UTILITY">Utility Body</option>
              <option value="OTHER">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">License Plate</label>
            <input
              type="text"
              value={formData.license_plate}
              onChange={(e) => handleChange('license_plate', e.target.value)}
              placeholder="ABC1234"
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>
        </div>
      </div>

      {/* Operational Data */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Operational Data</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Odometer (miles)</label>
            <input
              type="number"
              value={formData.odometer_miles || ''}
              onChange={(e) => handleChange('odometer_miles', e.target.value ? parseInt(e.target.value) : null)}
              placeholder="50000"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Engine Hours</label>
            <input
              type="number"
              value={formData.engine_hours || ''}
              onChange={(e) => handleChange('engine_hours', e.target.value ? parseInt(e.target.value) : null)}
              placeholder="5000"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>
        </div>
      </div>

      {/* Status & Notes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Status & Notes</h3>
        <div className="space-y-3">
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => handleChange('is_active', e.target.checked)}
                className="w-4 h-4 text-green-600 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              placeholder="Internal notes about this vehicle..."
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
          style={{ backgroundColor: '#7ed321' }}
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
}
