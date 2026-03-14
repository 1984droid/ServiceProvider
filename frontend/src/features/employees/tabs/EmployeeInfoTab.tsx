/**
 * EmployeeInfoTab - Basic employee information
 *
 * Includes: Employee number, name, contact info, department, hire date
 */

import { useState } from 'react';
import type { Employee, CreateEmployeeRequest } from '@/api/employees.api';
import type { Department } from '@/api/departments.api';

interface EmployeeInfoTabProps {
  formData: CreateEmployeeRequest;
  setFormData: (data: CreateEmployeeRequest) => void;
  departments: Department[];
  isEditing: boolean;
  employee: Employee | null;
}

export function EmployeeInfoTab({
  formData,
  setFormData,
  departments,
  isEditing,
  employee,
}: EmployeeInfoTabProps) {
  const [showHireDateConfirm, setShowHireDateConfirm] = useState(false);
  const [pendingHireDate, setPendingHireDate] = useState('');

  const handleHireDateChange = (newDate: string) => {
    if (isEditing && employee?.hire_date && newDate !== employee.hire_date) {
      // Show confirmation dialog
      setPendingHireDate(newDate);
      setShowHireDateConfirm(true);
    } else {
      // No confirmation needed for new employees or same date
      setFormData({ ...formData, hire_date: newDate });
    }
  };

  const confirmHireDateChange = () => {
    setFormData({ ...formData, hire_date: pendingHireDate });
    setShowHireDateConfirm(false);
    setPendingHireDate('');
  };

  const cancelHireDateChange = () => {
    setShowHireDateConfirm(false);
    setPendingHireDate('');
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hire Date Confirmation Modal */}
      {showHireDateConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Confirm Hire Date Change
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Changing the hire date affects tenure calculations, seniority, and benefits.
              Are you sure you want to change this employee's hire date?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={cancelHireDateChange}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmHireDateChange}
                className="px-4 py-2 text-sm font-medium text-white rounded"
                style={{ backgroundColor: '#7ed321' }}
              >
                Confirm Change
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Basic Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Employee Number <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.employee_number}
                onChange={(e) => setFormData({ ...formData, employee_number: e.target.value })}
                readOnly={isEditing}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                style={isEditing ? { backgroundColor: '#f3f4f6', cursor: 'not-allowed' } : {}}
                placeholder="e.g., EMP001"
                required
              />
              {isEditing && (
                <p className="mt-1 text-xs text-gray-500">
                  Employee number cannot be changed after creation
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                placeholder="e.g., Service Technician"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                required
              />
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Contact Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                placeholder="employee@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                placeholder="(555) 123-4567"
              />
            </div>
          </div>
        </div>

        {/* Department Assignment */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Department Assignment</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Base Department <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.base_department}
                onChange={(e) => setFormData({ ...formData, base_department: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                required
              >
                <option value="">Select department...</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name} ({dept.code})
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Primary department for this employee
              </p>
            </div>
          </div>
        </div>

        {/* Employment Details */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Employment Details</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hire Date
              </label>
              <input
                type="date"
                value={formData.hire_date}
                onChange={(e) => handleHireDateChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              />
              {isEditing && employee?.hire_date && (
                <p className="mt-1 text-xs text-gray-500">
                  Changes require confirmation due to impact on tenure and benefits
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
