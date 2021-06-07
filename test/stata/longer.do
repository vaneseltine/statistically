/*

Examples from canonical documentation

Generally Stata 16 manual

*/

capture capture log close

clear
cd N:/INK/matvan/stata/statistically/
set logtype text, permanently

sysuse auto, clear
capture log using various/longer.txt, replace

/*
    regress
    Example 1: Basic linear regression
    auto.dta
*/
regress mpg weight foreign
probit foreign weight mpg
logit foreign weight mpg

logit foreign /*
    */ weight mpg

sysuse auto2, clear

// summarize
summarize, separator(4)

summarize, separator(0)

// summarize
// minimally
sum make

/*
    table
    Example 1
    auto2.dta
*/
table rep78

tab foreign if foreign == 1

/*
    table with contents
    Example 1 with multiple statistics
    auto2.dta
*/
table rep78, contents(n mpg mean mpg sd mpg median mpg)


use N:/INK/matvan/stata/data/rod93.dta, clear
/*
    nbreg
    Remarks and examples
    rod93.dta
*/
nbreg deaths i.cohort


gen logexp = ln(exposure)
/*
    nbreg with offset
    Remarks and examples
    rod93.dta
*/
nbreg deaths i.cohort, ///
    offset(logexp) nolog


use N:/INK/matvan/stata/data/margex.dta, clear
regress y i.sex i.group

margins sex


regress y i.sex i.group
margins sex group

logistic outcome i.sex i.group sex#group age
margins sex#group

/*
use N:/INK/matvan/stata/data/.dta, clear
// no canonical example in Stata 16 manual
estat vif
capture log close
*/

/*
use N:/INK/matvan/stata/data/mroz.dta, clear
logit lfp k5 k618 age wc hc lwg inc
capture log using results/fitstat.txt, replace
// canonical example uses very old version of mroz
fitstat
*/

capture log close
