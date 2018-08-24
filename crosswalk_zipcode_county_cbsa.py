#-------------------------------------------------------------------------------
#
#   This file creates a cross-walk between zipcodes, counties, and CBSAs.
#
#-------------------------------------------------------------------------------
#   INPUTS
#-------------------------------------------------------------------------------
#   Zip code-to-FIPS and zip code-to-CBSA info can be found at Housing and Urban Development, here:
#       https://www.huduser.gov/portal/datasets/usps_crosswalk.html#data
#   This information is available from 2010-2017 every quarter. This file uses either the 2013:Q4 or 2015:Q4 data.
#   Note this data only includes the FIPS and CBSA codes, it does not include the names of these. I gather the
#   name data from the Census and OMB.
#   There does not appear to be an API from which to download this data, so you will need to do this manually.
#   Go to the webpage, use the drop-down menu to download the following files:
#       - ZIP-COUNTY, 4th Quarter 2013 (XLSX file name: ZIP_COUNTY_122013.xlsx)
#       - ZIP-COUNTY, 4th Quarter 2015 (XLSX file name: ZIP_COUNTY_122015.xlsx)
#       - ZIP-CBSA, 4th Quarter 2013 (XLSX file name: ZIP_CBSA_122013.xlsx)
#       - ZIP-CBSA, 4th Quarter 2015 (XLSX file name: ZIP_CBSA_122015.xlsx)
#
#
#   FIPS-to-county name info can be found at the Census, here:
#       https://www.census.gov/geo/reference/codes/cou.html
#   This is available for 2010, and earlier. The file automatically downloads the
#   entire national file, national_county.txt, to your current directory.
#
#
#   CBSA information comes from the Office of Management and Budget (OMB) and is taken from the Census website:
#       https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html
#   and more information can be found here:
#       https://www.census.gov/programs-surveys/metro-micro/about/delineation-files.html
#   This contains the 900 or so metropolitan and micropolitan statistical areas. These are often referred to as
#   Core Based Statistical Areas. The classifications were determined by OMB in 2010 and were updated in 2013
#   and 2015. This file uses either the 2013 or 2015 data.
#
#-------------------------------------------------------------------------------
#   OUTPUTS
#-------------------------------------------------------------------------------
#   The file produces a CSV with the columns:
#   - 'zipcode': 5 digit zip code number
#   - 'FIPS': 5 digit FIPS code (2 digit state code + 3 digit county code)
#   - 'CountyName': County names from the Census
#   - 'cbsacode': CBSA or Metro Division Codes (see notes below)
#   - 'cbsatitle': CBSA title
#   - 'metromicro': whether the CBSA is a micropolitan or metropolitan area
#
#-------------------------------------------------------------------------------
#   NOTES
#-------------------------------------------------------------------------------
#   - I find that the HUD zipcode-CBSA data uses 'Metropolitan Division Codes', when these are
#   available, rather than the 'CBSA Codes'. WeZIP_COUNTY_122013,ZIP_CBSA_122013 need to match on these Metro Codes in those cases.
#
#   - The HUD zipcode-CBSA data contains duplicates of zip codes. This occurs when a zipcode
#   falls across a CBSA boundary. In this case, HUD provides the residential share falling within each
#   CBSA reported. For simplicity, in these cases I choose to allocate a unique zipcode to the CBSA
#   with the highest residential share.
#
#-------------------------------------------------------------------------------
### IMPORT PYTHON LIBRARIES, SETUP
#-------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import requests       # To download data from webpages
import os

# Set year for County and CBSA information (2013 or 2015)
data_year = 2015

#-------------------------------------------------------------------------------
### DOWNLOAD OMB AND CENSUS DATA
#-------------------------------------------------------------------------------

# Download county name data from Census
census_url = 'https://www2.census.gov/geo/docs/reference/codes/files/'

filenames = ['national_county.txt']

for xx in filenames:
    dls = census_url+xx
    resp = requests.get(dls)

    output = open(xx, 'wb')
    output.write(resp.content)
    output.close()


### Download OMB CBSA data from Census
census_url_part1 = 'https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/'
census_url_years = ['2013', '2015', '2017']
census_url_part2 = '/delineation-files/'
filename = 'list1.xls'

for yy in census_url_years:
    full_url = census_url_part1 + yy + census_url_part2

    dls = full_url + filename
    resp = requests.get(dls)

    output = open(filename, 'wb')
    output.write(resp.content)
    output.close()

    # Convert to csv
    data_xls = pd.read_excel(filename, index_col=None)
    data_xls.to_csv('OMB_cbsa_'+yy+'.csv', index=False)

# Remove temp file
os.remove('list1.xls')

#-------------------------------------------------------------------------------
### IMPORT OMB CBSA DATA
#-------------------------------------------------------------------------------

# Import data from .csv file
skipfooter = (data_year==2015)*4 + (data_year==2013)*3
df_CBSA = pd.read_csv('OMB_cbsa_'+str(data_year)+'.csv', skiprows=2, skipfooter=skipfooter, engine='python',
                      dtype={'CBSA Code': str, 'Metro Division Code': str,
                            'Metropolitan Division Code': str})

# Select and rename columns
if (data_year==2013):
    usecols = ['CBSA Code', 'Metro Division Code', 'CBSA Title', 'Metropolitan/Micropolitan Statistical Area']
elif (data_year==2015):
    usecols = ['CBSA Code', 'Metropolitan Division Code', 'CBSA Title', 'Metropolitan/Micropolitan Statistical Area']

df_CBSA = df_CBSA[usecols]
df_CBSA.columns = ['cbsacode', 'metrocode', 'cbsatitle', 'metromicro']

# Shorten metro vs. micro designations
df_CBSA.loc[(df_CBSA['metromicro']=='Metropolitan Statistical Area'), 'metromicro'] = 'Metro'
df_CBSA.loc[(df_CBSA['metromicro']=='Micropolitan Statistical Area'), 'metromicro'] = 'Micro'

# Clean data
df_CBSA['metrocode'] = df_CBSA['metrocode'].str.strip()
df_CBSA['cbsacode'] = df_CBSA['cbsacode'].str.strip()
df_CBSA['cbsatitle'] = df_CBSA['cbsatitle'].str.strip()

# Merge cbsacode and metrocode. Will use metrocode to merge (when available)
# because HUD files use metrocodes, not cbsacodes. See notes above.
df_CBSA.loc[(df_CBSA['metrocode'] == 'nan'), 'metrocode'] = df_CBSA.loc[(df_CBSA['metrocode'] == 'nan')]['cbsacode']

# Remove duplicate CBSAs
df_CBSA = df_CBSA[~df_CBSA.duplicated(subset=['cbsatitle', 'metrocode'])]

# Keep selected columns
df_CBSA = df_CBSA[['metrocode', 'cbsatitle', 'metromicro']]

#-------------------------------------------------------------------------------
### IMPORT HUD ZIPCODE AND COUNTY DATA
#   - There are 6000 unique zip codes that fall into more than one county
#   - The HUD data reports the proportion of the residential population in the zip code that falls into the current county
#   - Easiest solution is to keep only the zip-county pair for which the residential ratio is highest.
#       - I.e. allocate the zipcode to the County in which the largest fraction of its population falls.
#-------------------------------------------------------------------------------

### Import zip code-FIPS data from .xlsx file
df_zip_fips = pd.read_excel('ZIP_COUNTY_12'+str(data_year)+'.xlsx', dtype={'ZIP': str, 'COUNTY': str})
df_zip_fips['StateCode'] = df_zip_fips['COUNTY'].str[:2]

# Select and rename columns
df_zip_fips = df_zip_fips[['ZIP', 'COUNTY', 'StateCode', 'RES_RATIO']]
df_zip_fips.columns = ['zipcode', 'FIPS', 'StateCode', 'resratio']

# Tidy data
df_zip_fips['zipcode'] = df_zip_fips['zipcode'].str.strip()
df_zip_fips['FIPS'] = df_zip_fips['FIPS'].str.strip()
df_zip_fips['StateCode'] = df_zip_fips['StateCode'].str.strip()

# Drop duplicates with lower resratio. i.e. take highest resratio zipcode-CBSA pairs (see note above)
df_zip_fips = df_zip_fips.sort_values('resratio', ascending=False).drop_duplicates('zipcode').sort_index()

# Only keep wanted columns
df_zip_fips = df_zip_fips[['zipcode', 'FIPS']]


#-------------------------------------------------------------------------------
### IMPORT HUD ZIPCODE AND CBSA DATA
#   - Note: Same issue as above for the zip-county data.
#-------------------------------------------------------------------------------

# Import zip code-CBSA data from .xlsx file
df_zip_cbsa = pd.read_excel('ZIP_CBSA_12'+str(data_year)+'.xlsx', dtype={'ZIP': str, 'CBSA': str})

# Select and rename columns
df_zip_cbsa = df_zip_cbsa[['ZIP', 'CBSA', 'RES_RATIO']]
df_zip_cbsa.columns = ['zipcode', 'cbsacode', 'resratio']

# Tidy data
df_zip_cbsa['zipcode'] = df_zip_cbsa['zipcode'].str.strip()
df_zip_cbsa['cbsacode'] = df_zip_cbsa['cbsacode'].str.strip()

# Drop duplicates with lower resratio. i.e. take highest resratio zipcode-CBSA pairs (see note above)
df_zip_cbsa = df_zip_cbsa.sort_values('resratio', ascending=False).drop_duplicates('zipcode').sort_index()

# Only keep wanted columns
df_zip_cbsa = df_zip_cbsa[['zipcode', 'cbsacode']]


#-------------------------------------------------------------------------------
### IMPORT CENSUS FIPS-COUNTY NAMES DATA
#-------------------------------------------------------------------------------

# Import FIPS-County names data from .txt file
col_names = ['State', 'StateFIPS', 'CountyFIPS', 'CountyName', 'CountyClass']
df_fips_countyname = pd.read_table('national_county.txt', sep=',', header=None,
                                  names=col_names, dtype={'StateFIPS': str, 'CountyFIPS': str})

# Create full 5-digit FIPS code
df_fips_countyname['StateFIPS'] = df_fips_countyname['StateFIPS'].str.zfill(2)
df_fips_countyname['CountyFIPS'] = df_fips_countyname['CountyFIPS'].str.zfill(3)
df_fips_countyname['FIPS'] = df_fips_countyname['StateFIPS']+df_fips_countyname['CountyFIPS']

# Keep selected columns
df_fips_countyname = df_fips_countyname[['FIPS', 'CountyName']]


#-------------------------------------------------------------------------------
### MERGE DATA
#-------------------------------------------------------------------------------

# Merge zip-to-FIPS and FIPS-to-countyname dataframes
df_zip_fips_countyname = pd.merge(df_zip_fips, df_fips_countyname, on='FIPS', how='left')

# Merge zip-to-CBSAcode dataframe
df_zip_fips_countyname_cbsa = pd.merge(df_zip_fips_countyname, df_zip_cbsa, on='zipcode', how='outer')

# Merge in CBSA names dataframe
df_zip_fips_countyname_cbsaname = pd.merge(df_zip_fips_countyname_cbsa, df_CBSA,
                                           left_on='cbsacode', right_on='metrocode', how='left')

# Final columns used
usecols = ['zipcode','FIPS','CountyName','cbsacode','cbsatitle','metromicro']
df_zip_fips_countyname_cbsaname = df_zip_fips_countyname_cbsaname[usecols]

#-------------------------------------------------------------------------------
### SAVE DATA TO CSV
#-------------------------------------------------------------------------------

# Sort by CBSA name
df_zip_fips_countyname_cbsaname = df_zip_fips_countyname_cbsaname.sort_values('cbsatitle')

# Save Cross-walk file to CSV
df_zip_fips_countyname_cbsaname.to_csv('zipcode_FIPS_cbsa_crosswalk_'+str(data_year)+'.csv', index=False)
