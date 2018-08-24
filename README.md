# Crosswalk between zip codes, counties, and metropolitan areas (CBSAs)

This file produces a crosswalk between zip codes, counties (both FIPS codes and county names), and metropolitan areas (both CBSA codes and names). This provides a useful starting point for exploring data that need to be cross-references across multiple geographies. 

Note that this file provides an alternative to the NBER cross-walk files (http://www.nber.org/data/cbsa-msa-fips-ssa-county-crosswalk.html). Relative to those cross-walk files, I add zip code information, and use more accurate CBSA information (i.e. names) that are more commonly found in other data sources. For example, the NBER crosswalk refers to the New York metro area as "New York-Wayne-White Plains, NY-NJ" with CBSA code 35644, whereas almost all other sources (including the OMB!) use the name "New York-Newark-Jersey City, NY-NJ-PA" with CBSA code 35620.

This code makes use of 2013 or 2015 information on zip codes, counties, and CBSAs. The file can easily be updated to accommodate more recent info (e.g. the 2017 CBSA names from the OMB/Census). The data used come from the department of Housing and Urban Development (zip code-to-FIPS and zip code-to-CBSA crosswalks), the Census (county name information), and the Office of Management and Budget (CBSA name information).

Comments and suggestions most welcome.

# Getting Started

Before running the code, you will need to download several files from the HUD website at: <https://www.huduser.gov/portal/datasets/usps_crosswalk.html#data>. This is necessary because HUD does not appear to have an API available for downloading data (the webpage is very easy to navigate, however). Download the following files (feel free to change the dates, and adjust the code accordingly), by using the drop-down menu to download the following files:
- ZIP-COUNTY, 4th Quarter 2013 (XLSX file name: ZIP_COUNTY_122013.xlsx)
- ZIP-COUNTY, 4th Quarter 2015 (XLSX file name: ZIP_COUNTY_122015.xlsx)
- ZIP-CBSA, 4th Quarter 2013 (XLSX file name: ZIP_CBSA_122013.xlsx)
- ZIP-CBSA, 4th Quarter 2015 (XLSX file name: ZIP_CBSA_122015.xlsx)

# Code output

The code produces a .csv file with the following columns.

- `zipcode`:    5-digit zip code number
- `FIPS`:       5-digit FIPS code (2 digit state code + 3 digit county code)
- `CountyName`: County names from the Census
- `cbsacode`:   CBSA or Metro Division Codes (see notes below)
- `cbsatitle`:  CBSA title
- `metromicro`: whether the CBSA is a micropolitan or metropolitan area

The resulting .csv file is approximately 2.3MB in size.

# Prerequisites

The script requires `Python` along with the `numpy`, `pandas`, `requests` and `os` libraries.

# Running the code

After downloading the required HUD data to the current directory, the code can be run directly from the command line via:
```
python crosswalk_zipcode_county_cbsa.py
```

# Author

- James Graham (NYU, 2018)

# License

This project is licensed under the MIT License.
