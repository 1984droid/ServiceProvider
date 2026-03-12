# 15 Leasing Compliance Monitoring

Tags: leasing, compliance, monitoring, policies, snapshots

## Goal
Enable a leasing tenant to:
- monitor maintenance and inspection compliance for leased assets
- confirm repairs are performed to standard by verified providers (optional)
- provide incentives for network participation (repair shop + customer join)

## Data sources for compliance
- MaintenanceDueInstance status (due/overdue/done)
- InspectionRun status + standards_version
- Unsafe defects and verification status
- Provider verification status (optional)

## Compliance snapshot model
Compute a ComplianceSnapshot for:
- (asset, lease_policy, time)

Outputs:
- compliant / due soon / overdue / out_of_service / unknown
- reasons list (human-readable)
- timestamps

## SharingContract enforcement
Leasing cannot view anything without an explicit SharingContract.
Even with a contract, sensitive data is redacted per permission level.

## References
- packages/leasing_compliance_mvp_package_v1.zip
- references/LEASING_COMPLIANCE_ASSESSMENT.md
