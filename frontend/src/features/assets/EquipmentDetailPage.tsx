/**
 * EquipmentDetailPage - Detailed equipment view with tabs
 *
 * Shows equipment information with tabs for work history, inspections, and maintenance
 */

import { useState, useEffect } from 'react';
import { vehiclesApi, equipmentApi } from '@/api/assets.api';
import type { Vehicle, Equipment } from '@/api/assets.api';
import { customersApi } from '@/api/customers.api';
import type { Customer } from '@/api/customers.api';
import { TabNavigation, type Tab } from '@/components/ui/TabNavigation';
import { EquipmentOverviewTab } from './tabs/EquipmentOverviewTab';
import { CreateInspectionModal } from '@/features/inspections/CreateInspectionModal';

type EquipmentTab = 'overview' | 'work-history' | 'inspection-history' | 'maintenance-schedule';

interface EquipmentDetailPageProps {
  equipmentId: string;
  onNavigateBack: () => void;
  onNavigateToVehicle: (vehicleId: string) => void;
  onNavigateToCustomer: (customerId: string) => void;
  onNavigateToInspection?: (inspectionId: string) => void;
}

export function EquipmentDetailPage({
  equipmentId,
  onNavigateBack,
  onNavigateToVehicle,
  onNavigateToCustomer,
  onNavigateToInspection,
}: EquipmentDetailPageProps) {
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [mountedVehicle, setMountedVehicle] = useState<Vehicle | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contentHeight, setContentHeight] = useState(0);
  const [activeTab, setActiveTab] = useState<EquipmentTab>('overview');
  const [showCreateInspection, setShowCreateInspection] = useState(false);

  useEffect(() => {
    loadEquipmentData();
  }, [equipmentId]);

  // Calculate available content height
  useEffect(() => {
    const calculateHeight = () => {
      let availableHeight = window.innerHeight - 64;

      const header = document.querySelector('.equipment-detail-header') as HTMLElement;
      if (header) availableHeight -= header.offsetHeight;

      const tabNav = document.querySelector('.equipment-detail-tabs') as HTMLElement;
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
  }, [equipment]);

  const loadEquipmentData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const equipmentData = await equipmentApi.get(equipmentId);
      setEquipment(equipmentData);

      // Load mounted vehicle if applicable
      if (equipmentData.mounted_on_vehicle) {
        const vehicleData = await vehiclesApi.get(equipmentData.mounted_on_vehicle);
        setMountedVehicle(vehicleData);
      }

      // Load customer
      const customerData = await customersApi.get(equipmentData.customer);
      setCustomer(customerData);
    } catch (err: any) {
      setError(err.message || 'Failed to load equipment');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading equipment...</p>
        </div>
      </div>
    );
  }

  if (error || !equipment) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Equipment</h3>
          <p className="text-sm text-gray-600 mb-4">{error || 'Equipment not found'}</p>
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
    { key: 'work-history', label: 'Work History' },
    { key: 'inspection-history', label: 'Inspection History' },
    { key: 'maintenance-schedule', label: 'Maintenance Schedule' },
  ];

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="equipment-detail-header flex-shrink-0 px-6 py-4 border-b border-gray-200">
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
            {equipment.photo ? (
              <img
                src={equipment.photo}
                alt={equipment.asset_number || 'Equipment'}
                className="w-12 h-12 rounded object-cover border border-gray-200"
              />
            ) : (
              <div className="w-12 h-12 rounded bg-gray-100 border border-gray-200 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 008 10.586V5L7 4z" />
                </svg>
              </div>
            )}
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {equipment.asset_number || `SN: ${equipment.serial_number.substring(0, 12)}...`}
              </h1>
              <p className="text-xs text-gray-500 mt-0.5">
                {equipment.manufacturer && equipment.model
                  ? `${equipment.manufacturer} ${equipment.model}`
                  : equipment.equipment_type || 'Equipment'}
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
                backgroundColor: equipment.is_active ? '#dcfce7' : '#fee2e2',
                color: equipment.is_active ? '#166534' : '#991b1b',
              }}
            >
              {equipment.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="equipment-detail-tabs flex-shrink-0 px-6">
        <TabNavigation tabs={tabs} activeTab={activeTab} onTabChange={(key) => setActiveTab(key as EquipmentTab)} />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden px-6 pb-6 pt-6">
        <div style={{ height: `${contentHeight}px`, overflowY: 'auto' }}>
          {activeTab === 'overview' && (
            <EquipmentOverviewTab
              equipment={equipment}
              mountedVehicle={mountedVehicle}
              customer={customer}
              onNavigateToVehicle={onNavigateToVehicle}
              onNavigateToCustomer={onNavigateToCustomer}
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
          assetType="EQUIPMENT"
          assetId={equipment.id}
          assetName={equipment.asset_number || `SN: ${equipment.serial_number.substring(0, 12)}...`}
          equipmentType={equipment.equipment_type}
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
