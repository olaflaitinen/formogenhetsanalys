* Descriptive statistics for wealth data
* Author: Förmögenhetsanalys
* Date: 2025-10-08

version 17
clear all
set more off

* Load data
use "data/synthetic/households.parquet", clear

* Descriptive statistics
sum total_wealth financial_wealth real_estate_wealth business_wealth debt

* Histograms
histogram total_wealth, frequency title("Total Wealth Distribution")
graph export "figures/total_wealth_histogram.png", replace

* Wealth by component
graph bar (mean) financial_wealth real_estate_wealth business_wealth, title("Average Wealth by Component")
graph export "figures/wealth_by_component.png", replace
