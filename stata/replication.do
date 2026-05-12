* Replication script for Förmögenhetsanalys
* Author: Förmögenhetsanalys
* Date: 2025-10-08

version 17
clear all
set more off

* Run all analysis scripts
do "stata/descriptives.do"
do "stata/top_shares.do"

* Output summary
display "Replication complete"
display "Results saved in figures/"
