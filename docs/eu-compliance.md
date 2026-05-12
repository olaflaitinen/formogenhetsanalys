# EU Compliance

This document describes compliance with relevant EU regulations and directives.

## GDPR (General Data Protection Regulation)

### Compliance Status: FULLY COMPLIANT
- Legal basis: Article 6(1)(e) public interest, Article 9(2)(j) scientific research
- Ethics committee approval obtained
- DPIA conducted and approved
- Data minimization and purpose limitation implemented
- Security measures in place

See `gdpr.md` and `dpia-summary.md` for details.

## EUPL-1.2 Licensing

### Compliance Status: FULLY COMPLIANT
- Primary license: EUPL-1.2
- All dependencies EUPL-1.2 compatible
- REUSE 3.0 compliance verified
- License texts in LICENSES/ directory

See GOVERNANCE.md for dependency license analysis.

## EU Open Data Directive (2019/1024)

### Compliance Status: PARTIALLY COMPLIANT
- Synthetic data available as CC0-1.0 (open data)
- Register data requires SCB microdata access (not open)
- Aggregated statistics available via SCB open data portal
- API access planned for synthetic data

## EU AI Act (Proposed)

### Compliance Status: NOT APPLICABLE
- Package is a research tool, not an AI system
- No automated decision-making
- No high-risk AI applications
- GNN models are for research only

## EU Copyright Directive

### Compliance Status: FULLY COMPLIANT
- Documentation licensed under CC-BY-4.0
- Proper attribution to sources
- No copyrighted material without permission
- License notices included

## EU Accessibility Directive (2016/210)

### Compliance Status: IN PROGRESS
- Documentation planned in English and Swedish
- Alt text for figures
- Screen reader compatible HTML
- High contrast color schemes

## EU Cybersecurity Act

### Compliance Status: IN PROGRESS
- Security audits planned
- Vulnerability disclosure policy in SECURITY.md
- SBOM generation via CycloneDX
- CodeQL analysis in CI/CD

## EU Digital Services Act

### Compliance Status: NOT APPLICABLE
- Package is not a digital service provider
- No user-generated content
- No online platform

## EU Data Act (Proposed)

### Compliance Status: NOT APPLICABLE
- No IoT devices
- No data sharing between businesses
- Research use only

## EU Public Sector Information Directive

### Compliance Status: PARTIALLY COMPLIANT
- Synthetic data available as open data
- Register data is public sector information but restricted
- API access planned for synthetic data
- Metadata standards followed (DCAT-AP)

## Ongoing Monitoring

We monitor EU regulatory developments and update compliance as needed.
