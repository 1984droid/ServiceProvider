# Leasing Compliance Monitoring System - Implementation Assessment

**Date:** 2026-02-08
**Status:** Design Review & Feasibility Analysis
**Author:** Claude (Architecture Review)

---

## Executive Summary

**Bottom Line:** This is an **excellent strategic direction** that leverages existing v2.3 infrastructure exceptionally well. The proposed "compliance visibility as a service" model is architecturally sound, doesn't require major refactoring, and creates powerful network effects.

**Feasibility Rating:** ⭐⭐⭐⭐⭐ (5/5 - Highly Feasible)

**Implementation Complexity:** Medium (3-4 months for MVP, phased approach)

**Strategic Fit:** Perfect - aligns with existing multi-tenant architecture and v2.3 systems

---

## Current State Analysis

### ✅ What We Already Have (Strong Foundation)

#### 1. **Multi-Tenant Architecture with Tenant Types** ✅
```python
# apps/core_tenant/models.py:33-37
TENANT_TYPE_CHOICES = [
    ('service_provider', 'Service Provider'),
    ('leasing_company', 'Leasing Company'),  # ← ALREADY EXISTS!
    ('fleet_management', 'Fleet Management'),
]
```
**Impact:** Leasing companies are already a first-class tenant type. This is HUGE.

#### 2. **Asset Ownership Model with Lease Relationships** ✅
```python
# apps/assets/models.py - Asset model already has:
owned_by_organization       # Who owns it
leased_by_tenant           # Which leasing company (tenant-level)
leased_by_organization     # Which customer org leases it
serviced_by_tenant         # Who performs maintenance
```
**Impact:** The entire lease ownership model is ALREADY BUILT. We can query `leased_by_tenant` to find all assets a leasing company has exposure to.

#### 3. **Inspection System v2.1 with Immutable Audit Trail** ✅
- **InspectionRun** with SHA256 finalization hash (apps/inspections/models.py:483)
- **InspectionDefect** with severity tracking and evidence storage
- **InspectionProgram** with frequency/meter-based scheduling
- **Context snapshots** capture asset state at inspection time
- **Standards references** (ANSI A92.2-2021, etc.)

**Impact:** The audit-grade evidence system already exists. We just need to expose it to leasing tenants.

#### 4. **Maintenance System v2.3** ✅
- **MaintenanceProgram** with time/meter-based intervals (apps/assets/models.py:852)
- **MaintenanceTask** catalog (13 tasks imported)
- **Scheduling logic** for ODOMETER_MILES, ENGINE_HOURS, REEFER_HOURS

**Impact:** We can compute "maintenance compliance" using existing scheduling rules.

#### 5. **Work Order System with Structured Vocabulary** ✅
- **682 nouns**, **89 verbs**, **69 locations** (structured, not free text)
- Work orders link to assets and can reference inspection defects
- **Provider tracking** (serviced_by_tenant)

**Impact:** We can show leasing companies WHO performed the work and WHAT was done (structured data = audit quality).

#### 6. **Asset Capabilities & Typed Fields** ✅
- **CapabilityDefinition** (164 definitions imported)
- **AssetSubtype** with capability packs
- **Asset.capabilities** JSONField with typed data

**Impact:** We can match policy requirements to asset capabilities (e.g., "insulated aerial device requires dielectric test").

---

## Gap Analysis: What We Need to Build

### Phase 0: Network Primitives (Foundation)

#### 1. **SharingContract Model** (NEW - Critical)
```python
class SharingContract(models.Model):
    """
    Cross-tenant data sharing agreement.
    Allows customer tenants to grant leasing companies read-only access.
    """
    grantor_tenant         # Customer granting access
    grantee_tenant         # Leasing company receiving access
    scope                  # Which assets (by ownership, list, tag, etc.)
    permissions            # What data types (JSONField)
    expires_at             # Optional expiration
    revoked_at             # Instant revocation support
    created_at / updated_at
```

**Complexity:** Low-Medium (2-3 days)
**Dependencies:** None
**Risk:** Low - standard model pattern

#### 2. **SharedAssetScope Rules** (NEW - Medium Complexity)
Logic to determine which assets are visible to grantee based on scope rules:
- `"all_leased_from_grantee"` - Assets where `leased_by_tenant == grantee_tenant`
- `"asset_list": [uuid, ...]` - Explicit asset IDs
- `"tags": [...]` - Assets with specific tags
- `"organization": org_id` - All assets owned by this org

**Complexity:** Medium (3-5 days)
**Dependencies:** SharingContract model
**Risk:** Medium - query performance matters

#### 3. **Permission Matrix** (NEW - Policy Definition)
Define granular permissions in SharingContract.permissions JSONField:
```json
{
  "asset_profile": true,           // Name, identifier, subtype
  "maintenance_history": "summary", // "none" | "summary" | "full"
  "inspection_results": "full",    // "none" | "summary" | "full"
  "evidence_attachments": false,   // Photos, documents
  "work_orders": "summary",        // Summary vs. full detail
  "provider_identity": true        // Who performed the work
}
```

**Complexity:** Low (1-2 days - mostly documentation)
**Dependencies:** SharingContract model
**Risk:** Low - JSON config

#### 4. **Audit Log for Access** (NEW - Compliance Critical)
```python
class SharingAccessLog(models.Model):
    """Log every time grantee views shared data."""
    sharing_contract
    accessed_by_user      # User from grantee tenant
    accessed_at
    resource_type         # "asset" | "inspection" | "work_order"
    resource_id
    action                # "view" | "export"
```

**Complexity:** Low (1-2 days)
**Dependencies:** SharingContract model
**Risk:** Low - append-only log

**Phase 0 Total Estimate:** 1.5-2 weeks

---

### Phase 1: Lease Compliance Policy Layer

#### 1. **LeasePolicy Model** (NEW - Core Feature)
```python
class LeasePolicy(models.Model):
    """
    Defines compliance requirements for leased assets.
    Assigned per lease agreement, asset, or customer.
    """
    tenant_root            # Leasing company that owns this policy
    name                   # "Standard Equipment Lease Policy"
    description

    # Requirements (JSONField config)
    required_inspection_programs   # ["ip.ansi_a92_2_2021_periodic", ...]
    required_maintenance_programs  # ["mp.fleet.tractor.pm_15000_miles", ...]

    # Thresholds
    due_soon_days          # 30 days
    overdue_threshold_days # 7 days
    overdue_threshold_miles
    overdue_threshold_hours

    # Evidence requirements
    require_photos         # bool
    require_test_data      # bool (for dielectric, load tests)
    require_signatures     # bool

    # Provider requirements
    verified_providers_only  # Only accept work from verified repair shops
    min_standards_version    # "A92.2-2021" (reject older standards)

    is_active
    created_at / updated_at
```

**Complexity:** Medium (3-5 days)
**Dependencies:** Existing InspectionProgram, MaintenanceProgram models
**Risk:** Low - config model

#### 2. **PolicyAssignment Model** (NEW)
```python
class PolicyAssignment(models.Model):
    """Links policies to assets, lease agreements, or customer groups."""
    policy

    # Assignment target (one of):
    asset              # Specific asset
    lease_agreement    # All assets in lease (if we add LeaseAgreement model)
    organization       # All assets leased to this customer org
    asset_subtype      # All assets of this subtype
```

**Complexity:** Low-Medium (2-3 days)
**Dependencies:** LeasePolicy model
**Risk:** Low

**Phase 1 Total Estimate:** 1 week

---

### Phase 2: Compliance Computation Engine

#### 1. **AssetComplianceSnapshot Model** (NEW - Performance Critical)
```python
class AssetComplianceSnapshot(models.Model):
    """
    Materialized view of asset compliance state.
    Updated nightly + on-change triggers.
    """
    asset
    policy             # Which policy is being evaluated
    computed_at        # Last computation timestamp

    # Overall state
    compliance_status  # COMPLIANT | DUE_SOON | OVERDUE | OUT_OF_SERVICE | UNKNOWN

    # Inspection compliance
    last_inspection_date
    next_inspection_due_date
    next_inspection_due_meter  # miles/hours
    days_overdue       # null if not overdue

    # Maintenance compliance
    last_maintenance_date
    next_maintenance_due_date
    next_maintenance_due_meter

    # Evidence quality
    evidence_ok        # All requirements met
    missing_evidence   # JSONField: what's missing

    # Standards compliance
    standards_version_met   # Policy requires A92.2-2021, asset has it
    provider_verified       # Last service by verified provider

    # Reasons (for dashboard drilldown)
    compliance_issues  # JSONField: list of issues
```

**Complexity:** High (1-1.5 weeks)
**Dependencies:** LeasePolicy, InspectionRun, MaintenanceProgram
**Risk:** Medium - performance optimization needed

#### 2. **Compliance Computation Logic** (NEW - Complex)

**compute_asset_compliance(asset, policy):**
- Query last completed InspectionRun for each required program
- Query current meter readings (odometer, engine hours)
- Calculate due dates based on last completion + interval
- Check evidence requirements (photos present, signatures, etc.)
- Check provider verification status
- Return compliance snapshot data

**Complexity:** High (1-1.5 weeks)
**Dependencies:** All existing models
**Risk:** Medium - complex business logic

#### 3. **Background Job + Triggers** (NEW)
- **Nightly job:** Recompute all snapshots for active leases
- **On-change triggers:** Recompute when inspection completed, maintenance logged
- **Celery task** or Django management command

**Complexity:** Medium (3-5 days)
**Dependencies:** Celery (or similar job queue)
**Risk:** Low-Medium - standard pattern

**Phase 2 Total Estimate:** 3 weeks

---

### Phase 3: Leasing Dashboards + Notifications

#### 1. **Leasing Dashboard API Endpoints** (NEW)
```
GET /api/leasing/customers/               # List customers with active leases
GET /api/leasing/customers/{id}/assets/   # Assets leased to this customer
GET /api/leasing/assets/{id}/compliance/  # Compliance details for asset
GET /api/leasing/compliance-summary/      # Rollup: X% compliant, Y overdue
GET /api/leasing/assets/overdue/          # List of overdue assets
GET /api/leasing/inspections/{id}/        # Inspection details (if permission granted)
GET /api/leasing/evidence/{id}/           # View evidence (if permission granted)
```

**Complexity:** Medium (1 week)
**Dependencies:** SharingContract, AssetComplianceSnapshot
**Risk:** Low - standard REST API

#### 2. **Permission Enforcement** (MODIFY)
Update OrganizationPermissionMixin to check SharingContract:
- If user is from leasing tenant, check if they have active SharingContract
- Filter assets by SharedAssetScope rules
- Filter fields by permissions matrix
- Log access to SharingAccessLog

**Complexity:** High (1 week)
**Dependencies:** Existing permission system
**Risk:** High - security-critical, must be correct

#### 3. **Notification System** (NEW)
**Alert types:**
- Due soon (30 days before due date)
- Overdue (7 days past due date)
- Out of service (UNSAFE defect found)
- Failed dielectric test (safety critical)

**Delivery methods:**
- Email (via existing TenantEmailSettings)
- In-app notifications
- Optional: webhook for external systems

**Complexity:** Medium (1 week)
**Dependencies:** Email system, AssetComplianceSnapshot
**Risk:** Low - standard notifications

**Phase 3 Total Estimate:** 3 weeks

---

### Phase 4: Verified Providers + Standards Enforcement

#### 1. **Provider Verification** (MODIFY Tenant model)
```python
# Add to Tenant model:
is_verified_provider = models.BooleanField(default=False)
verified_at = models.DateTimeField(null=True)
certifications = models.JSONField(default=list)  # ["ANSI_A92.2", "OSHA", ...]
```

**Complexity:** Low (2-3 days)
**Dependencies:** None
**Risk:** Low

#### 2. **Standards Pack Version Tracking** (MODIFY)
Enhance InspectionRun to track which standards version was used:
```python
# Add to InspectionRun:
standards_pack_version = models.CharField(max_length=50)  # "A92.2-2021"
```

**Complexity:** Low (2-3 days)
**Dependencies:** InspectionRun model
**Risk:** Low

#### 3. **Policy Enforcement in Compliance Computation**
When computing compliance, check:
- Was inspection performed by verified provider?
- Was correct standards version used?
- Flag non-compliant inspections

**Complexity:** Medium (3-5 days)
**Dependencies:** Compliance computation engine
**Risk:** Low

**Phase 4 Total Estimate:** 1.5 weeks

---

### Phase 5: Incentive Mechanics (Optional but Powerful)

#### 1. **Compliance Score Calculation** (NEW)
```python
def calculate_compliance_score(customer_org, date_range):
    """
    Calculate simple, explainable compliance score.
    Returns: {
      "score": 87,  # 0-100
      "breakdown": {
        "compliant_asset_pct": 90,
        "avg_overdue_days": 3,
        "safety_failures": 1
      }
    }
    """
```

**Complexity:** Medium (3-5 days)
**Dependencies:** AssetComplianceSnapshot
**Risk:** Low

#### 2. **Compliance Report Export** (NEW)
PDF/Excel export of compliance status for customer self-service:
- Asset list with compliance status
- Inspection history
- Maintenance history
- Evidence thumbnails (if permission granted)

**Complexity:** Medium (1 week)
**Dependencies:** Reporting library (WeasyPrint or similar)
**Risk:** Low

**Phase 5 Total Estimate:** 1.5 weeks

---

## Total Implementation Estimate

| Phase | Weeks | Dependencies |
|-------|-------|--------------|
| Phase 0: Network Primitives | 1.5-2 | None |
| Phase 1: Policy Layer | 1 | Phase 0 |
| Phase 2: Compliance Engine | 3 | Phase 1 |
| Phase 3: Dashboards + Alerts | 3 | Phase 2 |
| Phase 4: Verified Providers | 1.5 | Phase 3 |
| Phase 5: Incentives (Optional) | 1.5 | Phase 4 |
| **Total (MVP = Phases 0-3)** | **7.5-9 weeks** | |
| **Total (Full = Phases 0-5)** | **11.5-13 weeks** | |

**MVP Estimate:** 2-2.5 months
**Full Implementation:** 3-3.5 months

---

## Strategic Assessment

### ✅ Strengths (Why This Will Work)

1. **Existing Foundation is Solid**
   - Asset lease relationships already modeled
   - Leasing company tenant type already exists
   - Inspection system is audit-grade (SHA256 hashes, immutability)
   - Maintenance scheduling already implemented
   - Work order vocabulary is structured (not free text)

2. **Doesn't Break Existing Architecture**
   - Leasing layer sits on top (read-only + policy)
   - No need to refactor core asset/inspection models
   - SharingContract is clean abstraction for cross-tenant access

3. **Powerful Network Effects**
   - **Customers:** Get compliance visibility, better rates
   - **Leasing companies:** Reduce risk, protect residual value
   - **Repair shops:** Get "verified" status, attract more work
   - **Platform:** Stickiness, data network effects, upsell opportunities

4. **Natural Monetization**
   - Compliance monitoring per-asset fee
   - Verified provider certification
   - Premium analytics/reporting
   - API access for third-party integrations

### ⚠️ Challenges & Risks

#### 1. **Permission System Complexity** (HIGH RISK)
**Challenge:** Cross-tenant data access with granular permissions is security-critical.

**Mitigation:**
- Use SharingContract as explicit permission model (not implicit)
- Audit every access (SharingAccessLog)
- Default to deny (customer must explicitly grant access)
- Regular security reviews of permission logic

**Complexity:** High
**Time Impact:** +1 week for thorough testing

#### 2. **Performance at Scale** (MEDIUM RISK)
**Challenge:** Compliance computation for 10,000+ assets nightly could be slow.

**Mitigation:**
- Use AssetComplianceSnapshot (materialized view pattern)
- Index heavily (asset, policy, computed_at)
- Batch processing with progress tracking
- Consider Celery for background jobs
- On-change triggers only recompute affected assets

**Complexity:** Medium
**Time Impact:** +3-5 days for optimization

#### 3. **Compliance Logic Correctness** (MEDIUM RISK)
**Challenge:** "Is this asset compliant?" is non-trivial business logic.

**Mitigation:**
- Write comprehensive test suite (50+ test cases)
- Start simple (time-based only), add meter-based later
- Make computation logic pluggable (easy to fix/enhance)
- Expose "reasons" for compliance state (transparency)

**Complexity:** Medium
**Time Impact:** +1 week for thorough testing

#### 4. **Data Privacy & Customer Concerns** (MEDIUM RISK)
**Challenge:** Customers may be hesitant to share data with leasing companies.

**Mitigation:**
- Make sharing opt-in and granular
- Show customers EXACTLY what leasing company can see
- Allow instant revocation
- Provide audit trail of who accessed what
- Market as "compliance transparency = better rates"

**Complexity:** Low (mostly UX/communication)
**Time Impact:** None (frontend concern)

### 🤔 Design Questions & Recommendations

#### Q1: Should leasing companies see work order costs?
**Recommendation:** NO - not needed for compliance, too sensitive.
- Leasing cares about: "Was maintenance done?" not "How much did it cost?"
- Keep financial data separate from compliance data

#### Q2: How to handle multi-party leases?
**Example:** Customer leases from Leasing Co A, who leases from Manufacturer.

**Recommendation:** Support **multiple SharingContracts** per asset.
- Customer → Leasing Co A (full access)
- Leasing Co A → Manufacturer (summary only)
- Each SharingContract has its own permissions

**Complexity:** Low (already supports multiple contracts)

#### Q3: What if customer doesn't grant access?
**Recommendation:** Leasing company sees "UNKNOWN" compliance status.
- Leasing can't enforce without visibility
- Customer incentivized to grant access (better rates, fewer audits)
- Market this as "trust but verify" vs. "trust blindly"

#### Q4: Should we build a LeaseAgreement model?
**Current State:** Assets have `leased_by_tenant` and `leased_by_organization` fields.

**Recommendation:** START WITHOUT LeaseAgreement model (simpler).
- Phase 0-3: Use asset-level lease relationships
- Phase 4+: Add LeaseAgreement model if needed for:
  - Contract terms tracking
  - Billing integration
  - Multi-asset lease bundles

**Rationale:** Don't over-engineer. See what customers actually need first.

#### Q5: How to handle inspection performed BEFORE SharingContract granted?
**Scenario:** Customer grants access on Feb 1. Inspection was completed Jan 15.

**Recommendation:** Show historical data up to reasonable limit (e.g., 24 months).
- SharingContract.effective_date controls historical scope
- Default: 24 months lookback
- Customer can override (more/less history)

---

## Suggested Changes to Proposal

### ✅ Things to Keep (Excellent Ideas)

1. **SharingContract model** - Perfect abstraction
2. **LeasePolicy as JSON config** - Flexible, future-proof
3. **AssetComplianceSnapshot** - Correct pattern for performance
4. **Read-only access for leasing** - Critical design constraint
5. **Verified provider badge** - Powerful network effect
6. **Evidence permissions granular** - Many customers will want summary-only

### 🔄 Suggested Modifications

#### 1. **Add SharingContract.effective_date**
```python
effective_date = models.DateField(default=timezone.now)
```
**Reason:** Control historical data visibility.

#### 2. **Make LeasePolicy.required_programs support wildcards**
```json
{
  "required_inspection_programs": [
    "ip.ansi_a92_2_*",  // Any A92.2 program
    "ip.dielectric_*"   // Any dielectric test
  ]
}
```
**Reason:** Don't force leasing companies to update policies when you add new program variants.

#### 3. **Add AssetComplianceSnapshot.next_action_date**
```python
next_action_date = models.DateField()  # Next due date (inspection OR maintenance)
```
**Reason:** Leasing dashboard needs single "when is next action?" date for sorting/alerts.

#### 4. **Add "grace period" to LeasePolicy**
```python
grace_period_days = models.IntegerField(default=7)
```
**Reason:** "Overdue" shouldn't mean "out of compliance" immediately. Give 7-day grace period.

### ❌ Things to Defer (Not MVP)

1. **Phase 5: Incentive mechanics** - Defer to post-MVP
   - Compliance scoring can wait
   - Focus on visibility first, incentives later

2. **Webhook notifications** - Defer to post-MVP
   - Email + in-app is sufficient for MVP
   - Add webhooks when customers ask for it

3. **"Standards pack enforcement"** - Simplify for MVP
   - Track standards version, but don't block inspections
   - Phase 1: Track version, show in compliance report
   - Phase 2+: Add policy enforcement if customers demand it

---

## Implementation Roadmap

### Sprint 1-2 (Weeks 1-2): Network Primitives
- [ ] SharingContract model + migrations
- [ ] SharedAssetScope query logic
- [ ] SharingAccessLog model
- [ ] Permission matrix documentation
- [ ] Unit tests (50+ test cases)

**Deliverable:** Customer can grant leasing company read-only access to specific assets.

### Sprint 3-4 (Weeks 3-4): Policy Layer
- [ ] LeasePolicy model + migrations
- [ ] PolicyAssignment model
- [ ] Policy CRUD API endpoints
- [ ] Policy assignment logic
- [ ] Unit tests (30+ test cases)

**Deliverable:** Leasing companies can define compliance requirements.

### Sprint 5-7 (Weeks 5-7): Compliance Engine
- [ ] AssetComplianceSnapshot model + migrations
- [ ] Compliance computation logic
- [ ] Background job for nightly recomputation
- [ ] On-change triggers (inspection completed, etc.)
- [ ] Unit tests (100+ test cases - most critical)

**Deliverable:** System computes compliance state for all leased assets.

### Sprint 8-10 (Weeks 8-10): Dashboards + Alerts
- [ ] Leasing dashboard API endpoints
- [ ] Permission enforcement in OrganizationPermissionMixin
- [ ] Compliance summary views
- [ ] Email alerts (due soon, overdue)
- [ ] Frontend dashboard (if in scope)
- [ ] Integration tests (20+ test cases)

**Deliverable:** Leasing companies can monitor compliance and receive alerts.

### Sprint 11-12 (Weeks 11-12): Polish + Testing
- [ ] Security review of permission system
- [ ] Performance testing with 10K+ assets
- [ ] End-to-end integration tests
- [ ] Documentation (API docs, user guides)
- [ ] Customer pilot program

**Deliverable:** Production-ready MVP for beta customers.

---

## Technical Debt & Future Enhancements

### Known Limitations of MVP

1. **No lease agreement model** - Using asset-level lease relationships only
2. **No financial integration** - Compliance ≠ billing (separate concerns)
3. **No mobile app optimizations** - API-first, but not optimized for offline
4. **No real-time updates** - Nightly batch + on-change triggers (no WebSockets)

### Future Enhancements (Post-MVP)

1. **LeaseAgreement Model** (if customers need contract tracking)
2. **Billing Integration** (if leasing companies want to auto-adjust rates based on compliance)
3. **Advanced Analytics** (trends, predictive maintenance, residual value modeling)
4. **Mobile App API** (offline inspection, background sync)
5. **Third-party Integrations** (insurance companies, fleet management systems)
6. **Machine Learning** (predict compliance risk, recommend maintenance schedules)

---

## Conclusion

### Overall Assessment: ⭐⭐⭐⭐⭐

This is an **excellent strategic direction** that:
- Leverages existing v2.3 infrastructure perfectly
- Creates powerful network effects (customers, leasing, repair shops)
- Doesn't require major refactoring
- Has clear monetization path
- Aligns with multi-tenant architecture

### Go/No-Go Recommendation: **✅ GO**

**Confidence Level:** Very High

**Reasoning:**
1. Foundation is already 70% built (asset leasing, inspection system, maintenance scheduling)
2. Remaining 30% is well-understood CRUD + business logic (no exotic tech)
3. Architectural approach is sound (read-only layer, clean separation)
4. Business value is clear and compelling

### Recommended Approach

**MVP Scope:** Phases 0-3 (Network + Policy + Compliance + Dashboards)
**Timeline:** 10 weeks (2.5 months)
**Team Size:** 2 developers + 1 part-time QA
**Risk Level:** Medium (mostly permission system complexity)

**Success Metrics:**
- 5+ leasing companies onboarded
- 50+ customers granted sharing access
- 1000+ assets under compliance monitoring
- 95%+ uptime for compliance computation
- Zero security incidents

**Go-to-Market:**
1. Beta with 2-3 friendly leasing companies (weeks 8-12)
2. Iterate based on feedback (weeks 13-16)
3. General availability (week 17)

---

## Questions for Product Owner

1. **Priority:** Is this higher priority than other v2.3 enhancements (e.g., inspections v2.2, work orders v2.3)?
2. **Timeline:** Do you have committed customers waiting for this? (If yes, faster timeline)
3. **Team Capacity:** Can you dedicate 2 developers full-time for 10 weeks?
4. **Leasing Expertise:** Do we have access to a leasing company subject matter expert for requirements validation?
5. **Frontend:** Is frontend dashboard in scope, or API-only for MVP?
6. **Monetization:** Do you want billing integration in MVP, or separate later?

---

**Prepared by:** Claude (Architecture Agent)
**Review Status:** Draft - Awaiting Product Owner Approval
**Next Step:** Product roadmap alignment meeting
