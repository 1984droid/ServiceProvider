/**
 * EmployeeListPage
 *
 * Lists all employees with filtering and user access management
 */

import { useState, useEffect } from 'react';
import { employeesApi, type Employee } from '@/api/employees.api';

interface EmployeeListPageProps {
  onNavigateToDetail?: (employeeId: string) => void;
  onNavigateToCreate?: () => void;
}

export function EmployeeListPage({
  onNavigateToDetail,
  onNavigateToCreate,
}: EmployeeListPageProps) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<'all' | 'active' | 'inactive'>('active');
  const [filterHasLogin, setFilterHasLogin] = useState<'all' | 'yes' | 'no'>('all');

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await employeesApi.list();
      setEmployees(data.results);
    } catch (err: any) {
      setError(err.message || 'Failed to load employees');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch =
      emp.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.employee_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.base_department_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesActive =
      filterActive === 'all' ||
      (filterActive === 'active' && emp.is_active) ||
      (filterActive === 'inactive' && !emp.is_active);

    const matchesLogin =
      filterHasLogin === 'all' ||
      (filterHasLogin === 'yes' && emp.has_user_account) ||
      (filterHasLogin === 'no' && !emp.has_user_account);

    return matchesSearch && matchesActive && matchesLogin;
  });

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
            Team Management
          </h1>
          <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
            Manage employees and user access
          </p>
        </div>
        {onNavigateToCreate && (
          <button
            onClick={onNavigateToCreate}
            className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
            style={{ backgroundColor: '#7ed321' }}
          >
            + Add Employee
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <input
          type="text"
          placeholder="Search by name, employee #, email, or department..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        />
        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value as any)}
          className="px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        >
          <option value="all">All Status</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>
        <select
          value={filterHasLogin}
          onChange={(e) => setFilterHasLogin(e.target.value as any)}
          className="px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        >
          <option value="all">All Login Status</option>
          <option value="yes">Has Login</option>
          <option value="no">No Login</option>
        </select>
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
          <p className="text-sm" style={{ color: '#6b7280' }}>Loading employees...</p>
        </div>
      )}

      {/* Employees Table */}
      {!isLoading && !error && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="border-b" style={{ backgroundColor: '#f9fafb', borderColor: '#e5e7eb' }}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Employee
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Department
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Title
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Certifications
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Login Access
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: '#e5e7eb' }}>
              {filteredEmployees.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-sm" style={{ color: '#6b7280' }}>
                    {searchTerm || filterActive !== 'all' || filterHasLogin !== 'all'
                      ? 'No employees match your filters'
                      : 'No employees yet. Click "Add Employee" to get started.'}
                  </td>
                </tr>
              ) : (
                filteredEmployees.map((employee) => (
                  <tr key={employee.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium" style={{ color: '#111827' }}>
                          {employee.full_name}
                        </p>
                        <p className="text-xs" style={{ color: '#6b7280' }}>
                          {employee.employee_number}
                        </p>
                        {employee.email && (
                          <p className="text-xs" style={{ color: '#6b7280' }}>
                            {employee.email}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {employee.base_department_name}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                      {employee.title || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#6b7280' }}>
                      {employee.certifications && employee.certifications.length > 0 ? (
                        <div className="space-y-1">
                          {employee.certifications.map((cert, idx) => (
                            <div key={idx} className="text-xs">
                              {cert.standard}: {cert.cert_number}
                            </div>
                          ))}
                        </div>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {employee.has_user_account ? (
                        <div>
                          <span
                            className="px-2 py-1 text-xs font-medium rounded-full"
                            style={{
                              backgroundColor: employee.user_info?.is_active ? '#dcfce7' : '#fee2e2',
                              color: employee.user_info?.is_active ? '#166534' : '#991b1b',
                            }}
                          >
                            {employee.user_info?.is_active ? 'Active' : 'Inactive'}
                          </span>
                          <p className="text-xs mt-1" style={{ color: '#6b7280' }}>
                            {employee.user_info?.username}
                          </p>
                        </div>
                      ) : (
                        <span className="text-xs" style={{ color: '#6b7280' }}>
                          No Access
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-1 text-xs font-medium rounded-full"
                        style={{
                          backgroundColor: employee.is_active ? '#dcfce7' : '#fee2e2',
                          color: employee.is_active ? '#166534' : '#991b1b',
                        }}
                      >
                        {employee.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => onNavigateToDetail && onNavigateToDetail(employee.id)}
                        className="text-sm font-medium hover:underline"
                        style={{ color: '#7ed321' }}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Count */}
      {!isLoading && !error && filteredEmployees.length > 0 && (
        <div className="mt-4 text-sm" style={{ color: '#6b7280' }}>
          Showing {filteredEmployees.length} of {employees.length} employees
        </div>
      )}
    </div>
  );
}
