/**
 * VehicleDetailPage - Detailed vehicle view with tabs
 *
 * Shows vehicle information with tabs for VIN decode, work history, inspections, and maintenance
 */

import { useState, useEffect } from 'react';
import { vehiclesApi, equipmentApi } from '@/api/assets.api';
import type { Vehicle, Equipment } from '@/api/assets.api';
import { customersApi } from '@/api/customers.api';
import type { Customer } from '@/api/customers.api';
import { TabNavigation, type Tab } from '@/components/ui/TabNavigation';
import { VehicleOverviewTab } from './tabs/VehicleOverviewTab';
import { VehicleVINDecodeTab } from './tabs/VehicleVINDecodeTab';
import { CreateInspectionModal } from '@/features/inspections/CreateInspectionModal';

type VehicleTab = 'overview' | 'vin-decode' | 'work-history' | 'inspection-history' | 'maintenance-schedule';

interface VehicleDetailPageProps {
  vehicleId: string;
  onNavigateBack: () => void;
  onNavigateToEquipment: (equipmentId: string) => void;
  onNavigateToCustomer: (customerId: string) => void;
  onNavigateToInspection?: (inspectionId: string) => void;
}

export function VehicleDetailPage({
  vehicleId,
  onNavigateBack,
  onNavigateToEquipment,
  onNavigateToCustomer,
  onNavigateToInspection,
}: VehicleDetailPageProps) {
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [mountedEquipment, setMountedEquipment] = useState<Equipment[]>([]);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contentHeight, setContentHeight] = useState(0);
  const [activeTab, setActiveTab] = useState<VehicleTab>('overview');
  const [showCreateInspection, setShowCreateInspection] = useState(false);

  useEffect(() => {
    loadVehicleData();
  }, [vehicleId]);

  // Calculate available content height
  useEffect(() => {
    const calculateHeight = () => {
      let availableHeight = window.innerHeight - 64;

      const header = document.querySelector('.vehicle-detail-header') as HTMLElement;
      if (header) availableHeight -= header.offsetHeight;

      const tabNav = document.querySelector('.vehicle-detail-tabs') as HTMLElement;
      if (tabNav) availableHeight -= tabNav.offsetHeight;

      availableHeight -= 48; // padding
      setContentHeight(availableHeight);
    };

    const timer = setTimeout(calculateHeight, 150);
    window.addEventListener('resize', calculateHeight);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculateHeight);
    };
  }, [vehicle]);

  const loadVehicleData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const vehicleData = await vehiclesApi.get(vehicleId);
      setVehicle(vehicleData);

      // Load mounted equipment
      const allEquipment = await equipmentApi.list();
      const mounted = allEquipment.filter(e => e.mounted_on_vehicle === vehicleId);
      setMountedEquipment(mounted);

      // Load customer
      const customerData = await customersApi.get(vehicleData.customer);
      setCustomer(customerData);
    } catch (err: any) {
      setError(err.message || 'Failed to load vehicle');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading vehicle...</p>
        </div>
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Vehicle</h3>
          <p className="text-sm text-gray-600 mb-4">{error || 'Vehicle not found'}</p>
          <button
            onClick={onNavigateBack}
            className="px-4 py-2 text-sm font-medium text-white rounded"
            style={{ backgroundColor: '#7ed321' }}
          >
            Back to Assets
          </button>
        </div>
      </div>
    );
  }

  const tabs: Tab[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'vin-decode', label: 'VIN Decode' },
    { key: 'work-history', label: 'Work History' },
    { key: 'inspection-history', label: 'Inspection History' },
    { key: 'maintenance-schedule', label: 'Maintenance Schedule' },
  ];

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="vehicle-detail-header flex-shrink-0 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateBack}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="Back to assets"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            {vehicle.photo ? (
              <img
                src={vehicle.photo}
                alt={vehicle.unit_number || 'Vehicle'}
                className="w-12 h-12 rounded object-cover border border-gray-200"
              />
            ) : (
              <div className="w-12 h-12 rounded bg-gray-100 border border-gray-200 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            )}
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {vehicle.unit_number || `VIN: ${vehicle.vin.substring(0, 8)}...`}
              </h1>
              <p className="text-xs text-gray-500 mt-0.5">
                {vehicle.year && vehicle.make && vehicle.model
                  ? `${vehicle.year} ${vehicle.make} ${vehicle.model}`
                  : 'Vehicle'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCreateInspection(true)}
              className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
              style={{ backgroundColor: '#7ed321' }}
            >
              Create Inspection
            </button>
            <span
              className="px-2.5 py-1 text-xs font-medium rounded-full"
              style={{
                backgroundColor: vehicle.is_active ? '#dcfce7' : '#fee2e2',
                color: vehicle.is_active ? '#166534' : '#991b1b',
              }}
            >
              {vehicle.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="vehicle-detail-tabs flex-shrink-0 px-6">
        <TabNavigation tabs={tabs} activeTab={activeTab} onTabChange={(key) => setActiveTab(key as VehicleTab)} />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden px-6 pb-6 pt-6">
        <div style={{ height: `${contentHeight}px`, overflowY: 'auto' }}>
          {activeTab === 'overview' && (
            <VehicleOverviewTab
              vehicle={vehicle}
              mountedEquipment={mountedEquipment}
              customer={customer}
              onNavigateToEquipment={onNavigateToEquipment}
              onNavigateToCustomer={onNavigateToCustomer}
            />
          )}

          {activeTab === 'vin-decode' && (
            <VehicleVINDecodeTab
              vehicle={vehicle}
              onVINDecoded={loadVehicleData}
            />
          )}

          {activeTab === 'work-history' && (
            <div className="p-8 text-center border border-gray-200 rounded-lg">
              <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="mt-2 text-sm text-gray-500">Work history coming soon</p>
            </div>
          )}

          {activeTab === 'inspection-history' && (
            <div className="p-8 text-center border border-gray-200 rounded-lg">
              <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="mt-2 text-sm text-gray-500">Inspection history coming soon</p>
            </div>
          )}

          {activeTab === 'maintenance-schedule' && (
            <div className="p-8 text-center border border-gray-200 rounded-lg">
              <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="mt-2 text-sm text-gray-500">Maintenance schedule coming soon</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Inspection Modal */}
      {showCreateInspection && (
        <CreateInspectionModal
          assetType="VEHICLE"
          assetId={vehicle.id}
          assetName={vehicle.unit_number || `VIN: ${vehicle.vin.substring(0, 8)}...`}
          onClose={() => setShowCreateInspection(false)}
          onSuccess={(inspectionId) => {
            setShowCreateInspection(false);
            if (onNavigateToInspection) {
              onNavigateToInspection(inspectionId);
            }
          }}
        />
      )}
    </div>
  );
}
