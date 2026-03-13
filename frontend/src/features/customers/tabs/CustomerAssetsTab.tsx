/**
 * CustomerAssetsTab - List of all assets (vehicles and equipment) for customer
 *
 * Shows:
 * - Vehicles with VIN, unit number, make/model
 * - Equipment with serial number, asset number, type
 */

import type { Vehicle, Equipment } from '@/api/assets.api';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';

interface CustomerAssetsTabProps {
  vehicles: Vehicle[];
  equipment: Equipment[];
  onNavigateToVehicle?: (vehicleId: string) => void;
  onNavigateToEquipment?: (equipmentId: string) => void;
}

export function CustomerAssetsTab({
  vehicles,
  equipment,
  onNavigateToVehicle,
  onNavigateToEquipment,
}: CustomerAssetsTabProps) {
  const activeVehicles = vehicles.filter(v => v.is_active);
  const inactiveVehicles = vehicles.filter(v => !v.is_active);
  const activeEquipment = equipment.filter(e => e.is_active);
  const inactiveEquipment = equipment.filter(e => !e.is_active);

  if (vehicles.length === 0 && equipment.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No assets</h3>
          <p className="mt-1 text-sm text-gray-500">This customer has no vehicles or equipment yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Vehicles */}
      {activeVehicles.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <SectionHeader title={`Vehicles (${activeVehicles.length} Active)`} />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit #
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    VIN
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Year / Make / Model
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Body Type
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    License Plate
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Odometer
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeVehicles.map(vehicle => (
                  <tr
                    key={vehicle.id}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onNavigateToVehicle?.(vehicle.id)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {vehicle.unit_number || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-xs font-mono text-gray-600">{vehicle.vin}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">
                        {vehicle.year && vehicle.make && vehicle.model
                          ? `${vehicle.year} ${vehicle.make} ${vehicle.model}`
                          : '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {vehicle.body_type ? (
                        <Badge label={vehicle.body_type} variant="info" size="sm" />
                      ) : (
                        <span className="text-xs text-gray-400">Standard</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{vehicle.license_plate || '—'}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right">
                      <span className="text-sm text-gray-700">
                        {vehicle.odometer_miles !== null && vehicle.odometer_miles !== undefined
                          ? `${vehicle.odometer_miles.toLocaleString()} mi`
                          : '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Active Equipment */}
      {activeEquipment.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <SectionHeader title={`Equipment (${activeEquipment.length} Active)`} />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Asset #
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Serial Number
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Manufacturer / Model
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mounted On
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hours
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeEquipment.map(item => (
                  <tr
                    key={item.id}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onNavigateToEquipment?.(item.id)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {item.asset_number || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-xs font-mono text-gray-600">{item.serial_number}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {item.equipment_type ? (
                        <Badge label={item.equipment_type} variant="info" size="sm" />
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">
                        {item.manufacturer && item.model
                          ? `${item.manufacturer} ${item.model}`
                          : '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {item.mounted_on_vehicle ? (
                        <span className="text-xs text-gray-600">
                          {vehicles.find(v => v.id === item.mounted_on_vehicle)?.unit_number || 'Vehicle'}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">Standalone</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right">
                      <span className="text-sm text-gray-700">
                        {item.engine_hours !== null && item.engine_hours !== undefined
                          ? `${item.engine_hours.toLocaleString()} hrs`
                          : '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Inactive Assets Summary */}
      {(inactiveVehicles.length > 0 || inactiveEquipment.length > 0) && (
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <p className="text-xs text-gray-600">
            {inactiveVehicles.length > 0 && (
              <span>{inactiveVehicles.length} inactive vehicle{inactiveVehicles.length !== 1 ? 's' : ''}</span>
            )}
            {inactiveVehicles.length > 0 && inactiveEquipment.length > 0 && <span> • </span>}
            {inactiveEquipment.length > 0 && (
              <span>{inactiveEquipment.length} inactive equipment</span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}
