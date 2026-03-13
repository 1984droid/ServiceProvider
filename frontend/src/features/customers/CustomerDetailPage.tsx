/**
 * CustomerDetailPage - Comprehensive customer detail view
 *
 * Tabbed interface showing all customer data:
 * - Overview: Stats, company info, primary contact
 * - Contacts: List with correspondence preferences
 * - Assets: Vehicles and equipment
 * - USDOT Data: FMCSA lookup information
 * - Billing: Account info and invoice stubs
 */

import { useState, useEffect } from 'react';
import { customersApi } from '@/api/customers.api';
import type { CustomerDetail } from '@/api/customers.api';
import { vehiclesApi, equipmentApi } from '@/api/assets.api';
import type { Vehicle, Equipment } from '@/api/assets.api';
import { TabNavigation } from '@/components/ui/TabNavigation';
import type { Tab } from '@/components/ui/TabNavigation';
import { CustomerOverviewTab } from './tabs/CustomerOverviewTab';
import { CustomerContactsTab } from './tabs/CustomerContactsTab';
import { CustomerAssetsTab } from './tabs/CustomerAssetsTab';
import { CustomerUSDOTTab } from './tabs/CustomerUSDOTTab';
import { CustomerBillingTab } from './tabs/CustomerBillingTab';

interface CustomerDetailPageProps {
  customerId: string;
  onNavigateBack: () => void;
  onNavigateToVehicle?: (vehicleId: string) => void;
  onNavigateToEquipment?: (equipmentId: string) => void;
  onNavigateToContact?: (contactId: string) => void;
}

export function CustomerDetailPage({
  customerId,
  onNavigateBack,
  onNavigateToVehicle,
  onNavigateToEquipment,
  onNavigateToContact,
}: CustomerDetailPageProps) {
  const [customer, setCustomer] = useState<CustomerDetail | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [contentHeight, setContentHeight] = useState(0);

  useEffect(() => {
    loadCustomerData();
  }, [customerId]);

  // Calculate available content height by measuring actual DOM elements
  useEffect(() => {
    const calculateHeight = () => {
      // Start with viewport height minus navbar
      let availableHeight = window.innerHeight - 64;

      // Measure the header section (back button, title, status)
      const header = document.querySelector('.customer-detail-header');
      if (header) {
        availableHeight -= header.offsetHeight;
      }

      // Measure the tab navigation
      const tabNav = document.querySelector('.customer-detail-tabs');
      if (tabNav) {
        availableHeight -= tabNav.offsetHeight;
      }

      // Account for padding on the content area (24px top + 24px bottom)
      availableHeight -= 48;

      setContentHeight(availableHeight);
    };

    // Delay to ensure DOM is fully rendered
    const timer = setTimeout(calculateHeight, 150);

    window.addEventListener('resize', calculateHeight);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculateHeight);
    };
  }, [customer]);

  const loadCustomerData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [customerData, vehiclesData, equipmentData] = await Promise.all([
        customersApi.getDetail(customerId),
        vehiclesApi.list().then(all => all.filter(v => v.customer === customerId)),
        equipmentApi.list().then(all => all.filter(e => e.customer === customerId)),
      ]);
      setCustomer(customerData);
      setVehicles(vehiclesData);
      setEquipment(equipmentData);
    } catch (err: any) {
      setError(err.message || 'Failed to load customer data');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading customer...</p>
        </div>
      </div>
    );
  }

  if (error || !customer) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Customer</h3>
          <p className="text-sm text-gray-600 mb-4">{error || 'Customer not found'}</p>
          <button
            onClick={onNavigateBack}
            className="px-4 py-2 text-sm font-medium text-white rounded"
            style={{ backgroundColor: '#7ed321' }}
          >
            Back to Customers
          </button>
        </div>
      </div>
    );
  }

  const tabs: Tab[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'contacts', label: 'Contacts', count: customer.contacts.length },
    { key: 'assets', label: 'Assets', count: vehicles.length + equipment.length },
    { key: 'usdot', label: 'USDOT Data' },
    { key: 'billing', label: 'Billing' },
  ];

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="customer-detail-header flex-shrink-0 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateBack}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="Back to customers"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {customer.name}
              </h1>
              <p className="text-xs text-gray-500 mt-0.5">
                {customer.legal_name && customer.legal_name !== customer.name && (
                  <span>Legal: {customer.legal_name} • </span>
                )}
                Customer ID: {customer.id.substring(0, 8)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className="px-2.5 py-1 text-xs font-medium rounded-full"
              style={{
                backgroundColor: customer.is_active ? '#dcfce7' : '#fee2e2',
                color: customer.is_active ? '#166534' : '#991b1b',
              }}
            >
              {customer.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="customer-detail-tabs flex-shrink-0 px-6">
        <TabNavigation tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden px-6 pb-6 pt-6">
        <div style={{ height: `${contentHeight}px`, overflowY: 'auto' }}>
          {activeTab === 'overview' && (
            <CustomerOverviewTab customer={customer} vehicles={vehicles} equipment={equipment} />
          )}
          {activeTab === 'contacts' && (
            <CustomerContactsTab
              customer={customer}
              onNavigateToContact={onNavigateToContact}
            />
          )}
          {activeTab === 'assets' && (
            <CustomerAssetsTab
              vehicles={vehicles}
              equipment={equipment}
              onNavigateToVehicle={onNavigateToVehicle}
              onNavigateToEquipment={onNavigateToEquipment}
            />
          )}
          {activeTab === 'usdot' && (
            <CustomerUSDOTTab
              customer={customer}
              onDataRefreshed={loadCustomerData}
            />
          )}
          {activeTab === 'billing' && (
            <CustomerBillingTab customer={customer} />
          )}
        </div>
      </div>
    </div>
  );
}
