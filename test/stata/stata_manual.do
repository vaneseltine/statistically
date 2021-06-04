/*

Examples from canonical documentation

Generally Stata 16 manual

*/

capture capture log close

clear
cd N:/INK/matvan/stata/statistically/
set logtype text, permanently

use N:/INK/matvan/stata/data/auto.dta, clear
capture log using results/regress.txt, replace
/*
    regress
    Example 1: Basic linear regression
*/
regress mpg weight foreign
capture log close


use N:/INK/matvan/stata/data/auto2.dta, clear
capture log using results/summarize.txt, replace
/*
    summarize
    Example 1: summarize with the separator() option
*/
summarize, separator(4)
capture log close


use N:/INK/matvan/stata/data/auto2.dta, clear
capture log using results/table.txt, replace
/*
    table
    Example 1
*/
table rep78
capture log close


use N:/INK/matvan/stata/data/auto2.dta, clear
capture log using results/table_contents.txt, replace
/*
    table with contents
    Example 1 with multiple statistics
*/
table rep78, contents(n mpg mean mpg sd mpg median mpg)
capture log close


use N:/INK/matvan/stata/data/auto.dta, clear
capture log using results/probit.txt, replace
/*
    probit
    Example 1
*/
probit foreign weight mpg
capture log close


use N:/INK/matvan/stata/data/auto.dta, clear
capture log using results/logit.txt, replace
/*
    logit
    Example 1
*/
logit foreign weight mpg
capture log close


use N:/INK/matvan/stata/data/rod93.dta, clear
capture log using results/nbreg.txt, replace
/*
    nbreg
    Remarks and examples
*/
nbreg deaths i.cohort
capture log close


use N:/INK/matvan/stata/data/rod93.dta, clear
gen logexp = ln(exposure)
capture log using results/nbreg_offset.txt, replace
/*
    nbreg with offset
    Remarks and examples
*/
nbreg deaths i.cohort, offset(logexp) nolog
capture log close


use N:/INK/matvan/stata/data/margex.dta, clear
regress y i.sex i.group
capture log using results/margins1.txt, replace
/*
    margins

*/
margins sex
capture log close


use N:/INK/matvan/stata/data/margex.dta, clear
regress y i.sex i.group
capture log using results/margins4.txt, replace
/*
    margins
    Example 4: Multiple margins from one command
*/
margins sex group
capture log close


use N:/INK/matvan/stata/data/margex.dta, clear
logistic outcome i.sex i.group sex#group age
capture log using results/margins8.txt, replace
/*
    margins
    Example 8: Margins of interactions
*/
margins sex#group
capture log close

/*
use N:/INK/matvan/stata/data/.dta, clear
capture log using results/estat_vif.txt, replace
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
capture log close
*/
