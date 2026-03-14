/**
 * AssetsListPage
 *
 * Display list of all assets (vehicles and equipment) with tabs
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useEffect, useState } from 'react';
import { vehiclesApi, equipmentApi, type Vehicle, type Equipment } from '@/api/assets.api';
import { VehicleDetailPage } from './VehicleDetailPage';
import { EquipmentDetailPage } from './EquipmentDetailPage';

type Tab = 'vehicles' | 'equipment';
type View = 'list' | 'vehicle-detail' | 'equipment-detail';

interface AssetsListPageProps {
  initialVehicleId?: string;
  initialEquipmentId?: string;
  onNavigateToCustomer: (customerId: string) => void;
  onNavigateToInspection?: (inspectionId: string) => void;
  onClearSelection: () => void;
  onCreateVehicle: () => void;
  onCreateEquipment?: () => void;
}

export function AssetsListPage({
  initialVehicleId,
  initialEquipmentId,
  onNavigateToCustomer,
  onNavigateToInspection,
  onClearSelection,
  onCreateVehicle,
  onCreateEquipment,
}: AssetsListPageProps) {
  const [activeTab, setActiveTab] = useState<Tab>('vehicles');
  const [currentView, setCurrentView] = useState<View>('list');
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  // Handle initial navigation from external links
  useEffect(() => {
    if (initialVehicleId) {
      setSelectedVehicleId(initialVehicleId);
      setCurrentView('vehicle-detail');
    } else if (initialEquipmentId) {
      setSelectedEquipmentId(initialEquipmentId);
      setCurrentView('equipment-detail');
    }
  }, [initialVehicleId, initialEquipmentId]);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [vehiclesData, equipmentData] = await Promise.all([
        vehiclesApi.list(),
        equipmentApi.list(),
      ]);
      setVehicles(vehiclesData);
      setEquipment(equipmentData);
    } catch (err: any) {
      setError(err.message || 'Failed to load assets');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredVehicles = vehicles.filter(vehicle =>
    vehicle.vin.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.unit_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.make?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.model?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredEquipment = equipment.filter(eq =>
    eq.serial_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    eq.asset_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    eq.manufacturer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    eq.model?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleVehicleClick = (vehicleId: string) => {
    setSelectedVehicleId(vehicleId);
    setCurrentView('vehicle-detail');
  };

  const handleEquipmentClick = (equipmentId: string) => {
    setSelectedEquipmentId(equipmentId);
    setCurrentView('equipment-detail');
  };

  const handleNavigateBack = () => {
    setCurrentView('list');
    setSelectedVehicleId(null);
    setSelectedEquipmentId(null);
    onClearSelection();
  };

  // Show detail views
  if (currentView === 'vehicle-detail' && selectedVehicleId) {
    return (
      <VehicleDetailPage
        vehicleId={selectedVehicleId}
        onNavigateBack={handleNavigateBack}
        onNavigateToEquipment={handleEquipmentClick}
        onNavigateToCustomer={onNavigateToCustomer}
        onNavigateToInspection={onNavigateToInspection}
      />
    );
  }

  if (currentView === 'equipment-detail' && selectedEquipmentId) {
    return (
      <EquipmentDetailPage
        equipmentId={selectedEquipmentId}
        onNavigateBack={handleNavigateBack}
        onNavigateToVehicle={handleVehicleClick}
        onNavigateToCustomer={onNavigateToCustomer}
        onNavigateToInspection={onNavigateToInspection}
      />
    );
  }

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
            Assets
          </h1>
          <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
            Manage vehicles and equipment
          </p>
        </div>
        <button
          onClick={() => {
            if (activeTab === 'vehicles') {
              onCreateVehicle();
            } else if (onCreateEquipment) {
              onCreateEquipment();
            }
          }}
          className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
          style={{ backgroundColor: '#7ed321' }}
        >
          + Create {activeTab === 'vehicles' ? 'Vehicle' : 'Equipment'}
        </button>
      </div>

      {/* Tabs */}
      <div className="mb-4 flex gap-2 border-b" style={{ borderColor: '#e5e7eb' }}>
        <button
          onClick={() => setActiveTab('vehicles')}
          className="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'vehicles' ? '#7ed321' : 'transparent',
            color: activeTab === 'vehicles' ? '#7ed321' : '#6b7280',
          }}
        >
          Vehicles ({vehicles.length})
        </button>
        <button
          onClick={() => setActiveTab('equipment')}
          className="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
          style={{
            borderColor: activeTab === 'equipment' ? '#7ed321' : 'transparent',
            color: activeTab === 'equipment' ? '#7ed321' : '#6b7280',
          }}
        >
          Equipment ({equipment.length})
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder={activeTab === 'vehicles' ? 'Search by VIN, unit number, make, or model...' : 'Search by serial number, asset number, manufacturer, or model...'}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="font-medium" style={{ color: '#dc2626' }}>
            {error}
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <svg className="animate-spin h-8 w-8 mx-auto mb-3" style={{ color: '#7ed321' }} fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm" style={{ color: '#6b7280' }}>Loading assets...</p>
        </div>
      )}

      {/* Vehicles Table */}
      {!isLoading && !error && activeTab === 'vehicles' && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="border-b" style={{ backgroundColor: '#f9fafb', borderColor: '#e5e7eb' }}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Unit #
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Vehicle
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  VIN
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  License
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Odometer
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: '#e5e7eb' }}>
              {filteredVehicles.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: '#6b7280' }}>
                    {searchTerm ? 'No vehicles match your search' : 'No vehicles yet.'}
                  </td>
                </tr>
              ) : (
                filteredVehicles.map((vehicle) => (
                  <tr
                    key={vehicle.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => handleVehicleClick(vehicle.id)}
                  >
                    <td className="px-4 py-3 text-sm font-medium" style={{ color: '#111827' }}>
                      {vehicle.unit_number || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium" style={{ color: '#111827' }}>
                        {vehicle.year && vehicle.make && vehicle.model ? `${vehicle.year} ${vehicle.make} ${vehicle.model}` : 'Unknown'}
                      </p>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                      {vehicle.vin}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {vehicle.license_plate || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {vehicle.odometer_miles ? `${vehicle.odometer_miles.toLocaleString()} mi` : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-1 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: vehicle.is_active ? '#dcfce7' : '#f3f4f6',
                          color: vehicle.is_active ? '#166534' : '#6b7280',
                        }}
                      >
                        {vehicle.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Equipment Table */}
      {!isLoading && !error && activeTab === 'equipment' && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="border-b" style={{ backgroundColor: '#f9fafb', borderColor: '#e5e7eb' }}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Asset #
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Equipment
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Serial Number
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Hours
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: '#e5e7eb' }}>
              {filteredEquipment.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: '#6b7280' }}>
                    {searchTerm ? 'No equipment matches your search' : 'No equipment yet.'}
                  </td>
                </tr>
              ) : (
                filteredEquipment.map((eq) => (
                  <tr
                    key={eq.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => handleEquipmentClick(eq.id)}
                  >
                    <td className="px-4 py-3 text-sm font-medium" style={{ color: '#111827' }}>
                      {eq.asset_number || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium" style={{ color: '#111827' }}>
                        {eq.manufacturer && eq.model ? `${eq.manufacturer} ${eq.model}` : 'Unknown'}
                      </p>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                      {eq.equipment_type || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                      {eq.serial_number}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {eq.engine_hours ? `${eq.engine_hours.toLocaleString()} hrs` : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-1 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: eq.is_active ? '#dcfce7' : '#f3f4f6',
                          color: eq.is_active ? '#166534' : '#6b7280',
                        }}
                      >
                        {eq.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Count */}
      {!isLoading && !error && (
        <div className="mt-4 text-sm" style={{ color: '#6b7280' }}>
          {activeTab === 'vehicles'
            ? `Showing ${filteredVehicles.length} of ${vehicles.length} vehicles`
            : `Showing ${filteredEquipment.length} of ${equipment.length} equipment`
          }
        </div>
      )}
    </div>
  );
}
