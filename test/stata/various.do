/*

Various additional examples

*/

capture capture log close

clear
cd N:/INK/matvan/stata/statistically/
set logtype text, permanently

capture log using various/table_headings.txt, replace
sysuse auto, clear
/*
    Here the heading "Car type" crosses the columns
*/
tab rep78 foreign
capture log close


capture log using various/margins_complex.txt, replace
sysuse nlsw88, clear
/*
    Margins at uses an unusual arrangement
*/
reg grade married##age
margins married, at(age=(35(1)40))
capture log close
