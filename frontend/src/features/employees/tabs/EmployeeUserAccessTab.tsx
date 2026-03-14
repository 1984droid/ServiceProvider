/**
 * EmployeeUserAccessTab - Manage user access and permissions
 *
 * Grant/revoke access, manage password, view login info
 */

import { useState } from 'react';
import type { Employee } from '@/api/employees.api';
import { EmployeeUserAccessButton } from '../EmployeeUserAccessButton';

interface EmployeeUserAccessTabProps {
  employee: Employee | null;
  onRefresh: () => void;
}

export function EmployeeUserAccessTab({
  employee,
  onRefresh,
}: EmployeeUserAccessTabProps) {
  if (!employee) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-sm text-gray-600">
            Save the employee first to manage user access
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="space-y-6">
        {/* Access Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Portal Access Status</h3>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              {employee.has_user_account ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-green-700">
                      Portal Access Granted
                    </span>
                  </div>

                  {employee.user_info && (
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs font-medium text-gray-500">Username</p>
                        <p className="text-sm text-gray-900 font-mono">
                          {employee.user_info.username}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs font-medium text-gray-500">Account Status</p>
                        <p className="text-sm text-gray-900">
                          {employee.user_info.is_active ? (
                            <span className="text-green-700">Active</span>
                          ) : (
                            <span className="text-red-700">Inactive</span>
                          )}
                        </p>
                      </div>

                      {employee.user_info.last_login && (
                        <div>
                          <p className="text-xs font-medium text-gray-500">Last Login</p>
                          <p className="text-sm text-gray-900">
                            {new Date(employee.user_info.last_login).toLocaleString()}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-700">
                      No Portal Access
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    This employee does not have a user account. Grant access to allow them to log in to the system.
                  </p>
                </div>
              )}
            </div>

            <div className="ml-4">
              <EmployeeUserAccessButton
                employee={employee}
                onSuccess={onRefresh}
              />
            </div>
          </div>
        </div>

        {/* Permissions Section (Stub for future) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Permissions & Roles</h3>
          <div className="bg-gray-50 border border-gray-200 rounded p-4 text-center">
            <p className="text-sm text-gray-600">
              Permission management coming soon
            </p>
          </div>
        </div>

        {/* Security Settings (Stub for future) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Security Settings</h3>
          <div className="bg-gray-50 border border-gray-200 rounded p-4 text-center">
            <p className="text-sm text-gray-600">
              Password reset and security settings coming soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
