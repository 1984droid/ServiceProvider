/**
 * API Configuration
 *
 * Central configuration for API endpoints and settings.
 */

export const API_CONFIG = {
  // Base URL - will use proxy in development, direct URL in production
  baseURL: import.meta.env.VITE_API_URL || '/api',

  // Timeout for API requests (in milliseconds)
  timeout: 30000,

  // JWT token keys in localStorage
  tokenKeys: {
    access: 'access_token',
    refresh: 'refresh_token',
  },

  // Endpoints
  endpoints: {
    // Authentication
    auth: {
      login: '/auth/login/',
      logout: '/auth/logout/',
      refresh: '/auth/refresh/',
      me: '/auth/me/',
      register: '/auth/register/',
      changePassword: '/auth/change-password/',
      users: '/auth/users/',
    },
    // Customers
    customers: {
      list: '/customers/',
      detail: (id: string) => `/customers/${id}/`,
      contacts: (id: string) => `/customers/${id}/contacts/`,
      setPrimaryContact: (id: string) => `/customers/${id}/set_primary_contact/`,
      searchByUSDOT: '/customers/search_by_usdot/',
    },
    // Contacts
    contacts: {
      list: '/contacts/',
      detail: (id: string) => `/contacts/${id}/`,
      makePrimary: (id: string) => `/contacts/${id}/make_primary/`,
    },
    // USDOT Profiles
    usdotProfiles: {
      list: '/usdot-profiles/',
      detail: (id: string) => `/usdot-profiles/${id}/`,
      lookupByUSDOT: '/usdot-profiles/lookup_by_usdot/',
      copyToCustomer: (id: string) => `/usdot-profiles/${id}/copy_to_customer/`,
    },
    // Assets
    assets: {
      list: '/assets/',
      detail: (id: string) => `/assets/${id}/`,
    },
    // Inspections
    inspections: {
      list: '/inspections/',
      detail: (id: string) => `/inspections/${id}/`,
      exportPDF: (id: string) => `/inspections/${id}/export_pdf/`,
      defects: (id: string) => `/inspections/${id}/defects/`,
      completion: (id: string) => `/inspections/${id}/completion/`,
    },
    // Work Orders
    workOrders: {
      list: '/work-orders/',
      detail: (id: string) => `/work-orders/${id}/`,
    },
    // Organization
    organization: {
      company: '/organization/companies/',
      currentCompany: '/organization/companies/current/',
      departments: '/organization/departments/',
      departmentDetail: (id: string) => `/organization/departments/${id}/`,
      departmentEmployees: (id: string) => `/organization/departments/${id}/employees/`,
      employees: '/organization/employees/',
      employeeDetail: (id: string) => `/organization/employees/${id}/`,
      activeEmployees: '/organization/employees/active/',
      canWorkIn: (id: string) => `/organization/employees/${id}/can_work_in/`,
    },
  },
} as const;

// Type-safe environment variables
declare global {
  interface ImportMetaEnv {
    VITE_API_URL?: string;
  }
}
