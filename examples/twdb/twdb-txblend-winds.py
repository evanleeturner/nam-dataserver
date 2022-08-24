#!/home/eturner/anaconda3/envs/pyn_env/bin/python3
import pandas as pd
import urllib.request
import os
import time
import glob
import logging
import xarray as xr
import numpy as np
import datetime
from namdataserver import download_latest, BackFillNAM
from namdataserver import match_grb, make_tarfile, read_TWDB_NAM_csv, Convert_TWDB,Print_Winds_TXBLEND_FMT

starttime = datetime.datetime(2022,7,2,8,0)
endtime = datetime.datetime(2022,8,25,10,0)
#download_latest()


#BackFillNAM(starttime,endtime)

latest = '/home/eturner/nam-dataserver/downloaded_data/latest'
processed = '/home/eturner/nam-dataserver/downloaded_data/twdb/'
values = ["UGRD_P0_L103_GLC0","VGRD_P0_L103_GLC0"]
home = "/home/eturner"
root_dir = home+"/nam-dataserver/"
twdb_stations = pd.read_csv(root_dir+'examples/twdb/NAMwinds.latlist.csv')
logging.debug("Read twdb station file with head \n {twdb_stations}".format(twdb_stations=twdb_stations))

for filename in os.listdir(latest):
    f = os.path.join(latest, filename)
    # checking if it is a file
    if filename == 'info' or "md5sum" in filename: #skip our metadata files in the directory.
        continue
    if os.path.isfile(f):
        match_grb(filename,latest,values,twdb_stations,processed)

Convert_TWDB(processed,"/var/www/html/bays_estuaries/NAM-WINDS/",root_dir+"tmp_working",root_dir+"examples/twdb/NAMwinds.latlist.csv")
#fetch_twdb('nam_218_20220806_1800_000.grb2','/home/eturner/nam-dataserver/downloaded_data/latest/')
