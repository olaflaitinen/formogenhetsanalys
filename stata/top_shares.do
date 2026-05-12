* Top share calculation for wealth data
* Author: Förmögenhetsanalys
* Date: 2025-10-08

version 17
clear all
set more off

* Load data
use "data/synthetic/households.parquet", clear

* Sort by wealth descending
gsort -total_wealth

* Calculate cumulative wealth
gen cum_wealth = sum(total_wealth)
gen cum_share = cum_wealth / cum_wealth[_N]

* Top 1% share
gen top1pct = cum_share if _n <= _N * 0.01
local top1_share = top1pct[1]
display "Top 1% share: `top1_share'"

* Top 10% share
gen top10pct = cum_share if _n <= _N * 0.10
local top10_share = top10pct[1]
display "Top 10% share: `top10_share'"

* Gini coefficient
ineqdeco total_wealth
