/**
 * EmployeeFormPage - Create or edit employee with tabbed interface
 *
 * Tabs:
 * - Employee Info: Basic info, contact, department
 * - Certifications: Manage employee certifications
 * - User Access: Login, permissions, password management
 */

import { useState, useEffect } from 'react';
import { employeesApi, type Employee, type CreateEmployeeRequest } from '@/api/employees.api';
import { departmentsApi, type Department } from '@/api/departments.api';
import { TabNavigation, type Tab } from '@/components/ui/TabNavigation';
import { EmployeeInfoTab } from './tabs/EmployeeInfoTab';
import { EmployeeCertificationsTab } from './tabs/EmployeeCertificationsTab';
import { EmployeeUserAccessTab } from './tabs/EmployeeUserAccessTab';

type EmployeeTab = 'info' | 'certifications' | 'access';

interface EmployeeFormPageProps {
  employeeId?: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export function EmployeeFormPage({
  employeeId,
  onSuccess,
  onCancel,
}: EmployeeFormPageProps) {
  const [activeTab, setActiveTab] = useState<EmployeeTab>('info');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [contentHeight, setContentHeight] = useState(0);

  const [formData, setFormData] = useState<CreateEmployeeRequest>({
    employee_number: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    base_department: '',
    floating_departments: [],
    title: '',
    hire_date: '',
    certifications: [],
    skills: [],
  });

  useEffect(() => {
    loadDepartments();
    if (employeeId) {
      loadEmployee();
    }
  }, [employeeId]);

  // Calculate available content height
  useEffect(() => {
    const calculateHeight = () => {
      let availableHeight = window.innerHeight - 64; // Main nav height

      const header = document.querySelector('.employee-form-header') as HTMLElement;
      if (header) availableHeight -= header.offsetHeight;

      const tabNav = document.querySelector('.employee-form-tabs') as HTMLElement;
      if (tabNav) availableHeight -= tabNav.offsetHeight;

      const footer = document.querySelector('.employee-form-footer') as HTMLElement;
      if (footer) availableHeight -= footer.offsetHeight;

      availableHeight -= 48; // padding
      setContentHeight(availableHeight);
    };

    const timer = setTimeout(calculateHeight, 150);
    window.addEventListener('resize', calculateHeight);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', calculateHeight);
    };
  }, [employee]);

  const loadDepartments = async () => {
    try {
      const data = await departmentsApi.list({ is_active: true });
      setDepartments(data);
    } catch (err: any) {
      console.error('Failed to load departments:', err);
      setError('Failed to load departments');
    }
  };

  const loadEmployee = async () => {
    if (!employeeId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await employeesApi.get(employeeId);
      setEmployee(data);
      setFormData({
        employee_number: data.employee_number,
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email || '',
        phone: data.phone || '',
        base_department: data.base_department?.id || '',
        floating_departments: data.floating_departments?.map(d => d.id) || [],
        title: data.title || '',
        hire_date: data.hire_date || '',
        certifications: data.certifications || [],
        skills: data.skills || [],
      });
    } catch (err: any) {
      console.error('Failed to load employee:', err);
      setError(err.response?.data?.detail || 'Failed to load employee');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);

    try {
      if (employeeId) {
        await employeesApi.update(employeeId, formData);
      } else {
        await employeesApi.create(formData);
      }
      onSuccess();
    } catch (err: any) {
      console.error('Failed to save employee:', err);
      setError(err.response?.data?.detail || 'Failed to save employee');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading employee...</p>
        </div>
      </div>
    );
  }

  const tabs: Tab[] = [
    { key: 'info', label: 'Employee Info' },
    { key: 'certifications', label: 'Certifications', count: formData.certifications.length },
    { key: 'access', label: 'User Access' },
  ];

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="employee-form-header flex-shrink-0 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <button
              onClick={onCancel}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Team
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              {employeeId ? `Edit Employee: ${employee?.full_name}` : 'Create Employee'}
            </h1>
            {employeeId && employee && (
              <p className="mt-1 text-sm text-gray-600">
                {employee.employee_number} • {employee.base_department?.name}
                {employee.has_user_account && (
                  <span className="ml-2 text-green-600">• Portal Access</span>
                )}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex-shrink-0 mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <div className="flex gap-3">
            <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="mt-1 text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="employee-form-tabs flex-shrink-0 px-6">
        <TabNavigation
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={(key) => setActiveTab(key as EmployeeTab)}
        />
      </div>

      {/* Tab Content */}
      <div
        className="flex-1 overflow-y-auto px-6 py-6"
        style={{ maxHeight: contentHeight > 0 ? `${contentHeight}px` : 'auto' }}
      >
        {activeTab === 'info' && (
          <EmployeeInfoTab
            formData={formData}
            setFormData={setFormData}
            departments={departments}
            isEditing={!!employeeId}
            employee={employee}
          />
        )}

        {activeTab === 'certifications' && (
          <EmployeeCertificationsTab
            certifications={formData.certifications}
            onChange={(certs) => setFormData({ ...formData, certifications: certs })}
          />
        )}

        {activeTab === 'access' && (
          <EmployeeUserAccessTab
            employee={employee}
            onRefresh={loadEmployee}
          />
        )}
      </div>

      {/* Footer Actions */}
      <div className="employee-form-footer flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !formData.employee_number || !formData.first_name || !formData.last_name || !formData.base_department}
            className="px-4 py-2 text-sm font-medium text-white rounded disabled:opacity-50"
            style={{ backgroundColor: '#7ed321' }}
          >
            {isSaving ? 'Saving...' : (employeeId ? 'Save Changes' : 'Create Employee')}
          </button>
        </div>
      </div>
    </div>
  );
}
