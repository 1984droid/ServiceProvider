/**
 * EmployeeCertificationsTab - Manage employee certifications
 *
 * Add, edit, and remove certifications
 */

import { useState } from 'react';

interface Certification {
  standard: string;
  cert_number: string;
  expiry: string;
  issued_by?: string;
  issued_date?: string;
}

interface EmployeeCertificationsTabProps {
  certifications: Certification[];
  onChange: (certs: Certification[]) => void;
}

const COMMON_STANDARDS = [
  'ANSI/SAIA A92.2',
  'ANSI/SAIA A92.5',
  'ANSI/SAIA A92.6',
  'ANSI/ALOIM A10.31',
  'ASE',
  'CDL',
];

export function EmployeeCertificationsTab({
  certifications,
  onChange,
}: EmployeeCertificationsTabProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCert, setNewCert] = useState<Certification>({
    standard: '',
    cert_number: '',
    expiry: '',
    issued_by: '',
    issued_date: '',
  });

  const handleAdd = () => {
    if (!newCert.standard || !newCert.cert_number || !newCert.expiry) {
      alert('Please fill in Standard, Cert Number, and Expiry Date');
      return;
    }

    onChange([...certifications, newCert]);
    setNewCert({
      standard: '',
      cert_number: '',
      expiry: '',
      issued_by: '',
      issued_date: '',
    });
    setShowAddForm(false);
  };

  const handleRemove = (index: number) => {
    onChange(certifications.filter((_, i) => i !== index));
  };

  const isExpired = (expiryDate: string) => {
    return new Date(expiryDate) < new Date();
  };

  const isExpiringSoon = (expiryDate: string) => {
    const expiry = new Date(expiryDate);
    const today = new Date();
    const daysUntilExpiry = Math.floor((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry > 0 && daysUntilExpiry <= 30;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Certifications</h3>
            <p className="mt-1 text-sm text-gray-600">
              Manage employee certifications for inspections and compliance
            </p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 text-sm font-medium text-white rounded"
            style={{ backgroundColor: '#7ed321' }}
          >
            {showAddForm ? 'Cancel' : '+ Add Certification'}
          </button>
        </div>

        {/* Add Certification Form */}
        {showAddForm && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">New Certification</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Standard <span className="text-red-500">*</span>
                </label>
                <select
                  value={newCert.standard}
                  onChange={(e) => setNewCert({ ...newCert, standard: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                >
                  <option value="">Select standard...</option>
                  {COMMON_STANDARDS.map((std) => (
                    <option key={std} value={std}>
                      {std}
                    </option>
                  ))}
                  <option value="OTHER">Other (enter below)</option>
                </select>
              </div>

              {newCert.standard === 'OTHER' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Custom Standard
                  </label>
                  <input
                    type="text"
                    value=""
                    onChange={(e) => setNewCert({ ...newCert, standard: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    placeholder="Enter standard name"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Certification Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newCert.cert_number}
                  onChange={(e) => setNewCert({ ...newCert, cert_number: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                  placeholder="e.g., A92-12345"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={newCert.expiry}
                  onChange={(e) => setNewCert({ ...newCert, expiry: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Issued By
                </label>
                <input
                  type="text"
                  value={newCert.issued_by}
                  onChange={(e) => setNewCert({ ...newCert, issued_by: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                  placeholder="Issuing organization"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Issued Date
                </label>
                <input
                  type="date"
                  value={newCert.issued_date}
                  onChange={(e) => setNewCert({ ...newCert, issued_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={handleAdd}
                className="px-4 py-2 text-sm font-medium text-white rounded"
                style={{ backgroundColor: '#7ed321' }}
              >
                Add Certification
              </button>
            </div>
          </div>
        )}

        {/* Certifications List */}
        {certifications.length > 0 ? (
          <div className="space-y-3">
            {certifications.map((cert, index) => {
              const expired = isExpired(cert.expiry);
              const expiringSoon = !expired && isExpiringSoon(cert.expiry);

              return (
                <div
                  key={index}
                  className="bg-white rounded-lg shadow-sm border p-4"
                  style={{
                    borderColor: expired ? '#fca5a5' : expiringSoon ? '#fcd34d' : '#e5e7eb',
                    backgroundColor: expired ? '#fef2f2' : expiringSoon ? '#fffbeb' : 'white',
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-gray-900">
                          {cert.standard}
                        </h4>
                        {expired && (
                          <span className="px-2 py-0.5 text-xs font-medium text-red-700 bg-red-100 rounded">
                            EXPIRED
                          </span>
                        )}
                        {expiringSoon && (
                          <span className="px-2 py-0.5 text-xs font-medium text-yellow-700 bg-yellow-100 rounded">
                            EXPIRING SOON
                          </span>
                        )}
                      </div>

                      <div className="mt-1 space-y-1">
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Cert #:</span> {cert.cert_number}
                        </p>
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Expires:</span>{' '}
                          {new Date(cert.expiry).toLocaleDateString()}
                        </p>
                        {cert.issued_by && (
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Issued by:</span> {cert.issued_by}
                          </p>
                        )}
                        {cert.issued_date && (
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Issued on:</span>{' '}
                            {new Date(cert.issued_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => handleRemove(index)}
                      className="ml-4 text-sm text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <svg
              className="w-12 h-12 mx-auto text-gray-400 mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-sm font-medium text-gray-900">No certifications</p>
            <p className="mt-1 text-sm text-gray-600">
              Add certifications to enable inspection assignments
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
