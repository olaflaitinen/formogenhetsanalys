# Data Protection Impact Assessment (DPIA) Summary

## Project Overview
Förmögenhetsanalys: Graph-aware estimation of wealth concentration in Sweden using register data and GNN methods.

## DPIA Date
2025-10-08

## Controller
Statistics Sweden (SCB)

## Processor
Researchers at participating institutions

## Data Processing

### Types of Data
- Wealth register data (financial, real estate, business wealth, debt)
- Firm register data (equity, revenue, profit, sector)
- Ownership chain data (ownership shares)
- Asset price data (public sources)

### Data Subjects
- Swedish households (estimated 5 million)
- Swedish firms (estimated 500,000)

## Risk Assessment

### High Risk Areas Identified
1. **Re-identification risk**: Combining multiple data sources could potentially identify individuals
   - **Mitigation**: Aggregation thresholds, noise injection where appropriate
2. **Sensitive data**: Wealth information is sensitive personal data
   - **Mitigation**: Secure processing environment, access controls
3. **Large-scale processing**: Processing millions of records
   - **Mitigation**: Data minimization, purpose limitation

### Medium Risk Areas
1. **Cross-border data**: None (all processing in Sweden)
2. **Automated decision-making**: None (research only)
3. **Special category data**: Wealth data considered special category
   - **Mitigation**: Ethics approval, public interest basis

## Measures Taken

### Technical Measures
- Encryption at rest and in transit
- Access logging and monitoring
- Secure SCB microdata environment
- Regular security audits

### Organizational Measures
- Data access agreements
- Training for all personnel
- Data protection officer oversight
- Breach response procedures

### Legal Measures
- GDPR lawful basis (public interest, research)
- Ethics committee approval
- Swedish Statistics Act compliance
- SCB data access agreement

## Residual Risks
- Risk of statistical disclosure through sophisticated attacks: LOW
- Risk of unauthorized access: LOW
- Risk of data breach: LOW

## Conclusion
With the implemented measures, the residual risks are acceptable. The project can proceed with data processing under the described conditions.

## DPIA Approval
Approved by: [Institution Ethics Committee]
Date: 2025-10-15
