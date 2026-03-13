/**
 * EquipmentOverviewTab - Overview information for equipment
 */

import type { Equipment, Vehicle } from '@/api/assets.api';
import type { Customer } from '@/api/customers.api';
import { StatCard } from '@/components/ui/StatCard';

interface EquipmentOverviewTabProps {
  equipment: Equipment;
  mountedVehicle: Vehicle | null;
  customer: Customer | null;
  onNavigateToVehicle: (vehicleId: string) => void;
  onNavigateToCustomer: (customerId: string) => void;
}

export function EquipmentOverviewTab({
  equipment,
  mountedVehicle,
  customer,
  onNavigateToVehicle,
  onNavigateToCustomer,
}: EquipmentOverviewTabProps) {
  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Mounted Status"
          value={mountedVehicle ? 'Mounted' : 'Not Mounted'}
          variant={mountedVehicle ? 'info' : 'default'}
        />
        <StatCard
          label="Equipment Type"
          value={equipment.equipment_type || '—'}
          variant="default"
        />
        <StatCard
          label="Engine Hours"
          value={equipment.engine_hours !== null && equipment.engine_hours !== undefined
            ? `${equipment.engine_hours.toLocaleString()}`
            : '—'}
          subtitle="hours"
          variant="default"
        />
        <StatCard
          label="Status"
          value={equipment.is_active ? 'Active' : 'Inactive'}
          variant={equipment.is_active ? 'success' : 'danger'}
        />
      </div>

      {/* Equipment Details */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Equipment Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Serial Number</dt>
            <dd className="mt-0.5 text-sm text-gray-900 font-mono">{equipment.serial_number}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Asset Number</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{equipment.asset_number || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Equipment Type</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{equipment.equipment_type || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Manufacturer</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{equipment.manufacturer || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Model</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{equipment.model || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Year</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{equipment.year || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Customer</dt>
            <dd className="mt-0.5">
              <button
                onClick={() => customer && onNavigateToCustomer(customer.id)}
                className="text-sm font-medium hover:underline"
                style={{ color: '#7ed321' }}
              >
                {customer?.name || 'View Customer'}
              </button>
            </dd>
          </div>
        </div>
      </div>

      {/* Mounted Vehicle */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide">
            Mounted Vehicle
          </h3>
        </div>
        {!mountedVehicle ? (
          <div className="p-8 text-center">
            <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2 text-sm text-gray-500">Not mounted on any vehicle</p>
          </div>
        ) : (
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="grid grid-cols-4 gap-3">
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">Unit Number</dt>
                    <dd className="mt-0.5 text-sm text-gray-900 font-medium">
                      {mountedVehicle.unit_number || mountedVehicle.vin.substring(0, 12)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">VIN</dt>
                    <dd className="mt-0.5 text-sm text-gray-900 font-mono">{mountedVehicle.vin}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">Vehicle</dt>
                    <dd className="mt-0.5 text-sm text-gray-900">
                      {mountedVehicle.year && mountedVehicle.make && mountedVehicle.model
                        ? `${mountedVehicle.year} ${mountedVehicle.make} ${mountedVehicle.model}`
                        : '—'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">Status</dt>
                    <dd className="mt-0.5">
                      <span
                        className="px-2 py-0.5 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: mountedVehicle.is_active ? '#dcfce7' : '#fee2e2',
                          color: mountedVehicle.is_active ? '#166534' : '#991b1b',
                        }}
                      >
                        {mountedVehicle.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </dd>
                  </div>
                </div>
              </div>
              <div className="ml-4">
                <button
                  onClick={() => onNavigateToVehicle(mountedVehicle.id)}
                  className="px-4 py-2 text-sm font-medium text-white rounded"
                  style={{ backgroundColor: '#7ed321' }}
                >
                  View Vehicle Details
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Notes */}
      {equipment.notes && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Notes</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{equipment.notes}</p>
        </div>
      )}
    </div>
  );
}
