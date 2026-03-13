/**
 * VehicleOverviewTab - Overview information for vehicle
 */

import type { Vehicle, Equipment } from '@/api/assets.api';
import type { Customer } from '@/api/customers.api';
import { StatCard } from '@/components/ui/StatCard';

interface VehicleOverviewTabProps {
  vehicle: Vehicle;
  mountedEquipment: Equipment[];
  customer: Customer | null;
  onNavigateToEquipment: (equipmentId: string) => void;
  onNavigateToCustomer: (customerId: string) => void;
}

export function VehicleOverviewTab({
  vehicle,
  mountedEquipment,
  customer,
  onNavigateToEquipment,
  onNavigateToCustomer,
}: VehicleOverviewTabProps) {
  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Mounted Equipment"
          value={mountedEquipment.length}
          subtitle={`${mountedEquipment.filter(e => e.is_active).length} active`}
          variant="info"
        />
        <StatCard
          label="Odometer"
          value={vehicle.odometer_miles !== null && vehicle.odometer_miles !== undefined
            ? `${vehicle.odometer_miles.toLocaleString()}`
            : '—'}
          subtitle="miles"
          variant="default"
        />
        <StatCard
          label="Engine Hours"
          value={vehicle.engine_hours !== null && vehicle.engine_hours !== undefined
            ? `${vehicle.engine_hours.toLocaleString()}`
            : '—'}
          subtitle="hours"
          variant="default"
        />
        <StatCard
          label="Status"
          value={vehicle.is_active ? 'Active' : 'Inactive'}
          variant={vehicle.is_active ? 'success' : 'danger'}
        />
      </div>

      {/* Vehicle Details */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Vehicle Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">VIN</dt>
            <dd className="mt-0.5 text-sm text-gray-900 font-mono">{vehicle.vin}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Unit Number</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vehicle.unit_number || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">License Plate</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vehicle.license_plate || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Year</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vehicle.year || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Make</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vehicle.make || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Model</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vehicle.model || '—'}</dd>
          </div>
          {vehicle.body_type && (
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Body Type</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{vehicle.body_type}</dd>
            </div>
          )}
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

      {/* Mounted Equipment */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide">
            Mounted Equipment ({mountedEquipment.length})
          </h3>
        </div>
        {mountedEquipment.length === 0 ? (
          <div className="p-8 text-center">
            <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2 text-sm text-gray-500">No equipment mounted on this vehicle</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Asset #</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Manufacturer</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mountedEquipment.map(equipment => (
                  <tr key={equipment.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {equipment.asset_number || equipment.serial_number.substring(0, 12)}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{equipment.equipment_type || '—'}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{equipment.manufacturer || '—'}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{equipment.model || '—'}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className="px-2 py-0.5 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: equipment.is_active ? '#dcfce7' : '#fee2e2',
                          color: equipment.is_active ? '#166534' : '#991b1b',
                        }}
                      >
                        {equipment.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <button
                        onClick={() => onNavigateToEquipment(equipment.id)}
                        className="text-sm font-medium hover:underline"
                        style={{ color: '#7ed321' }}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Notes */}
      {vehicle.notes && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Notes</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{vehicle.notes}</p>
        </div>
      )}
    </div>
  );
}
