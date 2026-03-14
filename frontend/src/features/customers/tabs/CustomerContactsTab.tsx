/**
 * CustomerContactsTab - List of all contacts for customer
 *
 * Shows:
 * - Contact list with primary indicator
 * - Correspondence preferences
 * - Contact information
 */

import { useState } from 'react';
import type { CustomerDetail } from '@/api/customers.api';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { Badge } from '@/components/ui/Badge';
import { CorrespondenceIndicator } from '@/components/ui/CorrespondenceIndicator';
import { ContactUserAccessButton } from '../ContactUserAccessButton';

interface CustomerContactsTabProps {
  customer: CustomerDetail;
  onNavigateToContact?: (contactId: string) => void;
  onRefresh?: () => void;
}

export function CustomerContactsTab({ customer, onNavigateToContact, onRefresh }: CustomerContactsTabProps) {
  const activeContacts = customer.contacts.filter(c => c.is_active);
  const inactiveContacts = customer.contacts.filter(c => !c.is_active);

  if (customer.contacts.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts</h3>
          <p className="mt-1 text-sm text-gray-500">This customer has no contacts yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Contacts */}
      {activeContacts.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <SectionHeader title={`Active Contacts (${activeContacts.length})`} />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact Info
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Correspondence
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Portal Access
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeContacts.map(contact => (
                  <tr
                    key={contact.id}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onNavigateToContact?.(contact.id)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">
                          {contact.full_name}
                        </span>
                        {contact.is_primary && (
                          <Badge label="Primary" variant="success" size="sm" />
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{contact.title || '—'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-700 space-y-0.5">
                        {contact.email && (
                          <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <span className="text-xs">{contact.email}</span>
                          </div>
                        )}
                        {contact.phone && (
                          <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            <span className="text-xs">
                              {contact.phone}
                              {contact.phone_extension && ` ext. ${contact.phone_extension}`}
                            </span>
                          </div>
                        )}
                        {contact.mobile && (
                          <div className="flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                            <span className="text-xs">{contact.mobile}</span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <CorrespondenceIndicator
                        subscriptions={{
                          invoices: contact.receive_invoices,
                          estimates: contact.receive_estimates,
                          service_updates: contact.receive_service_updates,
                          inspection_reports: contact.receive_inspection_reports,
                        }}
                      />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {contact.is_automated ? (
                        <Badge label="Automated" variant="info" size="sm" />
                      ) : (
                        <span className="text-xs text-gray-500">Person</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <ContactUserAccessButton
                        contact={contact}
                        onSuccess={() => onRefresh?.()}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Inactive Contacts */}
      {inactiveContacts.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <SectionHeader title={`Inactive Contacts (${inactiveContacts.length})`} />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact Info
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Portal Access
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inactiveContacts.map(contact => (
                  <tr
                    key={contact.id}
                    className="opacity-60 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onNavigateToContact?.(contact.id)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-700">{contact.full_name}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-500">{contact.title || '—'}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-xs text-gray-500 space-y-0.5">
                        {contact.email && <div>{contact.email}</div>}
                        {contact.phone && <div>{contact.phone}</div>}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <ContactUserAccessButton
                        contact={contact}
                        onSuccess={() => onRefresh?.()}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
