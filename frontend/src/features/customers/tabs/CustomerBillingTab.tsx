/**
 * CustomerBillingTab - Billing and invoice information (stub)
 *
 * Shows:
 * - Account balance
 * - Recent invoices
 * - Payment history
 * - Billing preferences
 *
 * NOTE: This is a stub. Backend billing system not yet implemented.
 */

import type { CustomerDetail } from '@/api/customers.api';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { StatCard } from '@/components/ui/StatCard';

interface CustomerBillingTabProps {
  customer: CustomerDetail;
}

export function CustomerBillingTab({ customer }: CustomerBillingTabProps) {
  // TODO: When billing system is implemented:
  // - Fetch account balance from backend
  // - Fetch recent invoices
  // - Fetch payment history
  // - Fetch billing preferences

  return (
    <div className="space-y-6">
      {/* Account Summary (Stub) */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Account Balance"
          value="$0.00"
          subtitle="Current balance"
          variant="default"
        />
        <StatCard
          label="Total Invoiced"
          value="$0.00"
          subtitle="All time"
          variant="info"
        />
        <StatCard
          label="Total Paid"
          value="$0.00"
          subtitle="All time"
          variant="success"
        />
        <StatCard
          label="Outstanding"
          value="$0.00"
          subtitle="Unpaid invoices"
          variant="warning"
        />
      </div>

      {/* Coming Soon Message */}
      <div className="flex items-center justify-center h-64">
        <div className="text-center max-w-md">
          <svg className="w-16 h-16 mx-auto text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-4 text-base font-semibold text-gray-900">Billing System Coming Soon</h3>
          <p className="mt-2 text-sm text-gray-600">
            Invoice management, payment tracking, and account balances will be available here once the billing system is implemented.
          </p>
          <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
            <p className="text-xs" style={{ color: '#166534' }}>
              <strong>Planned features:</strong> Invoice generation, payment history, account statements, billing preferences, automated payment reminders
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
