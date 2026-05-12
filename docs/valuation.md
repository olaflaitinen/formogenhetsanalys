# Valuation Methods

This document describes the asset valuation methods used in Förmögenhetsanalys.

## Listed Equity

### Market Price Valuation
- Use closing price on valuation date
- Multiply by quantity held
- Apply FX adjustment for foreign-listed securities

### FX Adjustment
```
value_sek = value_local / sek_rate
```
where `sek_rate` is units of local currency per 1 SEK.

## Unlisted Equity

### Book Value Method
Direct use of reported equity book value from the firm register.

### Capitalised Earnings
Apply sector-specific P/E multiples to firm profit:
```
value = profit * pe_multiplier(sector)
```

Default P/E multipliers by sector:
- K (Financial activities): 18.0
- J (Information and communication): 20.0
- H (Transportation and storage): 15.0
- Other sectors: 14.0

### Transaction Multiples
Apply sector-specific revenue multiples:
```
value = revenue * revenue_multiplier(sector)
```

Default revenue multiples by sector:
- J (Information and communication): 4.0
- K (Financial activities): 3.0
- Other sectors: 2.5

## Real Estate

### Taxeringsvärde to Market Conversion
```
market_value = taxeringsvärde / purchase_coefficient
```

Purchase coefficients by municipality type:
- Stockholm: 0.68
- Major cities: 0.70
- Other municipalities: 0.75

### Hedonic Index Adjustment
```
adjusted_value = base_value * (index_current / index_base)
```

## Harmonisation

Blend multiple valuation methods:
```
harmonised = w_book * value_book + w_cap * value_capitalised + w_mult * value_multiples
```

Default weights: w_book=0.4, w_cap=0.3, w_mult=0.3

Sensitivity analysis runs all three methods separately.
