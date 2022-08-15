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

def fetch_twdb(filename,directory):
    logging.info("Entering fetch_twdb with filename {filename}".format(filename={filename}))
    twdb_stations = pd.read_csv('NAMwinds.latlist.csv')
    logging.debug("Read twdb station file with head \n {twdb_stations}".format(twdb_stations=twdb_stations))
    f = os.path.join(directory, filename)
    ds = xr.open_dataset(f,engine='pynio')
    logging.debug("Openned grb2 dataset {filename}".format(filename=filename))
    ds =ds.get(["UGRD_P0_L103_GLC0","VGRD_P0_L103_GLC0"])
    logging.debug("Sliced values for columns of interest...")
    df = ds.to_dataframe()
    logging.debug("Converted grb2 slice to dataframe...")
    winds = pd.DataFrame()
    arrays = []


    for index, row in twdb_stations.iterrows():
        logging.debug("searching for... {a}, {b}, {c}".format(a=row['station'],b=row["lat"], c=row['lon']))
        #print(row["station"], row["lat"], row['lon'])
        df2 = df[df['gridlat_0'] < (row['lat']+.001)]
        df3 = df2[df2['gridlat_0'] > (row['lat'] - .001)]
        df4 = df3[df3['gridlon_0'] < (row['lon'] + .01)]
        df5 = df4[df4['gridlon_0'] > (row['lon'] - .01)]
        row_1=df5.iloc[0]

        logging.debug("found {len} matches with row 1 as: {lat} , {lon}".format(len=len(df5),lat=df5['gridlat_0'].iat[0], lon=df5['gridlon_0'].iat[0]))
        #print ("row two as ",df5['gridlat_0'].iat[1], df5['gridlon_0'].iat[1])
        #supress errors for slice copying here...
        located = df5.iloc[:1]
        located.drop(columns=['gridlon_0', 'gridlat_0'], inplace=True)
        located['station'] = row['station']
        #located['org_lat'] = row['lat']
        #located['org_lon'] = row['lon']
        #located['speed'] = wind_uv_to_spd(located['UGRD_P0_L103_GLC0'].iat[0],located['VGRD_P0_L103_GLC0'].iat[0])
        #located['dir'] = wind_uv_to_dir(located['UGRD_P0_L103_GLC0'].iat[0],located['VGRD_P0_L103_GLC0'].iat[0])
        arrays.append(located)


    winds = pd.DataFrame()
    winds = pd.concat(arrays)
    winds.to_csv('/home/eturner/nam-dataserver/downloaded_data/'+filename+'.csv',index=False)

download_latest('218')



directory = '/home/eturner/nam-dataserver/downloaded_data/latest'
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        fetch_twdb(filename,directory)

#fetch_twdb('nam_218_20220806_1800_000.grb2','/home/eturner/nam-dataserver/downloaded_data/latest/')
