/*

Examples from canonical documentation

Generally Stata 16 manual

*/

capture log close
clear
cd N:/INK/matvan/stata/statistically/

use N:/INK/matvan/stata/data/auto.dta, clear
log using results/regress.txt, replace
/*
    regress
    Example 1: Basic linear regression
*/
regress mpg weight foreign
log close


use N:/INK/matvan/stata/data/auto2.dta, clear
log using results/summarize.txt, replace
/*
    summarize
    Example 1: summarize with the separator() option
*/
summarize, separator(4)
log close


use N:/INK/matvan/stata/data/auto.dta, clear
log using results/probit.txt, replace
/*
    probit
    Example 1
*/
probit foreign weight mpg
log close


use N:/INK/matvan/stata/data/auto.dta, clear
log using results/logit.txt, replace
/*
    logit
    Example 1
*/
logit foreign weight mpg
log close


use N:/INK/matvan/stata/data/rod93.dta, clear
log using results/nbreg.txt, replace
/*
    nbreg
    Remarks and examples
*/
nbreg deaths i.cohort
log close


use N:/INK/matvan/stata/data/rod93.dta, clear
gen logexp = ln(exposure)
log using results/nbreg_offset.txt, replace
/*
    nbreg with offset
    Remarks and examples
*/
nbreg deaths i.cohort, offset(logexp) nolog
log close


use N:/INK/matvan/stata/data/margex.dta, clear
regress y i.sex i.group
log using results/margins1.txt, replace
/*
    margins

*/
margins sex
log close


use N:/INK/matvan/stata/data/margex.dta, clear
regress y i.sex i.group
log using results/margins4.txt, replace
/*
    margins
    Example 4: Multiple margins from one command
*/
margins sex group
log close


use N:/INK/matvan/stata/data/margex.dta, clear
logistic outcome i.sex i.group sex#group age
log using results/margins8.txt, replace
/*
    margins
    Example 8: Margins of interactions
*/
margins sex#group
log close

/*
use N:/INK/matvan/stata/data/.dta, clear
log using results/estat_vif.txt, replace
// no canonical example in Stata 16 manual
estat vif
log close
*/

/*
use N:/INK/matvan/stata/data/mroz.dta, clear
logit lfp k5 k618 age wc hc lwg inc
log using results/fitstat.txt, replace
// canonical example uses very old version of mroz
fitstat
log close
*/
