# Frontend Development Roadmap

**ServiceProvider Application - React + TypeScript Frontend**

Last Updated: 2026-03-13

---

## 📊 Current State Overview

### ✅ Completed Features

#### **Core Infrastructure**
- [x] Authentication system with JWT
- [x] Auth store (Zustand)
- [x] API client setup (axios with interceptors)
- [x] Clean dashboard layout with collapsible sidebar
- [x] Hash-based routing system
- [x] Responsive design with viewport height tracking
- [x] Theme configuration
- [x] React Query setup

#### **Customers Module** - ✅ COMPLETE
- [x] `CustomerListPage.tsx` - List with search/filter
- [x] `CustomerDetailPage.tsx` - Detail with tabbed interface
- [x] `CustomerCreatePage.tsx` - Create new customer
- [x] `CustomerForm.tsx` - Reusable form component
- [x] `USDOTSearch.tsx` - USDOT/MC number lookup
- [x] **Tabs:**
  - [x] `CustomerOverviewTab.tsx` - Basic info, stats
  - [x] `CustomerAssetsTab.tsx` - Vehicles/equipment list
  - [x] `CustomerContactsTab.tsx` - Contact management
  - [x] `CustomerBillingTab.tsx` - Billing information
  - [x] `CustomerUSDOTTab.tsx` - USDOT compliance data

#### **Contacts Module** - ✅ COMPLETE
- [x] `ContactDetailPage.tsx` - Contact details with tabs
- [x] `ContactEditPage.tsx` - Edit contact information
- [x] **Tabs:**
  - [x] `ContactOverviewTab.tsx` - Basic info
  - [x] `ContactActivityTab.tsx` - Activity history
  - [x] `ContactPortalAccessTab.tsx` - Portal permissions

#### **Assets Module** - ✅ MOSTLY COMPLETE
- [x] `AssetsListPage.tsx` - Unified vehicle/equipment list
- [x] `VehicleCreatePage.tsx` - Create vehicle with VIN search
- [x] `VehicleDetailPage.tsx` - Vehicle details with tabs
- [x] `EquipmentDetailPage.tsx` - Equipment details with tabs
- [x] `VehicleForm.tsx` - Complete vehicle form
- [x] `VINSearch.tsx` - VIN decoder integration
- [x] **Tabs:**
  - [x] `VehicleOverviewTab.tsx` - Vehicle info
  - [x] `VehicleVINDecodeTab.tsx` - VIN decode results
  - [x] `EquipmentOverviewTab.tsx` - Equipment info
- [x] **API:**
  - [x] `vin.api.ts` - FMCSA VIN decoding
  - [x] `assets.api.ts` - Asset CRUD operations

#### **Inspections Module** - ⚠️ PARTIAL (30% Complete)
- [x] `InspectionsListPage.tsx` - List inspections with filtering
- [x] `CreateInspectionModal.tsx` - Create inspection from asset
- [x] Template filtering by asset type
- [ ] **MISSING:** Inspection execution workflow ❌
- [ ] **MISSING:** Inspection detail/results page ❌
- [ ] **MISSING:** PDF viewing/download ❌

#### **Reusable Components**
- [x] `TextInput.tsx` - Text input atom
- [x] `TextArea.tsx` - Textarea atom
- [x] `Select.tsx` - Select dropdown atom
- [x] `FormField.tsx` - Form field molecule
- [x] `Badge.tsx` - Status badges
- [x] `StatCard.tsx` - Dashboard stat cards
- [x] `InfoSection.tsx` - Info display sections
- [x] `SectionHeader.tsx` - Section headers
- [x] `TabNavigation.tsx` - Tab navigation
- [x] `CorrespondenceIndicator.tsx` - Email/activity indicators

#### **API Clients**
- [x] `auth.api.ts` - Authentication
- [x] `customers.api.ts` - Customer operations
- [x] `assets.api.ts` - Asset operations
- [x] `inspections.api.ts` - Inspection operations
- [x] `usdot.api.ts` - USDOT lookup
- [x] `vin.api.ts` - VIN decoding

---

## ❌ Missing Features (To Be Built)

### 🔴 **CRITICAL - Phase 1: Inspection Execution** (Weeks 1-3)

This is the **core value proposition** of the application. Without this, inspectors cannot perform inspections!

#### 1.1 Inspection Execution Engine
**Priority:** 🔴 CRITICAL | **Effort:** Large (40-50 hours)

**New Files:**
```
features/inspections/
├── InspectionExecutePage.tsx          # Main execution page
├── InspectionProgressBar.tsx          # Progress indicator
├── InspectionStepper.tsx              # Step-by-step wizard
├── hooks/
│   ├── useInspectionExecution.ts      # Execution state management
│   ├── useAutoSave.ts                 # Auto-save draft hook
│   └── useStepValidation.ts           # Step validation logic
└── validation/
    └── inspectionValidators.ts        # Field validation rules
```

**Features:**
- [ ] Load template and initialize inspection run
- [ ] Step-by-step wizard navigation
- [ ] Progress tracking (X of Y steps)
- [ ] Auto-save draft every 30 seconds
- [ ] Handle browser refresh (restore from draft)
- [ ] "Save & Exit" functionality
- [ ] "Previous" / "Next" navigation
- [ ] "Complete Inspection" final submission
- [ ] Blocking steps (can't proceed if failed)
- [ ] Template input handling (conditional steps)

**Technical Details:**
- State management: React Query + local state
- Auto-save: Debounced API calls
- Validation: Per-step validation using template schema
- Navigation: Block navigation if unsaved changes

---

#### 1.2 Dynamic Step Rendering
**Priority:** 🔴 CRITICAL | **Effort:** Large (30-40 hours)

**New Files:**
```
features/inspections/steps/
├── StepRenderer.tsx                   # Main step router
├── SetupStep.tsx                      # SETUP step type
├── VisualInspectionStep.tsx           # VISUAL_INSPECTION step type
├── FunctionTestStep.tsx               # FUNCTION_TEST step type
├── MeasurementStep.tsx                # MEASUREMENT step type
├── DefectCaptureStep.tsx              # DEFECT_CAPTURE step type
└── StepHeader.tsx                     # Common step header
```

**Features:**
- [ ] Route to correct component based on `step.type`
- [ ] Display step title, standard reference
- [ ] Show step instructions/guidance
- [ ] Handle step-level `blocking_fail`
- [ ] Display `required` indicator
- [ ] Conditional visibility based on `visibility_conditions`
- [ ] Auto-defect triggering based on field values

**Step Type Mapping:**
```typescript
{
  SETUP: <SetupStep />,
  VISUAL_INSPECTION: <VisualInspectionStep />,
  FUNCTION_TEST: <FunctionTestStep />,
  MEASUREMENT: <MeasurementStep />,
  DEFECT_CAPTURE: <DefectCaptureStep />
}
```

---

#### 1.3 Dynamic Field Rendering
**Priority:** 🔴 CRITICAL | **Effort:** Large (30-40 hours)

**New Files:**
```
features/inspections/fields/
├── FieldRenderer.tsx                  # Main field router
├── TextField.tsx                      # TEXT field type
├── TextAreaField.tsx                  # TEXT_AREA field type
├── NumberField.tsx                    # NUMBER field type
├── BooleanField.tsx                   # BOOLEAN field type
├── DateField.tsx                      # DATE field type
├── EnumField.tsx                      # ENUM field type (dropdown/radio)
├── PhotoField.tsx                     # PHOTO field type
└── FieldLabel.tsx                     # Common field label with required indicator
```

**Features:**
- [ ] Route to correct input based on `field.type`
- [ ] Display field label and help text
- [ ] Show required indicator (`*`)
- [ ] Validate based on field constraints:
  - [ ] `required` - must have value
  - [ ] `min` / `max` - numeric bounds
  - [ ] `precision` - decimal places for numbers
  - [ ] `enum_ref` - validate against enum values
- [ ] Real-time validation with error display
- [ ] Support for `enum` fields (dropdown or radio buttons)
- [ ] Photo capture/upload for PHOTO fields

**Field Type Support:**
- TEXT ✅
- TEXT_AREA ✅
- NUMBER (with min/max/precision)
- BOOLEAN (checkbox or toggle)
- DATE (date picker)
- ENUM (dropdown from template.enums)
- PHOTO (camera capture + file upload)
- ATTACHMENTS (multiple file upload)

---

#### 1.4 Photo Capture & Upload
**Priority:** 🔴 CRITICAL | **Effort:** Medium (15-20 hours)

**New Files:**
```
components/
├── PhotoCapture/
│   ├── PhotoCapture.tsx               # Main photo component
│   ├── CameraCapture.tsx              # Use device camera
│   ├── FileUpload.tsx                 # Upload from device
│   ├── PhotoPreview.tsx               # Preview captured photo
│   └── PhotoGallery.tsx               # Multiple photos for defects
```

**Features:**
- [ ] Mobile camera access (getUserMedia API)
- [ ] File upload fallback
- [ ] Image preview before submission
- [ ] Resize/compress images (max 2MB per photo)
- [ ] Multiple photos per field/defect
- [ ] Delete photo
- [ ] Photo metadata (timestamp, GPS if available)
- [ ] Upload progress indicator
- [ ] Error handling (camera permission denied, upload failed)

**Technical Details:**
- Use native camera API for mobile
- Compress images client-side (browser-image-compression)
- Upload to backend `/api/inspections/{id}/upload-photo/`
- Store photo URLs in inspection responses

---

#### 1.5 Defect Capture Workflow
**Priority:** 🔴 CRITICAL | **Effort:** Medium (20-25 hours)

**New Files:**
```
features/inspections/defects/
├── DefectCaptureForm.tsx              # Record new defect
├── DefectList.tsx                     # List defects in inspection
├── DefectSeveritySelector.tsx         # Select severity (SAFE, MINOR, etc.)
├── DefectPhotoGallery.tsx             # Defect photos
└── AutoDefectIndicator.tsx            # Show auto-generated defects
```

**Features:**
- [ ] Manual defect entry (title, description, severity)
- [ ] Auto-defect generation from rules
- [ ] Defect photos (multiple per defect)
- [ ] Standard reference linking
- [ ] Severity selection (from template enum)
- [ ] Location/component field
- [ ] Edit/delete defects
- [ ] Review all defects before completing inspection
- [ ] Mark defect as "blocks inspection" (UNSAFE)

**Defect Fields:**
- Title (required)
- Description (TEXT_AREA)
- Severity (ENUM: SAFE, MINOR, SERVICE_REQUIRED, UNSAFE_OUT_OF_SERVICE)
- Standard reference
- Component/location
- Photos (multiple)
- Created by inspector
- Auto-generated flag

---

### 🟡 **HIGH PRIORITY - Phase 2: Inspection Results** (Weeks 4-5)

#### 2.1 Inspection Detail/Results Page
**Priority:** 🟡 HIGH | **Effort:** Medium (20-25 hours)

**New Files:**
```
features/inspections/
├── InspectionDetailPage.tsx           # Main detail page
├── InspectionResultsTab.tsx           # Results overview
├── InspectionPhotosTab.tsx            # All photos
├── InspectionDefectsTab.tsx           # All defects
├── InspectionHistoryTab.tsx           # Audit trail
└── InspectionPDFTab.tsx               # PDF viewer
```

**Features:**
- [ ] Display inspection metadata (inspector, date, asset, customer)
- [ ] Show pass/fail status
- [ ] Display all step responses
- [ ] Group by step
- [ ] Show photos inline
- [ ] List all defects with severity badges
- [ ] Download PDF report
- [ ] Email PDF to customer
- [ ] Print inspection
- [ ] View audit history (created, modified, completed times)

---

#### 2.2 PDF Viewing & Download
**Priority:** 🟡 HIGH | **Effort:** Small (8-10 hours)

**New Files:**
```
features/inspections/
├── PDFViewer.tsx                      # Embedded PDF viewer
└── PDFDownloadButton.tsx              # Download with loading state
```

**Features:**
- [ ] Embed PDF viewer (react-pdf or iframe)
- [ ] Download PDF button
- [ ] Email PDF button (triggers backend email)
- [ ] Print PDF button
- [ ] Loading states
- [ ] Error handling (PDF generation failed)
- [ ] Mobile-friendly PDF viewing

---

### 🟢 **MEDIUM PRIORITY - Phase 3: Work Orders** (Weeks 6-7)

Work orders module is currently **completely missing** (empty directory).

#### 3.1 Work Orders List Page
**Priority:** 🟢 MEDIUM | **Effort:** Medium (15-20 hours)

**New Files:**
```
features/work-orders/
├── WorkOrdersListPage.tsx             # List page
├── WorkOrderCard.tsx                  # Individual work order card
└── WorkOrderFilters.tsx               # Filter controls
```

**Features:**
- [ ] List all work orders
- [ ] Search by WO number, customer, asset
- [ ] Filter by status (DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)
- [ ] Filter by priority
- [ ] Sort by due date, created date, priority
- [ ] Click to view detail
- [ ] Create new work order button
- [ ] Pagination

---

#### 3.2 Work Order Detail Page
**Priority:** 🟢 MEDIUM | **Effort:** Medium (20-25 hours)

**New Files:**
```
features/work-orders/
├── WorkOrderDetailPage.tsx            # Main detail page
├── WorkOrderOverviewTab.tsx           # Basic info
├── WorkOrderDefectsTab.tsx            # Linked defects
├── WorkOrderPartsTab.tsx              # Parts used
├── WorkOrderLaborTab.tsx              # Labor hours
└── WorkOrderNotesTab.tsx              # Technician notes
```

**Features:**
- [ ] Display work order details
- [ ] Show linked defects from inspections
- [ ] Parts used tracking
- [ ] Labor hours tracking
- [ ] Status updates
- [ ] Assigned technicians
- [ ] Due date
- [ ] Priority
- [ ] Customer approval status
- [ ] Edit work order
- [ ] Delete work order
- [ ] Mark complete

---

#### 3.3 Create Work Order from Defect
**Priority:** 🟢 MEDIUM | **Effort:** Medium (15-20 hours)

**New Files:**
```
features/work-orders/
├── WorkOrderCreatePage.tsx            # Create page
├── WorkOrderForm.tsx                  # Reusable form
└── DefectWorkOrderLinking.tsx         # Link defects to WO
```

**Features:**
- [ ] Create from inspection defect (one-click)
- [ ] Auto-populate customer, asset from defect
- [ ] Link multiple defects to one work order
- [ ] Set priority based on defect severity
- [ ] Schedule work order
- [ ] Assign technicians
- [ ] Add parts/labor estimates
- [ ] Customer request variant

---

### 🔵 **LOW PRIORITY - Phase 4: Polish & Enhancement** (Weeks 8-10)

#### 4.1 Dashboard Widgets
**Priority:** 🔵 LOW | **Effort:** Medium (15-20 hours)

**New Files:**
```
features/dashboard/
├── DashboardPage.tsx                  # Replace placeholder
├── RecentInspectionsWidget.tsx        # Recent inspections
├── UpcomingWorkOrdersWidget.tsx       # Upcoming work
├── StatsOverview.tsx                  # Key metrics
└── QuickActions.tsx                   # Quick links
```

**Features:**
- [ ] Key stats (total customers, active inspections, pending WOs)
- [ ] Recent inspections (last 10)
- [ ] Upcoming work orders (due this week)
- [ ] Quick actions (create inspection, create WO, etc.)
- [ ] Inspector performance metrics (if admin)
- [ ] Charts (inspections over time, pass/fail ratio)

---

#### 4.2 Advanced Search & Filtering
**Priority:** 🔵 LOW | **Effort:** Small (8-10 hours)

**Features:**
- [ ] Global search (across customers, assets, inspections)
- [ ] Advanced filters (date ranges, multiple criteria)
- [ ] Saved searches
- [ ] Export search results to CSV
- [ ] Search suggestions/autocomplete

---

#### 4.3 Batch Operations
**Priority:** 🔵 LOW | **Effort:** Medium (12-15 hours)

**Features:**
- [ ] Bulk select inspections
- [ ] Bulk download PDFs
- [ ] Bulk email PDFs
- [ ] Bulk status updates
- [ ] Bulk delete

---

#### 4.4 Notifications & Alerts
**Priority:** 🔵 LOW | **Effort:** Medium (15-20 hours)

**New Files:**
```
features/notifications/
├── NotificationsPanel.tsx             # Notification dropdown
├── NotificationsList.tsx              # List notifications
└── NotificationSettings.tsx           # User preferences
```

**Features:**
- [ ] In-app notifications
- [ ] Inspection completed alerts
- [ ] Work order due reminders
- [ ] Defect severity alerts
- [ ] Notification preferences
- [ ] Mark as read
- [ ] Notification history

---

## 📐 Technical Architecture

### State Management Strategy

**Server State (React Query):**
- Inspections
- Customers
- Assets
- Work orders
- Templates

**Client State (Zustand):**
- Authentication
- Current inspection execution (steps, responses)
- UI state (sidebar collapsed, modals open)

**Local State (useState):**
- Form inputs
- Temporary UI state

### Component Organization

```
frontend/src/
├── api/                               # API clients
│   ├── auth.api.ts
│   ├── inspections.api.ts
│   └── ...
├── components/                        # Reusable components
│   ├── atoms/                         # Basic inputs
│   ├── molecules/                     # Composed components
│   ├── ui/                            # UI components
│   └── PhotoCapture/                  # Photo components
├── features/                          # Feature modules
│   ├── auth/
│   ├── customers/
│   ├── assets/
│   ├── inspections/                   # Largest module
│   │   ├── InspectionsListPage.tsx
│   │   ├── InspectionExecutePage.tsx  # NEW
│   │   ├── InspectionDetailPage.tsx   # NEW
│   │   ├── steps/                     # NEW
│   │   ├── fields/                    # NEW
│   │   ├── defects/                   # NEW
│   │   └── hooks/                     # NEW
│   ├── work-orders/                   # Needs everything
│   └── dashboard/                     # Needs overhaul
├── hooks/                             # Global hooks
├── lib/                               # Libraries
├── store/                             # Zustand stores
└── types/                             # TypeScript types
```

### API Integration Patterns

**Optimistic Updates:**
- Use for non-critical updates (status changes)
- Roll back on error

**Auto-save:**
- Debounce 30 seconds
- Save to draft endpoint
- Show "Saving..." / "Saved" indicator

**Error Handling:**
- Toast notifications for errors
- Inline validation errors
- Retry logic for network failures

### Performance Considerations

**Code Splitting:**
- Lazy load inspection execution page
- Lazy load work orders module
- Lazy load PDF viewer

**Image Optimization:**
- Compress photos to max 2MB
- Progressive image loading
- Lazy load images in galleries

**Caching:**
- Cache templates (rarely change)
- Cache customer/asset data
- Invalidate on mutations

---

## 🎯 Milestones & Timeline

### **Milestone 1: Core Inspection Execution** (Weeks 1-3)
**Goal:** Inspectors can perform inspections end-to-end

- [ ] Inspection execution page with step navigation
- [ ] All field types rendering correctly
- [ ] Photo capture working
- [ ] Defect capture working
- [ ] Save draft & complete inspection
- [ ] Auto-save functionality

**Success Criteria:**
- Inspector can complete a full inspection
- All field types work
- Photos upload successfully
- Defects are recorded
- Inspection can be saved and resumed

---

### **Milestone 2: Inspection Results & Reporting** (Weeks 4-5)
**Goal:** Users can view completed inspections and download PDFs

- [ ] Inspection detail page showing all data
- [ ] PDF viewing/download
- [ ] Email PDF functionality
- [ ] Photo gallery view
- [ ] Defect list view

**Success Criteria:**
- Completed inspections are viewable
- PDFs generate and download
- Photos display correctly
- Defects are organized and clear

---

### **Milestone 3: Work Orders** (Weeks 6-7)
**Goal:** Work orders can be created from defects and managed

- [ ] Work orders list page
- [ ] Work order detail page
- [ ] Create work order from defect
- [ ] Link defects to work orders
- [ ] Status management

**Success Criteria:**
- Work orders can be created
- Defects link correctly
- Status updates work
- Technicians can view assigned work

---

### **Milestone 4: Polish & Production Ready** (Weeks 8-10)
**Goal:** Application is production-ready with enhanced UX

- [ ] Dashboard with real data
- [ ] Notifications system
- [ ] Advanced search
- [ ] Batch operations
- [ ] Performance optimizations
- [ ] Mobile responsiveness verified
- [ ] Error handling improved
- [ ] Loading states polished

**Success Criteria:**
- Dashboard provides useful insights
- Search is fast and accurate
- Mobile experience is excellent
- No critical bugs
- Performance metrics met

---

## 📱 Mobile Considerations

**Camera Access:**
- Request camera permissions properly
- Fallback to file upload if denied
- Handle camera not available

**Touch Targets:**
- Minimum 44px touch targets
- Sufficient spacing between buttons
- Avoid hover-only interactions

**Offline Support (Future):**
- Service worker for offline inspections
- Queue photos for upload when online
- Local draft storage

**Responsive Design:**
- All pages work on mobile
- Collapsible sidebar on mobile
- Bottom navigation for mobile?

---

## 🧪 Testing Strategy

**Unit Tests:**
- Field validation logic
- Defect generation rules
- Date/time calculations

**Integration Tests:**
- Inspection execution flow
- Photo upload
- Auto-save functionality

**E2E Tests (Playwright):**
- Complete inspection from start to finish
- Create work order from defect
- Download PDF

**Manual Testing:**
- Mobile camera on real devices
- Different browsers
- Slow network conditions

---

## 🚀 Deployment Considerations

**Environment Variables:**
- API base URL
- FMCSA API key
- Upload size limits

**Build Optimization:**
- Code splitting
- Tree shaking
- Minification
- Gzip compression

**CDN:**
- Static assets to CDN
- Photo uploads to S3/Cloudinary

**Monitoring:**
- Error tracking (Sentry)
- Performance monitoring
- User analytics

---

## 📚 Dependencies to Add

**Already Installed:**
- React
- TypeScript
- React Query
- Zustand
- Axios
- Tailwind CSS

**Need to Add:**
```json
{
  "dependencies": {
    "react-pdf": "^7.x",                  // PDF viewing
    "browser-image-compression": "^2.x",  // Image compression
    "date-fns": "^3.x",                   // Date utilities
    "react-hot-toast": "^2.x",            // Toast notifications
    "react-dropzone": "^14.x",            // File upload
    "react-hook-form": "^7.x",            // Form management
    "zod": "^3.x"                         // Schema validation
  },
  "devDependencies": {
    "@playwright/test": "^1.x",           // E2E testing
    "vitest": "^1.x",                     // Unit testing
    "@testing-library/react": "^14.x"     // Component testing
  }
}
```

---

## 💡 Open Questions & Decisions Needed

1. **Photo Storage:**
   - Store on backend filesystem or cloud (S3/Cloudinary)?
   - Max photo size? (currently thinking 2MB)

2. **Offline Support:**
   - Is offline inspection execution required?
   - If yes, this significantly increases complexity

3. **Mobile App:**
   - Is a native mobile app needed or is PWA sufficient?
   - Camera quality requirements?

4. **Signature Capture:**
   - Do inspections need inspector signature?
   - Customer signature?

5. **Barcode/QR Scanning:**
   - Scan asset tags during inspection?
   - Scan VIN barcodes?

6. **GPS/Location:**
   - Record GPS location during inspection?
   - Required or optional?

7. **Multi-language:**
   - Support languages other than English?

8. **Accessibility:**
   - WCAG compliance level needed?

---

## 🔗 Related Documentation

- [SETUP.md](./SETUP.md) - Development environment setup
- [EQUIPMENT_DATA_SCHEMAS.md](./docs/EQUIPMENT_DATA_SCHEMAS.md) - Equipment typing
- Backend API Documentation (when available)
- Design System / Style Guide (when available)

---

## 📝 Notes

**Current Focus:**
The inspection execution workflow (Phase 1) is the highest priority. Without this, the application cannot fulfill its core purpose.

**Technical Debt:**
- Hash-based routing should eventually migrate to React Router
- Consider migrating inline styles to Tailwind classes
- Form validation could be standardized with react-hook-form + zod

**Performance Targets:**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90

**Browser Support:**
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Android)
- No IE11 support needed

---

**Last Updated:** 2026-03-13
**Next Review:** After Phase 1 completion
