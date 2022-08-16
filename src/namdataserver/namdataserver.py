
import pandas as pd
import urllib.request
import os
import time
import glob
import logging
import xarray as xr
import numpy as np
from pathlib import Path

pd.options.mode.chained_assignment = None  # default='warn' cuts down on a lot of warning printing...

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)



#product for the 218 12k grid with 3hourly winds, taken from the main website here:
#https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale

def fetch_html(url,tries=5):
    """
        Function fetches url for number of tries (default 5), returning the last value from the first column.
    """
    logging.info("Fetching html for {url}".format(url=url))
    for i in range(tries):
        try:
            html = pd.read_html(url)
            break
        except:
            logging.warning("Failed to read {url}...".format(url=url))

    if html is None:
        logging.error("CRITICAL ERROR - could not download {url}".format(url=url))
        return

    else:
        df = html[0]
        df.dropna(how='all', inplace=True)
        last_file = df.iloc[-1,0]
        return  last_file

def fetch_file(url, file, tries=5):
    logging.info("Fetching file {file} ...".format(file=file))

    for i in range(tries):
        try:
            urllib.request.urlretrieve(url,filename=file)
            break
        except:
            logging.warning("Failed to download file {file} from {url}".format(file=file,url=url))

    return


def download_latest(model='218'):
    home = str(Path.home())  #logic to find our home directory for cronscripts...

    root_dir = home+"/nam-dataserver/"

    if (model == '218'):
        url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'
    else:
        logging.error("Feature not implimented to download NAM model {model}".format(model=model))
        return

    logging.debug("Entering function download_latest()")
    #cleanup all existing files for space savings...

    #logging.debug("Changing directory to downloaded_data/latest ")
    #os.chdir('/home/eturner/nam-dataserver/downloaded_data/latest')



    our_month = fetch_html(url_base)
    logging.debug("Latest month folder: {our_month}".format(our_month=our_month))
    #repeat procedure for latest forecast of the month...
    our_day = fetch_html(url_base+our_month) #grabs the very last forecast day..  eg. '20220806/'
    logging.debug("Latest day folder: {our_day}".format(our_day=our_day))
    #repeat to find the last run hourly forecast in the list..
    logging.info("Fetching html for {url}".format(url=our_day))
    last_file = fetch_html(url_base+our_month+our_day)
    logging.debug("Latest file in list: {last_file}".format(last_file=last_file))
    file_prefix = last_file[:-13]  #boil down the last file name to just the file prefix, etc. 'nam_218_20220806_1800'

    file_post = '.grb2'

    folder = root_dir+'downloaded_data/latest/'
    #logic to see if we need to clear out old files...
    files = glob.glob(folder+'*.grb2',)
    if files:
        logging.debug("Found grb2 files for deletion: {files}".format(files=files))
        if folder+last_file[:-4] in files:
            logging.info("Found the same date and time in our current repository {folder} already, skipping download and exiting download_latest() succesfully.".format(folder=folder))
            return
        else:
            logging.debug("Did not locate {last_file} in our repository - follows we need to download fresh set, remove files existing...".format(last_file=folder+last_file[:-4]))
            logging.info("Deleting old NAM files from repository {folder}".format(folder=folder))
            for f in files:
                try:
                    os.remove(f)
                    logging.debug("Removed file {f}".format(f=f))
                except OSError as e:
                    print("Error: %s : %s" % (f, e.strerror))
    else:
        logging.info("Did not locate files to delete in folder {folder} - downloading fresh copy from NAM.".format(folder=folder))



    st = time.time()  #our program start time...
    #download all of the grib files... this could take a while
    index = 0
    for i in range(53):
        time.sleep(1)
        st2 = time.time()  #our program start time...
        our_file=str(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post)
        fetch_file(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post, 'downloaded_data/latest/'+file_prefix+'_'+str(index).zfill(3)+file_post)
        # get the end time	# get the end time
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

    logging.debug("Exiting function download_latest() successfully.")
