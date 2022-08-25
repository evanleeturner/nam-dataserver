#!/home/eturner/anaconda3/envs/pyn_env/bin/python3
import os
from namdataserver import download_latest, BackFillNAM,Open_Pandas_CSV
from namdataserver import match_grb, make_tarfile, read_TWDB_NAM_csv, Convert_TWDB,Print_Winds_TXBLEND_FMT
"""
This is the Texas Water Development Board (TWDB) running example for nam-dataserver.
The TWDB runs a legacy hydrodynamic model, TxBLEND for their oil response
program (https://www.twdb.texas.gov/surfacewater/bays/oil_spill/index.asp).  this
model requires wind data forecasts at specific grid points within the model.

This listing of model grid points, the resulting NAM column names, and folder
preferences are fed into the nam-dataserver functions to download, collate, and
prepare input for the TxBLEND model code.

This script is run daily using a cronscript.  NOTE that cronscripts require hard
paths (eg. paths that must start from the root directory '/').  The script also
runs with the working directory as the user who calls it.  Therefore, we need to
pay close attention to paths within nam-dataserver and set a hard path to the
home of the running user (here the example runs in my home directory).


For running on a fresh computer for the first time, it is required to backfill
NAM download data using the function BackFillNAM.  TxBLEND requires 50 days
of wind data in 3-hourly format to start a single model run.

An example code snippet would be:

starttime = datetime.datetime(2022,7,2,8,0)
endtime = datetime.datetime(2022,8,25,10,0)
BackFillNAM(starttime,endtime)

"""

#setting up our paths for running the script.
logging.info("Stating main TWDB NAM download script")
home = "/home/eturner"    #must set this to the correct path!
root_dir = os.path.join(home+"/nam-dataserver")
latest_dir = os.path.join(root_dir,"/downloaded_data/latest")
processed_dir = os.path.join(root_dir,"/downloaded_data/twdb/")
NAM_column_listings = ["UGRD_P0_L103_GLC0","VGRD_P0_L103_GLC0"]
output_dir = "/var/www/html/bays_estuaries/NAM-WINDS/"
TWDB_Dir = os.path.join(root_dir,"/examples/twdb/")

filename,latest_dir,NAM_column_listings,match_df,processed_dir)
#download latest NAM files
download_latest()

#open the TWDB station listing and create a pandas dataframe
twdb_stations = Open_Pandas_CSV(os.path.join(TWDB_Dir ,"NAMwinds.latlist.csv"))
logging.debug("Read twdb station file with head \n {twdb_stations}".format(twdb_stations=twdb_stations))

logging.info("Begin stripping needed data from NAM files using match_grb().")
match_grb(latest_dir,NAM_column_listings,match_df,processed_dir)
logging.info("Converting stripped NAM values from csv to fixed width format.")
Convert_TWDB(processed,output_dir,root_dir+"tmp_working",twdb_stations)
logging.info("Completed TWDB nam-dataserver script")
