/**
 * EmployeeFormPage
 *
 * Create or edit employee with certification management
 */

import { useState, useEffect } from 'react';
import { employeesApi, type Employee, type CreateEmployeeRequest } from '@/api/employees.api';
import { departmentsApi, type Department } from '@/api/departments.api';

interface EmployeeFormPageProps {
  employeeId?: string;
  onSuccess: () => void;
  onCancel: () => void;
}

interface CertificationForm {
  standard: string;
  cert_number: string;
  expiry: string;
  issued_by?: string;
  issued_date?: string;
}

const COMMON_STANDARDS = [
  'ANSI/SAIA A92.2',
  'ANSI/SAIA A92.5',
  'ANSI/SAIA A92.6',
  'ANSI/ALOIM A10.31',
  'ASE',
  'CDL',
];

export function EmployeeFormPage({
  employeeId,
  onSuccess,
  onCancel,
}: EmployeeFormPageProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);

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

  const [certifications, setCertifications] = useState<CertificationForm[]>([]);
  const [showAddCert, setShowAddCert] = useState(false);
  const [newCert, setNewCert] = useState<CertificationForm>({
    standard: '',
    cert_number: '',
    expiry: '',
    issued_by: '',
    issued_date: '',
  });

  useEffect(() => {
    loadDepartments();
    if (employeeId) {
      loadEmployee();
    }
  }, [employeeId]);

  const loadDepartments = async () => {
    try {
      const data = await departmentsApi.list({ is_active: true });
      setDepartments(data);
    } catch (err: any) {
      console.error('Failed to load departments:', err);
    }
  };

  const loadEmployee = async () => {
    if (!employeeId) return;

    setIsLoading(true);
    setError(null);
    try {
      const employee = await employeesApi.get(employeeId);
      setFormData({
        employee_number: employee.employee_number,
        first_name: employee.first_name,
        last_name: employee.last_name,
        email: employee.email || '',
        phone: employee.phone || '',
        base_department: employee.base_department,
        floating_departments: employee.floating_departments,
        title: employee.title || '',
        hire_date: employee.hire_date || '',
        certifications: employee.certifications || [],
        skills: employee.skills || [],
      });
      setCertifications(employee.certifications || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load employee');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      const data = {
        ...formData,
        certifications,
      };

      if (employeeId) {
        await employeesApi.update(employeeId, data);
      } else {
        await employeesApi.create(data);
      }

      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to save employee');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddCertification = () => {
    if (!newCert.standard || !newCert.cert_number || !newCert.expiry) {
      alert('Please fill in Standard, Cert Number, and Expiry Date');
      return;
    }

    setCertifications([...certifications, newCert]);
    setNewCert({
      standard: '',
      cert_number: '',
      expiry: '',
      issued_by: '',
      issued_date: '',
    });
    setShowAddCert(false);
  };

  const handleRemoveCertification = (index: number) => {
    setCertifications(certifications.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-sm text-gray-600">Loading employee...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
          {employeeId ? 'Edit Employee' : 'Add Employee'}
        </h1>
        <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
          {employeeId ? 'Update employee information and certifications' : 'Create a new employee record'}
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="font-medium" style={{ color: '#dc2626' }}>
            {error}
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4" style={{ color: '#111827' }}>
              Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Employee Number *
                </label>
                <input
                  type="text"
                  required
                  value={formData.employee_number}
                  onChange={(e) => setFormData({ ...formData, employee_number: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Department *
                </label>
                <select
                  required
                  value={formData.base_department}
                  onChange={(e) => setFormData({ ...formData, base_department: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                >
                  <option value="">Select department...</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  First Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Last Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                  placeholder="e.g., Service Technician"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                  Hire Date
                </label>
                <input
                  type="date"
                  value={formData.hire_date}
                  onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  style={{ borderColor: '#e5e7eb' }}
                />
              </div>
            </div>
          </div>

          {/* Certifications */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold" style={{ color: '#111827' }}>
                Certifications
              </h3>
              <button
                type="button"
                onClick={() => setShowAddCert(!showAddCert)}
                className="px-3 py-1.5 text-sm font-medium text-white rounded transition-colors"
                style={{ backgroundColor: '#7ed321' }}
              >
                {showAddCert ? 'Cancel' : '+ Add Certification'}
              </button>
            </div>

            {/* Add Certification Form */}
            {showAddCert && (
              <div className="mb-4 p-4 rounded-lg border" style={{ borderColor: '#e5e7eb', backgroundColor: '#f9fafb' }}>
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                      Standard *
                    </label>
                    <select
                      value={newCert.standard}
                      onChange={(e) => setNewCert({ ...newCert, standard: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      style={{ borderColor: '#e5e7eb' }}
                    >
                      <option value="">Select standard...</option>
                      {COMMON_STANDARDS.map((std) => (
                        <option key={std} value={std}>
                          {std}
                        </option>
                      ))}
                      <option value="OTHER">Other (specify below)</option>
                    </select>
                  </div>
                  {newCert.standard === 'OTHER' && (
                    <div>
                      <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                        Custom Standard
                      </label>
                      <input
                        type="text"
                        value={newCert.standard === 'OTHER' ? '' : newCert.standard}
                        onChange={(e) => setNewCert({ ...newCert, standard: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg"
                        style={{ borderColor: '#e5e7eb' }}
                      />
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                      Cert Number *
                    </label>
                    <input
                      type="text"
                      value={newCert.cert_number}
                      onChange={(e) => setNewCert({ ...newCert, cert_number: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      style={{ borderColor: '#e5e7eb' }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                      Expiry Date *
                    </label>
                    <input
                      type="date"
                      value={newCert.expiry}
                      onChange={(e) => setNewCert({ ...newCert, expiry: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      style={{ borderColor: '#e5e7eb' }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                      Issued By
                    </label>
                    <input
                      type="text"
                      value={newCert.issued_by}
                      onChange={(e) => setNewCert({ ...newCert, issued_by: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      style={{ borderColor: '#e5e7eb' }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>
                      Issued Date
                    </label>
                    <input
                      type="date"
                      value={newCert.issued_date}
                      onChange={(e) => setNewCert({ ...newCert, issued_date: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      style={{ borderColor: '#e5e7eb' }}
                    />
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleAddCertification}
                  className="px-4 py-2 text-sm font-medium text-white rounded transition-colors"
                  style={{ backgroundColor: '#7ed321' }}
                >
                  Add Certification
                </button>
              </div>
            )}

            {/* Certifications List */}
            {certifications.length > 0 ? (
              <div className="space-y-2">
                {certifications.map((cert, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg border flex items-center justify-between"
                    style={{ borderColor: '#e5e7eb', backgroundColor: '#f9fafb' }}
                  >
                    <div>
                      <p className="text-sm font-medium" style={{ color: '#111827' }}>
                        {cert.standard} - {cert.cert_number}
                      </p>
                      <p className="text-xs" style={{ color: '#6b7280' }}>
                        Expires: {new Date(cert.expiry).toLocaleDateString()}
                        {cert.issued_by && ` • Issued by: ${cert.issued_by}`}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveCertification(index)}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: '#6b7280' }}>
                No certifications added yet
              </p>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex gap-3 pt-4 border-t" style={{ borderColor: '#e5e7eb' }}>
            <button
              type="button"
              onClick={onCancel}
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
              style={{ backgroundColor: '#7ed321' }}
            >
              {isSaving ? 'Saving...' : employeeId ? 'Save Changes' : 'Create Employee'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
