
import xarray as xr
import pandas as pd
import urllib.request
import lxml
import os
import time
import glob
#!pip3 install lxml  Need to install this...

print("Fetching html file information from NAM website...")

#product for the 218 12k grid with 3hourly winds, taken from the main website here:
#https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale
url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'

def download_latest():

    #cleanup all existing files for space savings...

    os.chdir('downloaded_data/latest')

    files = glob.glob('*.grb2')

    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


    html_buff = pd.read_html(url_base)  #download the base page for forecast months
    monthly_forecasts= html_buff[0]
    monthly_forecasts.dropna(how='all', inplace=True)
    our_month = monthly_forecasts.iloc[-1,0]  #grabs the very last forecast month..  eg. '202208/'
    #repeat procedure for latest forecast of the month...
    html_buff = pd.read_html(url_base+our_month)  #download the base page for forecast months
    daily_forecasts= html_buff[0]
    daily_forecasts.dropna(how='all', inplace=True)
    our_day = daily_forecasts.iloc[-1,0]  #grabs the very last forecast day..  eg. '20220806/'
    #repeat to find the last run hourly forecast in the list..
    html_buff = pd.read_html(url_base+our_month+our_day)
    hourly_forecasts= html_buff[0]
    hourly_forecasts.dropna(how='all', inplace=True)
    last_file = hourly_forecasts.iloc[-1,0]
    file_prefix = last_file[:-13]  #boil down the last file name to just the file prefix, etc. 'nam_218_20220806_1800'



    file_post = '.grb2'

    st = time.time()  #our program start time...

    #download all of the grib files... this could take a while
    index = 0
    for i in range(54):
        st2 = time.time()  #our program start time...
        print("Fetching file ",url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post,"...")
        urllib.request.urlretrieve(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post, filename=file_prefix+'_'+str(i).zfill(3)+file_post)
        # get the end time
        et = time.time()
        # get the execution time
        elapsed_time = et - st2
        print('Download took: ', elapsed_time, ' seconds')
        if index < 36:
            index+=1
        else:
            index+=3


    ft = time.time()
    elapsed_time = et - st
    print('Final download time took: ', elapsed_time, ' seconds')

download_latest()
