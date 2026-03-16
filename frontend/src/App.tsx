/**
 * Main App Component
 *
 * Root application with clean dashboard layout that adapts to user's window size.
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/api/auth.api';
import { LoginPage } from '@/features/auth/LoginPage';
import { CustomerCreatePage } from '@/features/customers/CustomerCreatePage';
import { CustomerListPage } from '@/features/customers/CustomerListPage';
import { CustomerDetailPage } from '@/features/customers/CustomerDetailPage';
import { ContactDetailPage } from '@/features/contacts/ContactDetailPage';
import { ContactEditPage } from '@/features/contacts/ContactEditPage';
import { AssetsListPage } from '@/features/assets/AssetsListPage';
import { VehicleCreatePage } from '@/features/assets/VehicleCreatePage';
import { EquipmentCreatePage } from '@/features/assets/EquipmentCreatePage';
import { InspectionsListPage } from '@/features/inspections/InspectionsListPage';
import { InspectionExecutePage } from '@/features/inspections/InspectionExecutePage';
import { InspectionReviewPage } from '@/features/inspections/InspectionReviewPage';
import { EmployeeListPage } from '@/features/employees/EmployeeListPage';
import { EmployeeFormPage } from '@/features/employees/EmployeeFormPage';
import { WorkOrdersListPage } from '@/features/work-orders/WorkOrdersListPage';
import { WorkOrderDetailPage } from '@/features/work-orders/WorkOrderDetailPage';
import { WorkOrderCreatePage } from '@/features/work-orders/WorkOrderCreatePage';

type Page = 'dashboard' | 'customers' | 'customers-create' | 'customers-detail' | 'contacts-detail' | 'contacts-edit' | 'assets' | 'assets-create-vehicle' | 'assets-create-equipment' | 'inspections' | 'inspection-execute' | 'inspection-review' | 'work-orders' | 'work-orders-create' | 'work-order-detail' | 'employees' | 'employees-create' | 'employees-edit';

interface NavigationState {
  customerId?: string;
  contactId?: string;
  vehicleId?: string;
  equipmentId?: string;
  inspectionId?: string;
  workOrderId?: string;
  employeeId?: string;
}

function App() {
  const { user, isAuthenticated, isLoading, setUser, setLoading } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [operationsOpen, setOperationsOpen] = useState(true);
  const [managementOpen, setManagementOpen] = useState(true);
  const [currentPage, setCurrentPage] = useState<Page>('customers');
  const [navState, setNavState] = useState<NavigationState>({});
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);

  // Navigation helper functions
  const navigateToCustomer = (customerId: string) => {
    setNavState({ customerId });
    setCurrentPage('customers-detail');
    window.history.pushState({}, '', `/customers/${customerId}`);
  };

  const navigateToContact = (contactId: string) => {
    setNavState({ contactId });
    setCurrentPage('contacts-detail');
    window.history.pushState({}, '', `/contacts/${contactId}`);
  };

  const navigateToContactEdit = (contactId: string) => {
    setNavState({ contactId });
    setCurrentPage('contacts-edit');
    window.history.pushState({}, '', `/contacts/${contactId}/edit`);
  };

  const navigateToVehicle = (vehicleId: string) => {
    setNavState({ vehicleId });
    setCurrentPage('assets');
    window.history.pushState({}, '', `/vehicles/${vehicleId}`);
  };

  const navigateToEquipment = (equipmentId: string) => {
    setNavState({ equipmentId });
    setCurrentPage('assets');
    window.history.pushState({}, '', `/equipment/${equipmentId}`);
  };

  const navigateToInspection = (inspectionId: string) => {
    setNavState({ inspectionId });
    setCurrentPage('inspection-execute');
    window.history.pushState({}, '', `/inspections/${inspectionId}`);
  };

  const navigateToInspectionReview = (inspectionId: string) => {
    setNavState({ inspectionId });
    setCurrentPage('inspection-review');
    window.history.pushState({}, '', `/inspections/${inspectionId}/review`);
  };

  const navigateToWorkOrder = (workOrderId: string) => {
    setNavState({ workOrderId });
    setCurrentPage('work-order-detail');
    window.history.pushState({}, '', `/work-orders/${workOrderId}`);
  };

  useEffect(() => {
    const initAuth = async () => {
      if (authApi.isAuthenticated()) {
        try {
          const user = await authApi.getCurrentUser();
          setUser(user);
        } catch (error) {
          console.error('Failed to load user:', error);
          setUser(null);
        }
      } else {
        setLoading(false);
      }
    };
    initAuth();
  }, [setUser, setLoading]);

  // Restore navigation state from URL on mount
  useEffect(() => {
    const path = window.location.pathname;

    // Parse URL and restore state
    if (path.startsWith('/customers/')) {
      const customerId = path.replace('/customers/', '');
      if (customerId && customerId !== 'create') {
        setNavState({ customerId });
        setCurrentPage('customers-detail');
      } else if (customerId === 'create') {
        setCurrentPage('customers-create');
      }
    } else if (path.startsWith('/contacts/')) {
      const parts = path.replace('/contacts/', '').split('/');
      const contactId = parts[0];
      if (parts[1] === 'edit') {
        setNavState({ contactId });
        setCurrentPage('contacts-edit');
      } else {
        setNavState({ contactId });
        setCurrentPage('contacts-detail');
      }
    } else if (path.startsWith('/vehicles/')) {
      const vehicleId = path.replace('/vehicles/', '');
      setNavState({ vehicleId });
      setCurrentPage('assets');
    } else if (path.startsWith('/equipment/')) {
      const equipmentId = path.replace('/equipment/', '');
      setNavState({ equipmentId });
      setCurrentPage('assets');
    } else if (path === '/inspections') {
      setCurrentPage('inspections');
    } else if (path.startsWith('/inspections/')) {
      const parts = path.replace('/inspections/', '').split('/');
      const inspectionId = parts[0];
      if (parts[1] === 'review') {
        setNavState({ inspectionId });
        setCurrentPage('inspection-review');
      } else {
        setNavState({ inspectionId });
        setCurrentPage('inspection-execute');
      }
    } else if (path.startsWith('/work-orders/')) {
      const workOrderId = path.replace('/work-orders/', '');
      setNavState({ workOrderId });
      setCurrentPage('work-order-detail');
    } else if (path.startsWith('/employees')) {
      setCurrentPage('employees');
    } else if (path.startsWith('/assets')) {
      setCurrentPage('assets');
    } else if (path === '/' || path === '/customers') {
      setCurrentPage('customers');
    }
  }, []);

  // Handle hash-based URL routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1); // Remove the #

      if (!hash) return;

      // Parse hash routes
      if (hash.startsWith('/customers/')) {
        const customerId = hash.replace('/customers/', '');
        if (customerId && customerId !== 'create') {
          navigateToCustomer(customerId);
        } else if (customerId === 'create') {
          setCurrentPage('customers-create');
        }
      } else if (hash.startsWith('/contacts/')) {
        const contactId = hash.replace('/contacts/', '');
        if (contactId) {
          navigateToContact(contactId);
        }
      } else if (hash === '/customers') {
        setCurrentPage('customers');
        setNavState({});
      } else if (hash === '/assets') {
        setCurrentPage('assets');
        setNavState({});
      } else if (hash === '/inspections') {
        setCurrentPage('inspections');
        setNavState({});
      }
    };

    // Handle initial hash on load
    handleHashChange();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Track viewport height changes
  useEffect(() => {
    const handleResize = () => {
      setViewportHeight(window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#f9fafb' }}>
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 mx-auto mb-4" style={{ color: '#7ed321' }} fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p style={{ color: '#6b7280' }}>Loading...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Authenticated - Dashboard
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f9fafb' }}>
      {/* Top Navigation */}
      <nav className="bg-white border-b" style={{ borderColor: '#e5e7eb', height: '64px' }}>
        <div className="h-full px-6 flex items-center justify-between">
          {/* Left - Logo */}
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Advantage Fleet" style={{ height: '40px', width: 'auto' }} />
            <span className="font-semibold" style={{ color: '#111827', fontSize: '16px' }}>
              Advantage Fleet
            </span>
          </div>

          {/* Right - User */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-semibold text-sm" style={{ color: '#111827' }}>
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs" style={{ color: '#6b7280' }}>
                {user?.roles?.[0] || 'User'}
              </p>
            </div>
            <button
              onClick={() => authApi.logout().then(() => setUser(null))}
              className="px-4 py-2 text-sm font-medium rounded-lg border"
              style={{
                borderColor: '#d1d5db',
                color: '#374151',
                backgroundColor: 'white'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="flex" style={{ height: `${viewportHeight - 64}px` }}>
        {/* Left Sidebar */}
        <aside
          className="bg-white border-r flex flex-col transition-all duration-200"
          style={{
            width: sidebarCollapsed ? '60px' : '160px',
            borderColor: '#e5e7eb',
            height: '100%'
          }}
        >
          {/* Collapse Button */}
          <div className="flex-shrink-0 p-2 border-b" style={{ borderColor: '#e5e7eb' }}>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="w-full flex items-center justify-center p-1.5 rounded hover:bg-gray-50 transition-colors"
              style={{ color: '#6b7280' }}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {sidebarCollapsed ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                )}
              </svg>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-1.5">
            {/* Dashboard */}
            <button
              onClick={() => { setCurrentPage('dashboard'); window.history.pushState({}, '', '/'); }}
              className={`w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs transition-colors ${sidebarCollapsed ? 'justify-center' : ''}`}
              style={{
                backgroundColor: currentPage === 'dashboard' ? '#f0fdf4' : 'transparent',
                color: currentPage === 'dashboard' ? '#15803d' : '#6b7280'
              }}
              title="Dashboard"
            >
              <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              {!sidebarCollapsed && <span className="font-medium">Dashboard</span>}
            </button>

            {/* OPERATIONS Section */}
            {!sidebarCollapsed && (
              <div className="mt-3">
                <button
                  onClick={() => setOperationsOpen(!operationsOpen)}
                  className="w-full flex items-center justify-between px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide"
                  style={{ color: '#9ca3af' }}
                >
                  <span>Operations</span>
                  <svg
                    className={`w-2.5 h-2.5 transition-transform ${operationsOpen ? 'rotate-0' : '-rotate-90'}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {operationsOpen && (
                <div className="mt-0.5 space-y-0.5">
                  <button
                    onClick={() => { setCurrentPage('assets'); window.history.pushState({}, '', '/assets'); }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundColor: currentPage === 'assets' ? '#f0fdf4' : 'transparent',
                      color: currentPage === 'assets' ? '#15803d' : '#6b7280'
                    }}
                    title="Assets"
                  >
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    {!sidebarCollapsed && <span>Assets</span>}
                  </button>
                  <button
                    onClick={() => { setCurrentPage('inspections'); window.history.pushState({}, '', '/inspections'); }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundColor: currentPage === 'inspections' ? '#f0fdf4' : 'transparent',
                      color: currentPage === 'inspections' ? '#15803d' : '#6b7280'
                    }}
                    title="Inspections"
                  >
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    {!sidebarCollapsed && <span>Inspections</span>}
                  </button>
                  <button
                    onClick={() => { setCurrentPage('work-orders'); window.history.pushState({}, '', '/work-orders'); }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundColor: currentPage === 'work-orders' || currentPage === 'work-order-detail' ? '#f0fdf4' : 'transparent',
                      color: currentPage === 'work-orders' || currentPage === 'work-order-detail' ? '#15803d' : '#6b7280'
                    }}
                    title="Work Orders"
                  >
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                    </svg>
                    {!sidebarCollapsed && <span>Work Orders</span>}
                  </button>
                  <button
                    onClick={() => { setCurrentPage('employees'); window.history.pushState({}, '', '/employees'); }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundColor: currentPage === 'employees' ? '#f0fdf4' : 'transparent',
                      color: currentPage === 'employees' ? '#15803d' : '#6b7280'
                    }}
                    title="Team"
                  >
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                    {!sidebarCollapsed && <span>Team</span>}
                  </button>
                </div>
              )}
            </div>
            )}

            {/* Collapsed view - show all menu items as icons */}
            {sidebarCollapsed && (
              <div className="mt-2 space-y-1">
                <a href="#" className="flex justify-center items-center px-2.5 py-1.5 rounded hover:bg-gray-50 transition-colors" style={{ color: '#6b7280' }} title="Assets">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </a>
                <a href="#" className="flex justify-center items-center px-2.5 py-1.5 rounded hover:bg-gray-50 transition-colors" style={{ color: '#6b7280' }} title="Work Orders">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                  </svg>
                </a>
                <a href="#" className="flex justify-center items-center px-2.5 py-1.5 rounded hover:bg-gray-50 transition-colors" style={{ color: '#6b7280' }} title="Inspections">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </a>
                <a href="#" className="flex justify-center items-center px-2.5 py-1.5 rounded hover:bg-gray-50 transition-colors" style={{ color: '#6b7280' }} title="Customers">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </a>
              </div>
            )}

            {/* MANAGEMENT Section */}
            {!sidebarCollapsed && (
            <div className="mt-3">
              <button
                onClick={() => setManagementOpen(!managementOpen)}
                className="w-full flex items-center justify-between px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide"
                style={{ color: '#9ca3af' }}
              >
                {!sidebarCollapsed && <span>Management</span>}
                <svg
                  className={`w-2.5 h-2.5 transition-transform ${managementOpen ? 'rotate-0' : '-rotate-90'}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {managementOpen && (
                <div className="mt-0.5 space-y-0.5">
                  <button
                    onClick={() => { setCurrentPage('customers'); window.history.pushState({}, '', '/customers'); }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                    style={{
                      backgroundColor: currentPage.startsWith('customers') ? '#f0fdf4' : 'transparent',
                      color: currentPage.startsWith('customers') ? '#15803d' : '#6b7280'
                    }}
                    title="Customers"
                  >
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    {!sidebarCollapsed && <span>Customers</span>}
                  </button>
                </div>
              )}
            </div>
            )}
          </nav>

          {/* Settings at Bottom */}
          <div className="flex-shrink-0 border-t" style={{ borderColor: '#e5e7eb', height: '48px' }}>
            <div className="h-full flex items-center px-1.5">
              <a
                href="#"
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs hover:bg-gray-50 transition-colors"
                style={{ color: '#6b7280' }}
                title="Settings"
              >
                <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {!sidebarCollapsed && <span>Settings</span>}
              </a>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {currentPage === 'dashboard' && (
            <div className="p-6">
              <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Dashboard</h1>
              <p className="mt-2 text-sm" style={{ color: '#6b7280' }}>Welcome to Advantage Fleet</p>
            </div>
          )}
          {currentPage === 'assets' && (
            <AssetsListPage
              initialVehicleId={navState.vehicleId}
              initialEquipmentId={navState.equipmentId}
              onNavigateToCustomer={navigateToCustomer}
              onNavigateToInspection={navigateToInspection}
              onClearSelection={() => setNavState({})}
              onCreateVehicle={() => setCurrentPage('assets-create-vehicle')}
              onCreateEquipment={() => setCurrentPage('assets-create-equipment')}
            />
          )}
          {currentPage === 'assets-create-vehicle' && (
            <VehicleCreatePage
              onSuccess={(vehicleId) => {
                setNavState({ vehicleId });
                setCurrentPage('assets');
              }}
              onCancel={() => setCurrentPage('assets')}
            />
          )}
          {currentPage === 'assets-create-equipment' && (
            <EquipmentCreatePage
              onSuccess={(equipmentId) => {
                setNavState({ equipmentId });
                setCurrentPage('assets');
              }}
              onCancel={() => setCurrentPage('assets')}
            />
          )}
          {currentPage === 'inspections' && (
            <InspectionsListPage onViewInspection={navigateToInspection} />
          )}
          {currentPage === 'inspection-execute' && navState.inspectionId && (
            <InspectionExecutePage
              inspectionId={navState.inspectionId}
              onExit={() => {
                setCurrentPage('inspections');
                setNavState({});
              }}
            />
          )}
          {currentPage === 'inspection-review' && navState.inspectionId && (
            <InspectionReviewPage
              inspectionId={navState.inspectionId}
              onExit={() => {
                setCurrentPage('inspections');
                setNavState({});
              }}
              onFinalize={() => {
                // TODO: Implement finalization flow
                setCurrentPage('inspections');
                setNavState({});
              }}
            />
          )}
          {currentPage === 'work-orders' && (
            <WorkOrdersListPage
              onNavigateToDetail={navigateToWorkOrder}
              onNavigateToCreate={() => setCurrentPage('work-orders-create')}
            />
          )}
          {currentPage === 'work-order-detail' && navState.workOrderId && (
            <WorkOrderDetailPage
              workOrderId={navState.workOrderId}
              onBack={() => setCurrentPage('work-orders')}
            />
          )}
          {currentPage === 'work-orders-create' && (
            <WorkOrderCreatePage
              onCancel={() => setCurrentPage('work-orders')}
              onSuccess={(workOrderId) => {
                setNavState({ workOrderId });
                setCurrentPage('work-order-detail');
              }}
            />
          )}
          {currentPage === 'employees' && (
            <EmployeeListPage
              onNavigateToCreate={() => setCurrentPage('employees-create')}
              onNavigateToDetail={(employeeId) => {
                setNavState({ employeeId });
                setCurrentPage('employees-edit');
              }}
            />
          )}
          {currentPage === 'employees-create' && (
            <EmployeeFormPage
              onSuccess={() => setCurrentPage('employees')}
              onCancel={() => setCurrentPage('employees')}
            />
          )}
          {currentPage === 'employees-edit' && navState.employeeId && (
            <EmployeeFormPage
              employeeId={navState.employeeId}
              onSuccess={() => setCurrentPage('employees')}
              onCancel={() => setCurrentPage('employees')}
            />
          )}
          {currentPage === 'customers' && (
            <CustomerListPage
              onNavigateToCreate={() => setCurrentPage('customers-create')}
              onNavigateToDetail={navigateToCustomer}
            />
          )}
          {currentPage === 'customers-create' && <CustomerCreatePage onSuccess={() => setCurrentPage('customers')} />}
          {currentPage === 'customers-detail' && navState.customerId && (
            <CustomerDetailPage
              customerId={navState.customerId}
              onNavigateBack={() => {
                setCurrentPage('customers');
                setNavState({});
              }}
              onNavigateToVehicle={navigateToVehicle}
              onNavigateToEquipment={navigateToEquipment}
              onNavigateToContact={navigateToContact}
            />
          )}
          {currentPage === 'contacts-detail' && navState.contactId && (
            <ContactDetailPage
              contactId={navState.contactId}
              onNavigateBack={() => {
                setCurrentPage('customers-detail');
              }}
              onNavigateToCustomer={navigateToCustomer}
              onEdit={navigateToContactEdit}
            />
          )}
          {currentPage === 'contacts-edit' && navState.contactId && (
            <ContactEditPage
              contactId={navState.contactId}
              onNavigateBack={() => {
                setCurrentPage('contacts-detail');
              }}
              onSaveComplete={(contactId) => {
                setNavState({ contactId });
                setCurrentPage('contacts-detail');
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
