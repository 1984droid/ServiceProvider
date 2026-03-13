/**
 * ContactDetailPage - View detailed information about a contact
 *
 * Features:
 * - Overview tab with contact information
 * - Portal Access tab (for future customer portal)
 * - Activity tab (placeholder for future activity tracking)
 */

import { useState, useEffect, useRef } from 'react';
import type { Contact } from '@/api/customers.api';
import { customersApi } from '@/api/customers.api';
import { TabNavigation } from '@/components/ui/TabNavigation';
import type { Tab } from '@/components/ui/TabNavigation';
import { ContactOverviewTab } from './tabs/ContactOverviewTab';
import { ContactPortalAccessTab } from './tabs/ContactPortalAccessTab';
import { ContactActivityTab } from './tabs/ContactActivityTab';

type ContactTab = 'overview' | 'portal-access' | 'activity';

interface ContactDetailPageProps {
  contactId: string;
  onNavigateBack: () => void;
  onNavigateToCustomer: (customerId: string) => void;
  onEdit: (contactId: string) => void;
}

export function ContactDetailPage({
  contactId,
  onNavigateBack,
  onNavigateToCustomer,
  onEdit,
}: ContactDetailPageProps) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ContactTab>('overview');
  const [contentHeight, setContentHeight] = useState<number>(0);

  const headerRef = useRef<HTMLDivElement>(null);
  const tabsRef = useRef<HTMLDivElement>(null);

  const tabs: Tab[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'portal-access', label: 'Portal Access' },
    { key: 'activity', label: 'Activity' },
  ];

  useEffect(() => {
    loadContact();
  }, [contactId]);

  useEffect(() => {
    const calculateHeight = () => {
      setTimeout(() => {
        const navbarHeight = 64;
        const header = document.querySelector('.contact-detail-header') as HTMLElement;
        const tabNav = document.querySelector('.contact-detail-tabs') as HTMLElement;
        const headerHeight = header?.offsetHeight || 0;
        const tabsHeight = tabNav?.offsetHeight || 0;
        const padding = 48; // 24px top + 24px bottom

        const availableHeight = window.innerHeight - navbarHeight - headerHeight - tabsHeight - padding;
        setContentHeight(availableHeight);
      }, 150);
    };

    calculateHeight();
    window.addEventListener('resize', calculateHeight);
    return () => window.removeEventListener('resize', calculateHeight);
  }, [contact]);

  const loadContact = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await customersApi.getContact(contactId);
      setContact(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
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

  if (error || !contact) {
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
      <div ref={headerRef} className="contact-detail-header flex-shrink-0 px-6 py-4 border-b border-gray-200">
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
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">{contact.full_name}</h1>
                {contact.is_primary && (
                  <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800">
                    Primary
                  </span>
                )}
                {!contact.is_active && (
                  <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                    Inactive
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-0.5">
                {contact.title || 'No title'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onEdit(contact.id)}
              className="px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Edit Contact
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div ref={tabsRef} className="contact-detail-tabs flex-shrink-0 px-6">
        <TabNavigation
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={(key) => setActiveTab(key as ContactTab)}
        />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden px-6 pb-6 pt-6">
        <div style={{ height: `${contentHeight}px`, overflowY: 'auto' }}>
          {activeTab === 'overview' && (
            <ContactOverviewTab
              contact={contact}
              onNavigateToCustomer={onNavigateToCustomer}
              onDataRefreshed={loadContact}
            />
          )}
          {activeTab === 'portal-access' && (
            <ContactPortalAccessTab
              contact={contact}
              onDataRefreshed={loadContact}
            />
          )}
          {activeTab === 'activity' && (
            <ContactActivityTab contact={contact} />
          )}
        </div>
      </div>
    </div>
  );
}
