/**
 * EmployeeUserAccessButton
 *
 * Grant or revoke user access for an employee with confirmation modal
 */

import { useState } from 'react';
import { employeesApi, type Employee } from '@/api/employees.api';

interface EmployeeUserAccessButtonProps {
  employee: Employee;
  onSuccess: () => void;
}

export function EmployeeUserAccessButton({
  employee,
  onSuccess,
}: EmployeeUserAccessButtonProps) {
  const [showModal, setShowModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tempPassword, setTempPassword] = useState<string | null>(null);

  const handleGrantAccess = async () => {
    setIsProcessing(true);
    setError(null);
    setTempPassword(null);

    try {
      const result = await employeesApi.createUser(employee.id);
      setTempPassword(result.temporary_password || null);

      // Auto-close after a delay if no password to show
      if (!result.temporary_password) {
        setTimeout(() => {
          setShowModal(false);
          onSuccess();
        }, 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to grant access');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRevokeAccess = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      await employeesApi.revokeUser(employee.id, false);
      setShowModal(false);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to revoke access');
    } finally {
      setIsProcessing(false);
    }
  };

  const hasAccess = employee.has_user_account;

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="text-xs font-medium hover:underline"
        style={{ color: hasAccess ? '#dc2626' : '#7ed321' }}
      >
        {hasAccess ? 'Revoke' : 'Grant Access'}
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4" style={{ color: '#111827' }}>
              {hasAccess ? 'Revoke User Access' : 'Grant User Access'}
            </h3>

            {/* Success - Show temp password */}
            {tempPassword && (
              <div className="mb-4">
                <div className="p-4 rounded-lg" style={{ backgroundColor: '#dcfce7', border: '2px solid #16a34a' }}>
                  <p className="text-sm font-semibold mb-2" style={{ color: '#166534' }}>
                    ✓ Access Granted!
                  </p>
                  <p className="text-sm mb-2" style={{ color: '#166534' }}>
                    Username: <strong>{employee.email?.split('@')[0] || `emp_${employee.employee_number}`}</strong>
                  </p>
                  <p className="text-sm mb-2" style={{ color: '#166534' }}>
                    Temporary Password:
                  </p>
                  <div className="p-2 rounded font-mono text-sm" style={{ backgroundColor: 'white', border: '1px solid #16a34a' }}>
                    {tempPassword}
                  </div>
                  <p className="text-xs mt-2" style={{ color: '#166534' }}>
                    ⚠️ Save this password now - it will not be shown again!
                  </p>
                </div>
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => {
                      setShowModal(false);
                      onSuccess();
                    }}
                    className="px-4 py-2 text-sm font-medium text-white rounded"
                    style={{ backgroundColor: '#7ed321' }}
                  >
                    Done
                  </button>
                </div>
              </div>
            )}

            {/* Grant Access Confirmation */}
            {!hasAccess && !tempPassword && (
              <>
                <p className="text-sm mb-4" style={{ color: '#6b7280' }}>
                  Create a user account for <strong>{employee.full_name}</strong>?
                </p>
                <p className="text-sm mb-4" style={{ color: '#6b7280' }}>
                  A username and temporary password will be generated automatically.
                </p>

                {error && (
                  <div className="mb-4 p-3 rounded text-sm" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowModal(false)}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGrantAccess}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white rounded disabled:opacity-50"
                    style={{ backgroundColor: '#7ed321' }}
                  >
                    {isProcessing ? 'Creating...' : 'Grant Access'}
                  </button>
                </div>
              </>
            )}

            {/* Revoke Access Confirmation */}
            {hasAccess && !tempPassword && (
              <>
                <p className="text-sm mb-4" style={{ color: '#6b7280' }}>
                  Revoke login access for <strong>{employee.full_name}</strong>?
                </p>
                <p className="text-sm mb-4" style={{ color: '#6b7280' }}>
                  Username: <strong>{employee.user_info?.username}</strong>
                </p>
                <p className="text-sm mb-4" style={{ color: '#991b1b' }}>
                  The user account will be deactivated and unlinked. The employee record will remain.
                </p>

                {error && (
                  <div className="mb-4 p-3 rounded text-sm" style={{ backgroundColor: '#fee2e2', color: '#991b1b' }}>
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowModal(false)}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRevokeAccess}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white rounded disabled:opacity-50"
                    style={{ backgroundColor: '#dc2626' }}
                  >
                    {isProcessing ? 'Revoking...' : 'Revoke Access'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
