"""
Sample data for Stata 16
https://www.stata-press.com/data/r16/
"""
from pathlib import Path
from urllib import request

OUT_FOLDER = Path(__file__).parent / "data"

datasets_16th_ed = {
    "auto.dta": "1978 Automobile Data",
    "auto2.dta": "1978 Automobile Data",
    "autornd.dta": "Subset of 1978 Automobile Data",
    "bplong.dta": "fictional blood pressure data",
    "bpwide.dta": "fictional blood pressure data",
    "cancer.dta": "Patient Survival in Drug Trial",
    "census.dta": "1980 Census data by state",
    "citytemp.dta": "City Temperature Data",
    "citytemp4.dta": "City Temperature Data",
    "educ99gdp.dta": "Education and GDP",
    "gnp96.dta": "U.S. GNP, 1967–2002",
    "lifeexp.dta": "Life expectancy, 1998",
    "network1.dta": "fictional network diagram data",
    "network1a.dta": "fictional network diagram data",
    "nlsw88.dta": "U.S. National Longitudinal Study of Young Women (NLSW, 1988 extract)",
    "nlswide1.dta": "U.S. National Longitudinal Study of Young Women (NLSW, 1988 extract)",
    "pop2000.dta": "U.S. Census, 2000, extract",
    "sandstone.dta": "Subsea elevation of Lamont sandstone in an area of Ohio",
    "sp500.dta": "S&P 500",
    "surface.dta": "NOAA Sea Surface Temperature",
    "tsline1.dta": "simulated time-series data",
    "tsline2.dta": "fictional data on calories consumed",
    "uslifeexp.dta": "U.S. life expectancy, 1900–1999",
    "uslifeexp2.dta": "U.S. life expectancy, 1900–1940",
    "voter.dta": "1992 presidential voter data",
    "xtline1.dta": "fictional data on calories consumed",
}

for dta in datasets_16th_ed:
    url = f"https://www.stata-press.com/data/r16/{dta}"
    outfile = OUT_FOLDER / dta
    print(url)
    print(outfile)
    g = request.urlopen(url)
    outfile.write_bytes(g.read())
