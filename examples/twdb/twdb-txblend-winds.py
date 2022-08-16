#!/home/eturner/anaconda3/envs/pyn_env/bin/python3
import pandas as pd
import urllib.request
import os
import time
import glob
import logging
import xarray as xr
import numpy as np
from namdataserver import download_latest
from namdataserver import match_grb

download_latest()
twdb_stations = pd.read_csv('examples/twdb/NAMwinds.latlist.csv')
logging.debug("Read twdb station file with head \n {twdb_stations}".format(twdb_stations=twdb_stations))

latest = '/home/eturner/nam-dataserver/downloaded_data/latest'
processed = '/home/eturner/nam-dataserver/downloaded_data/twdb/'
values = ["UGRD_P0_L103_GLC0","VGRD_P0_L103_GLC0"]



for filename in os.listdir(latest):
    f = os.path.join(latest, filename)
    # checking if it is a file
    if filename == 'info': #skip our metadata file in the directory.
        continue
    if os.path.isfile(f):
        match_grb(filename,latest,values,twdb_stations,processed)

#fetch_twdb('nam_218_20220806_1800_000.grb2','/home/eturner/nam-dataserver/downloaded_data/latest/')
