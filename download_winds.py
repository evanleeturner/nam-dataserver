
import pandas as pd
import urllib.request
import os
import time
import glob
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(message)s')
#!pip3 install lxml  Need to install this...



#product for the 218 12k grid with 3hourly winds, taken from the main website here:
#https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale


def download_latest():
    url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'

    logging.debug("Entering function download_latest()")
    #cleanup all existing files for space savings...

    logging.debug("Changing directory to downloaded_data/latest ")
    os.chdir('/home/eturner/nam-dataserver/downloaded_data/latest')



    logging.debug("Fetching html for {url_base}".format(url_base=url_base))
    html_buff = pd.read_html(url_base)  #download the base page for forecast months
    monthly_forecasts= html_buff[0]
    monthly_forecasts.dropna(how='all', inplace=True)
    our_month = monthly_forecasts.iloc[-1,0]  #grabs the very last forecast month..  eg. '202208/'
    logging.debug("Latest month folder: {our_month}".format(our_month=our_month))
    #repeat procedure for latest forecast of the month...
    logging.debug("Fetching html for {url}".format(url=our_month))
    html_buff = pd.read_html(url_base+our_month)  #download the base page for forecast months
    daily_forecasts= html_buff[0]
    daily_forecasts.dropna(how='all', inplace=True)
    our_day = daily_forecasts.iloc[-1,0]  #grabs the very last forecast day..  eg. '20220806/'
    logging.debug("Latest day folder: {our_day}".format(our_day=our_day))
    #repeat to find the last run hourly forecast in the list..
    logging.debug("Fetching html for {url}".format(url=our_day))
    html_buff = pd.read_html(url_base+our_month+our_day)
    hourly_forecasts= html_buff[0]
    hourly_forecasts.dropna(how='all', inplace=True)
    last_file = hourly_forecasts.iloc[-1,0]
    logging.debug("Latest file in list: {last_file}".format(last_file=last_file))
    file_prefix = last_file[:-13]  #boil down the last file name to just the file prefix, etc. 'nam_218_20220806_1800'

    file_post = '.grb2'

    #logic to see if we need to clear out old files...
    files = glob.glob('*.grb2')
    if files:
        logging.debug("Found grb2 files for deletion: {files}".format(files=files))
        for f in files:
            try:
                os.remove(f)
                logging.debug("Removed file {f}".format(f=f))
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))


    st = time.time()  #our program start time...
    #download all of the grib files... this could take a while
    index = 0
    for i in range(53):
        st2 = time.time()  #our program start time...
        our_file=str(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post)
        logging.info("Fetching file {file} ...".format(file=our_file))
        urllib.request.urlretrieve(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post, filename=file_prefix+'_'+str(i).zfill(3)+file_post)
        # get the end time
        et = time.time()
        # get the execution time
        elapsed_time = et - st2
        logging.info('Download took: {elapsed_time} seconds'.format(elapsed_time=elapsed_time))
        if index < 36:
            index+=1
        else:
            index+=3

    ft = time.time()
    elapsed_time = et - st
    logging.info('Total download took: {elapsed_time} seconds'.format(elapsed_time=elapsed_time))

    logging.debug("Exiting function download_latest() successfully")

download_latest()
