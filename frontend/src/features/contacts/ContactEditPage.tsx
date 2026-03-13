/**
 * ContactEditPage - Edit contact information
 */

import { useState, useEffect } from 'react';
import type { Contact } from '@/api/customers.api';
import { customersApi } from '@/api/customers.api';

interface ContactEditPageProps {
  contactId: string;
  onNavigateBack: () => void;
  onSaveComplete: (contactId: string) => void;
}

export function ContactEditPage({
  contactId,
  onNavigateBack,
  onSaveComplete,
}: ContactEditPageProps) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    title: '',
    email: '',
    phone: '',
    phone_extension: '',
    mobile: '',
    is_active: true,
    is_automated: false,
    is_primary: false,
    receive_invoices: false,
    receive_estimates: false,
    receive_service_updates: false,
    receive_inspection_reports: false,
    notes: '',
  });

  useEffect(() => {
    loadContact();
  }, [contactId]);

  const loadContact = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await customersApi.getContact(contactId);
      setContact(data);
      setFormData({
        first_name: data.first_name,
        last_name: data.last_name,
        title: data.title || '',
        email: data.email || '',
        phone: data.phone || '',
        phone_extension: data.phone_extension || '',
        mobile: data.mobile || '',
        is_active: data.is_active,
        is_automated: data.is_automated,
        is_primary: data.is_primary,
        receive_invoices: data.receive_invoices,
        receive_estimates: data.receive_estimates,
        receive_service_updates: data.receive_service_updates,
        receive_inspection_reports: data.receive_inspection_reports,
        notes: data.notes || '',
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationErrors({});

    // Basic validation
    const errors: Record<string, string> = {};
    if (!formData.first_name.trim()) {
      errors.first_name = 'First name is required';
    }
    if (!formData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }
    if (formData.email && !formData.email.includes('@')) {
      errors.email = 'Please enter a valid email address';
    }

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await customersApi.updateContact(contactId, formData);
      onSaveComplete(contactId);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update contact');
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
          <p className="mt-2 text-sm text-gray-600">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (error && !contact) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading contact</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
          <button
            onClick={onNavigateBack}
            className="mt-4 px-4 py-2 text-sm font-medium text-white rounded"
            style={{ backgroundColor: '#7ed321' }}
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onNavigateBack}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              aria-label="Go back"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Contact</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                {contact?.full_name}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <form onSubmit={handleSubmit} className="max-w-4xl space-y-6">
          {error && (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">Basic Information</h2>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                  First Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-offset-0 ${
                    validationErrors.first_name ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                  }`}
                />
                {validationErrors.first_name && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.first_name}</p>
                )}
              </div>
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-offset-0 ${
                    validationErrors.last_name ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                  }`}
                />
                {validationErrors.last_name && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.last_name}</p>
                )}
              </div>
              <div className="col-span-2">
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
                  placeholder="e.g., Fleet Manager"
                />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">Contact Information</h2>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className={`w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-offset-0 ${
                    validationErrors.email ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
                  }`}
                />
                {validationErrors.email && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.email}</p>
                )}
              </div>
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
                />
              </div>
              <div>
                <label htmlFor="phone_extension" className="block text-sm font-medium text-gray-700 mb-1">
                  Extension
                </label>
                <input
                  type="text"
                  id="phone_extension"
                  value={formData.phone_extension}
                  onChange={(e) => handleChange('phone_extension', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
                />
              </div>
              <div className="col-span-2">
                <label htmlFor="mobile" className="block text-sm font-medium text-gray-700 mb-1">
                  Mobile
                </label>
                <input
                  type="tel"
                  id="mobile"
                  value={formData.mobile}
                  onChange={(e) => handleChange('mobile', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
                />
              </div>
            </div>
          </div>

          {/* Status & Preferences */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">Status & Preferences</h2>
            <div className="space-y-2">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => handleChange('is_active', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Active Contact</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.is_automated}
                  onChange={(e) => handleChange('is_automated', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div>
                  <span className="text-sm text-gray-700">Automated System</span>
                  <p className="text-xs text-gray-500 mt-0.5">Check if this is an automated email system rather than a person</p>
                </div>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.is_primary}
                  onChange={(e) => handleChange('is_primary', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Primary Contact</span>
              </label>
            </div>
          </div>

          {/* Correspondence Preferences */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">Correspondence Preferences</h2>
            <div className="space-y-2">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.receive_invoices}
                  onChange={(e) => handleChange('receive_invoices', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Receive Invoices</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.receive_estimates}
                  onChange={(e) => handleChange('receive_estimates', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Receive Estimates</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.receive_service_updates}
                  onChange={(e) => handleChange('receive_service_updates', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Receive Service Updates</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={formData.receive_inspection_reports}
                  onChange={(e) => handleChange('receive_inspection_reports', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Receive Inspection Reports</span>
              </label>
            </div>
          </div>

          {/* Notes */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">Notes</h2>
            <textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
              placeholder="Additional notes about this contact..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onNavigateBack}
              disabled={saving}
              className="px-6 py-2.5 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
              style={{ backgroundColor: '#7ed321' }}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
