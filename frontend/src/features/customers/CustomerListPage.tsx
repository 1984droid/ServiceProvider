/**
 * CustomerListPage
 *
 * Display list of customers with search and filter
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useEffect, useState } from 'react';
import { customersApi, type Customer } from '@/api/customers.api';

interface CustomerListPageProps {
  onNavigateToCreate: () => void;
  onNavigateToDetail: (customerId: string) => void;
}

export function CustomerListPage({ onNavigateToCreate, onNavigateToDetail }: CustomerListPageProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await customersApi.list();
      setCustomers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load customers');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.legal_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.usdot_number?.includes(searchTerm) ||
    customer.mc_number?.includes(searchTerm)
  );

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>
            Customers
          </h1>
          <p className="mt-1 text-sm" style={{ color: '#6b7280' }}>
            Manage your customer accounts
          </p>
        </div>
        <button
          onClick={onNavigateToCreate}
          className="px-4 py-2 text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
          style={{
            backgroundColor: '#7ed321',
            color: 'white',
          }}
        >
          + New Customer
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by name, USDOT, or MC number..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 text-sm border rounded-lg"
          style={{
            borderColor: '#e5e7eb',
            color: '#111827',
          }}
        />
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
          <p className="text-sm" style={{ color: '#6b7280' }}>Loading customers...</p>
        </div>
      )}

      {/* Customer Table */}
      {!isLoading && !error && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="border-b" style={{ backgroundColor: '#f9fafb', borderColor: '#e5e7eb' }}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  USDOT
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  MC Number
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Location
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Contact
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide" style={{ color: '#6b7280' }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ borderColor: '#e5e7eb' }}>
              {filteredCustomers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: '#6b7280' }}>
                    {searchTerm ? 'No customers match your search' : 'No customers yet. Create your first customer to get started.'}
                  </td>
                </tr>
              ) : (
                filteredCustomers.map((customer) => (
                  <tr
                    key={customer.id}
                    onClick={() => onNavigateToDetail(customer.id)}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium" style={{ color: '#111827' }}>
                          {customer.name}
                        </p>
                        {customer.legal_name && customer.legal_name !== customer.name && (
                          <p className="text-xs" style={{ color: '#6b7280' }}>
                            {customer.legal_name}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {customer.usdot_number || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: '#111827' }}>
                      {customer.mc_number || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm" style={{ color: '#111827' }}>
                        {customer.city && customer.state ? `${customer.city}, ${customer.state}` : '—'}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      {customer.primary_contact_name ? (
                        <p className="text-sm" style={{ color: '#111827' }}>
                          {customer.primary_contact_name}
                        </p>
                      ) : (
                        <span className="text-sm" style={{ color: '#6b7280' }}>—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigateToDetail(customer.id);
                        }}
                        className="text-sm font-medium hover:underline"
                        style={{ color: '#7ed321' }}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Customer Count */}
      {!isLoading && !error && filteredCustomers.length > 0 && (
        <div className="mt-4 text-sm" style={{ color: '#6b7280' }}>
          Showing {filteredCustomers.length} of {customers.length} customers
        </div>
      )}
    </div>
  );
}
