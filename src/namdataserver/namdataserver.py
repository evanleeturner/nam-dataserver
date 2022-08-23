
import pandas as pd
import urllib.request
import os
import time
import glob
import logging
import xarray as xr
import numpy as np
from pathlib import Path
import faulthandler
import sys
from .wind_calcs import *
import datetime
import functools
import tarfile
import tabulate

#faulthandler.enable(file=sys.stderr, all_threads=True)
#faulthandler.dump_traceback(file=sys.stderr, all_threads=True)

pd.options.mode.chained_assignment = None  # default='warn' cuts down on a lot of warning printing...

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
# Python program to find MD5 hash value of a file
import hashlib

def Locate_Closest_File(timestamp):
    """
    Method determins the most accurate NAM file for the exact timestamp.
    
    returns URL for NAM
    
    
    """
    file_prefix = "nam_218_"

    first_file =  file_prefix+timestamp.strftime('%Y%m%d')
    hour = int(timestamp.strftime('%H'))
    #logic to find the most current 4-day model run hour
    if hour < 6:
        nam_H = 0
        offset = hour
    elif (hour >= 6)  and (hour < 12):
        nam_H = 6
        offset = hour - 6
    elif (hour >= 12)  and (hour < 18):
        nam_H = 12
        offset = hour - 12
    elif (hour >= 18)  and (hour <= 23):
        nam_H = 18
        offset = hour - 18
    else:
        logging.error("Something went terribly wrong with our hour {}".format(hour))
    
    #construct a file like this...nam_218_20220801_0000_000.grb2
    first_file = first_file+"_"+str(nam_H).zfill(2)+"00_"+str(offset).zfill(3)+".grb2"
    logging.debug("Our detected closest file to {} was {}".format(timestamp,first_file))

    #construct the URL... will look like..
    #https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/202208/20220801/nam_218_20220801_1200_000.grb2
    url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'
    url = url_base +timestamp.strftime('%Y%m') + '/' + timestamp.strftime('%Y%m%d') + '/' + first_file

    logging.debug("Constructed URL \n{}".format(url))
    
    return url

def BackFillNAM(starttime, endtime, model='218'):
    """
    Function downloads a series of NAM files between two timeperiods, or from the most current model back n hours.

    Taken from the NAM documentation (https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale)
    the NAM system updates (4/day: 00, 06, 12, 18UTC) with hourly forecasts.  To retrieve the most accurate past data, 
    this method retrieves the most accurate forecast data for the time period in question within the 4/day runcycle of the 
    model.

    NOTE: All times are considered to be UTC.

    Example:

    BackFillNAM(startdate, enddate) - where startdate = "3/3/2022 8:00" and enddate="3/3/2022" 14:00.

    Method downloads NAM files: 
     
    nam_218_20220303_06_002    -  3/3/2022 8:00
    nam_218_20220303_06_003    -  3/3/2022 9:00
    nam_218_20220303_06_004    -  3/3/2022 10:00
    nam_218_20220303_06_005    -  3/3/2022 11:00
    nam_218_20220303_12_000    -  3/3/2022 12:00
    nam_218_20220303_12_001    -  3/3/2022 13:00
    nam_218_20220303_12_002    -  3/3/2022 14:00
    """
    
    logging.debug("Entering BackFillNAM() with startime {} endtime {} model {}".format(starttime,endtime,model))
    pwd = os.getcwd()  #locate our working directory
    logging.debug("BackFillNAM() assuming our CWD is ./namdataserver .  Our CWD is: {}".format(pwd))

    if (model == '218'):
        file_prefix = 'NAM_218_'
    else:
        logging.error("Feature not implimented to download NAM model {model}".format(model=model))
        return

    fn= fetch_latestfile(model)
    home = str(Path.home())  #logic to find our home directory for cronscripts...

    root_dir = home+"/nam-dataserver/"
    #logic to find time from NAM file name
    latest = datetime.datetime(int(fn[8:12]), int(fn[12:14]), int(fn[14:16]),int(fn[17:19]))

    if endtime > latest:
        logging.warn("Detected that the requested enddate of {} is greater than the lastest file {} online.  Your data download will be incomplete".format(endtime,latest))
        endtime = latest
    
    #I use while loops exeedinly rarely.  This is one instance where I feel approporate since it would be very difficult to construct a for loop
    while starttime <= endtime:
        url = Locate_Closest_File(starttime)
        print("pretending to fetch url ",url)
        fetch_file(url, root_dir+'downloaded_data/latest/'+url[94:])
        starttime = starttime + datetime.timedelta(hours=1)
    return

def hash_finder(filename,directory):
    file = os.path.join(directory, filename)
    logging.debug("Performing hash operation on {file}".format(file=file))
    md5_hash = hashlib.md5()
    with open(file,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)

    return (md5_hash.hexdigest())


def match_grb(grb_file,directory,match_list,gps_list,output_folder):
    logging.info("Entering match_grb() with filename {filename}".format(filename={grb_file}))
    f = os.path.join(directory, grb_file)
    fout = os.path.join(output_folder, grb_file[:-5]+'.csv.xz')
    
    if os.path.isfile(fout):
        logging.info("File already exists for {} , quitting.".format(fout))
        return
    
    try:
        ds = xr.open_dataset(f,engine='pynio')
    except:
        logging.error("CRITICAL Error: Could not open {grb_file} for processing.".format(grb_file=grb_file))
        return -1
    logging.debug("Openned {grb_file} for processing.".format(grb_file=grb_file))

    ds =ds.get(match_list)  #parse grb for the parameter list
    logging.debug("Sliced values for columns of interest: {match_list}".format(match_list=match_list))
    df = ds.to_dataframe()
    logging.debug("Converted grb2 slice to dataframe...")
    winds = pd.DataFrame()
    arrays = []

    #need to add testing to make sure gps_list has columns lat,lon, station
    for index, row in gps_list.iterrows():
        #logging.debug("searching for... {a}, {b}, {c}".format(a=row['station'],b=row["lat"], c=row['lon']))
        #print(row["station"], row["lat"], row['lon'])
        df2 = df[df['gridlat_0'] < (row['lat']+.001)]
        df3 = df2[df2['gridlat_0'] > (row['lat'] - .001)]
        df4 = df3[df3['gridlon_0'] < (row['lon'] + .01)]
        df5 = df4[df4['gridlon_0'] > (row['lon'] - .01)]
        row_1=df5.iloc[0]

        #logging.debug("found {len} matches with row 1 as: {lat} , {lon}".format(len=len(df5),lat=df5['gridlat_0'].iat[0], lon=df5['gridlon_0'].iat[0]))
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
    logging.debug("Writing to compressed csv with xz compression.")
    try:
        winds.to_csv(fout,index=False)
    except:
        logging.error("CRITICAL Error: could not write output file {file}".format(file=fout))


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
        #columns = df.columns

        #df.sort_values(by='Name', inplace=True)

        last_file = df.iloc[-1,0]
        return  last_file

def fetch_file(url, file, hashfile=None, tries=5):
    pwd = os.getcwd()  #locate our working directory
    logging.debug("Entering fetch_file() from working directory {pwd} to fetch file {file} from url {url}"
                    .format(pwd=pwd,file=file,url=url))
    if hashfile is None:
        print ("did not detect a hashfile...")
    else:
        print ("our hashfile is ",hashfile)
        md5_hashes = pd.read_csv(hashfile)
        first_column = md5_hashes.iloc[:, 0]

    logging.info("Fetching file {url}".format(url=url))

    for i in range(tries):
        try:
            urllib.request.urlretrieve(url,filename=file)
        except:
            logging.warning("Failed to download file {file} from {url}".format(file=file,url=url))

        if hashfile is not None:
            ourhash = hash_finder(file,'')
            logging.info('File {local_name} has md5hash {ourhash}'.format(local_name=file,ourhash=ourhash))

            if first_column.str.contains(ourhash).any():
                logging.debug("Our hash matches the NAM metadata, we have the correct file - exiting fetch_file()")
                break
            else:
                logging.debug("Our hash DOES NOT match the NAM metadata, the file was not complete, retry download...")


    return

def fetch_latestfile(model='218'):
    logging.debug("Entering function fetch_latestfile()")

    home = str(Path.home())  #logic to find our home directory for cronscripts...

    root_dir = home+"/nam-dataserver/"

    if (model == '218'):
        url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'
    else:
        logging.error("Feature not implimented to download NAM model {model}".format(model=model))
        return

    
    #fetch months
    our_month = fetch_html(url_base)
    logging.debug("Latest month folder: {our_month}".format(our_month=our_month))
    #repeat procedure for latest forecast of the month...
    our_day = fetch_html(url_base+our_month) #grabs the very last forecast day..  eg. '20220806/'
    logging.debug("Latest day folder: {our_day}".format(our_day=our_day))
    #repeat to find the last run hourly forecast in the list..
    logging.info("Fetching html for {url}".format(url=our_day))
    last_file = fetch_html(url_base+our_month+our_day)
    logging.debug("Latest file in list: {last_file}".format(last_file=last_file))

    return last_file

def download_latest(model='218'):
    logging.debug("Entering function download_latest()")
    home = str(Path.home())  #logic to find our home directory for cronscripts...

    root_dir = home+"/nam-dataserver/"

    if (model == '218'):
        url_base = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/forecast/'
    else:
        logging.error("Feature not implimented to download NAM model {model}".format(model=model))
        return


    last_file = fetch_latestfile()
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



    #fetch the md5sum file from NAM folder so we can process.
    #use the last file as method to find md5sum file Name
    md5_name = 'md5sum.'+our_day[:-1]
    fetch_file(url_base+our_month+our_day+md5_name, root_dir+'downloaded_data/latest/'+md5_name)
    #open md5 listing for reading

    st = time.time()  #our program start time...
    #download all of the grib files... this could take a while
    index = 0
    for i in range(53):
        time.sleep(1)
        st2 = time.time()  #our program start time...
        our_file=str(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post)
        local_name=str(file_prefix+'_'+str(index).zfill(3)+file_post)
        fetch_file(url_base+our_month+our_day+file_prefix+'_'+str(index).zfill(3)+file_post, root_dir+'downloaded_data/latest/'+local_name, 'downloaded_data/latest/'+md5_name)


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

def Print_Winds_TXBLEND_FMT(bigframe, twdb_wind_list, outputfolder):
    """
    Function prints a large combined dataframe of wind data in the TXBLEND wndq format file.
    This format was originally what was delivered to TWDB by the TAMU modeling group through a web interface

    The function converts a dataframe that looks like this:

    	station	Datetime	SPD_mph	DIR
    0	twdb000	2022-08-14 18:00:00	15.128582	102.088511
    1	twdb001	2022-08-14 18:00:00	14.335636	108.621309
    2	twdb002	2022-08-14 18:00:00	15.999258	85.801288


    Tp the ending file format with fixed with crazyness like this:

    :*******Wind Data (3Hourly) Time in GMT****
    **3-hourly winds from NAM  model for station  twdb135 28.248   -96.326
     50, number of days of this record
    2022 03 19 00   11.0  354.8
    2022 03 19 03    9.4   12.2
    2022 03 19 06   10.5   31.9
    2022 03 19 09   16.5   48.4
    2022 03 19 12   16.4   49.8
    2022 03 19 15   15.8   60.4
    2022 03 19 18   12.0   70.3

    To accomplish this, we use a library called tabulate (https://pypi.org/project/tabulate/),
    various string formats, and pandas.

    """
    logging.debug("Entering Print_Winds_TXBLEND_FMT() with bigframe of len {}, {}, {}"
                  .format(len(bigframe),twdb_wind_list,outputfolder))
    logging.info("Writing wind data in TXBLEND format: STARTING")

    #error checking...
    isdir = os.path.isdir(outputfolder)
    if not isdir:
        logging.info("The specified output directory {} does not exist.  Trying to create it now...".format(outputfolder))
        try:
            os.mkdir(outputfolder)
            logging.info("Succesfully created {}".format(outputfolder))
        except OSError as err:
            logging.error("Could not create directory {}.  Quitting!  OS error: {0}".format(outputfolder,err))

    isfile = os.path.isfile(twdb_wind_list)
    if not isfile:
        logging.error("CRITICAL: Could not locate valid TWDB wind listing file specified at {}  Exiting."
                      .format(twdb_wind_list))
        return



    try:
        listdf = pd.read_csv(twdb_wind_list)
        logging.debug("Openned twdb_wind_list for reading with {} entries".format(len(listdf)))
    except:
        logging.error("CRITICAL: Pandas had critical error trying to open our wind list file {}"
                      .format(twdb_wind_list))
        return

    #we expect to have a dataframe with these exact columns.  Otherwise lets quit out and respond why.
    expected_columns = ['station', 'Datetime', 'SPD_mph', 'DIR']
    logging.debug("Running check on our df columns {} to expected {}".format(bigframe.columns,expected_columns))

    #some crazy lamba function testing to see if our columns are exactly the same.  I lifted this from:
    #https://www.digitalocean.com/community/tutorials/how-to-compare-two-lists-in-python
    if not functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q,expected_columns,bigframe.columns), True):
        logging.error("CRITICAL: Our dataframe columns are NOT what we expected.  What was passed in is {} \n We expected {}"
                      .format(bigframe.columns,expected_columns))
        return

    for i in bigframe['station'].unique():
        logging.debug("Processing station {}".format(i))
        tmp = bigframe.loc[(bigframe['station'] == i)].copy()
        logging.debug("Our sliced df has len {} and looks like {}".format(len(tmp),tmp.head(2)))
        tmp['STRTIME'] = tmp['Datetime'].dt.strftime('%Y %m %d %H')
        tmp['HOUR'] = tmp['Datetime'].dt.strftime('%H')

        #drop any duplicates - if they exist...
        tmp.drop_duplicates(subset=['Datetime'],inplace=True)


        #some crazy slicing here to get only the 3-hourly wind data...
        tmp  = tmp [(tmp['HOUR'] == '00') | (tmp['HOUR'] == '03')
                    | (tmp['HOUR'] == '06') | (tmp['HOUR'] == '09')
                   | (tmp['HOUR'] == '12') | (tmp['HOUR'] == '15')
                | (tmp['HOUR'] == '18') | (tmp['HOUR'] == '21')]
        #how many days are in the record??
        count = int(len(tmp)/8)

        tmp = tmp[['STRTIME', 'SPD_mph','DIR']]

        series = listdf.loc[listdf['station'] == i].squeeze()
        #need to separate the values from series to for python format print to work
        lon = series['lon']
        lat = series['lat']
        #for help with format printing, check out https://www.w3schools.com/python/ref_string_format.asp
        header_ln2 = "**3-hourly winds from NAM  model for station  {} {lat:.3f}   {lon:.3f}\n"
        header_ln3 = str(count)+ " number of days of this record\n"


        content = tabulate.tabulate(tmp.values.tolist(), tablefmt="plain", numalign="right",floatfmt=".1f",stralign="right")

        mypath = os.path.join(outputfolder,i)
        try:
            f = open(mypath+".wndq", "w")
        except:
            logging.error("CRITICAL: could not write file {} ".format(mypath+".wndq"))
            break
        f.write("*******Wind Data (3Hourly) Time in GMT****\n")
        f.write(header_ln2.format(i,lat=lat,lon=lon))
        f.write(header_ln3)
        f.write(content)
        f.close()
        logging.debug("Writing file {} COMPLETED".format(mypath+".wndq"))


    logging.info("Print_Winds_TXBLEND_FMT() COMPLETE")
    return

def make_tarfile(output_filename, source_dir):
    """
    Method is a simple wrapper for tarfile library to create a tar.gz out of an entire directory.
    """
    logging.debug("Entering make_tarfile() with output {} and source {}".format(output_filename, source_dir))
    org_dir = os.getcwd()

    os.chdir(source_dir)
    
    with tarfile.open(output_filename, "w:") as tar:
        tar.add(".", arcname=os.path.basename("."))
    logging.info("Wrote tarfile {}".format(output_filename))

    os.chdir(org_dir)
def read_TWDB_NAM_csv(fn,folder,columns_name, convertUVwinds=True):
    """
    Function reads a single file from disk in TWDB NAM CSV format.

    An example file "nam_218_20220814_1800_000.csv" would look like:

    UGRD_P0_L103_GLC0,VGRD_P0_L103_GLC0,station
    -6.6131005,1.416339,twdb000
    -6.0731006,2.046339,twdb001
    -7.1331005,-0.5236609,twdb002
    -7.4331,1.036339,twdb003
    -6.7131004,1.936339,twdb004
    -5.8631005,2.2063391,twdb005
    -5.3731003,2.376339,twdb006
    -5.8531003,-1.2136608,twdb007
    -7.8431005,0.2863391,twdb008
    -8.1331005,1.8463391,twdb009
    -7.1031003,2.616339,twdb010
    """
    try:
        tmp = pd.read_csv(os.path.join (folder, fn))
    except:
        logging.error("read_TWDB_NAM_csv() CRITICAL: Failed to read file {} in folder {} \n exiting the program early!".format(fn, folder))
        return -1
    logging.debug("read_TWDB_NAM_csv() Detected the timestamp from file {} as {} {} {} {} {}"
                  .format(fn,fn[8:12], fn[12:14], fn[14:16],fn[17:19], fn[23:25]))
    #datetime requires integers, create datetime column from the filename and apply deltatime from hour
    tmp['Datetime'] = datetime.datetime( int(fn[8:12]),int( fn[12:14]), int(fn[14:16]),int(fn[17:19])) +  datetime.timedelta(hours=int(fn[23:25]))

    #our our columns winds in U and V components, if so process to mph and dir
    if convertUVwinds:
        #convert U and V to speedmph and dir - converting from mps to mph with constant 2.23694
        tmp['SPD_mph'] = wind_uv_to_spd(tmp[columns_name[0]],tmp[columns_name[1]])* 2.23694
        tmp['DIR'] = wind_uv_to_dir(tmp[columns_name[0]],tmp[columns_name[1]])
        tmp.drop([columns_name[0],columns_name[1]], axis=1, inplace=True)


    logging.debug("read_TWDB_NAM_csv() Our completed ingested file looks like: \n {}".format(tmp.head(2)))

    return tmp

def Convert_TWDB(import_folder,OUTPUT_folder,TMP_folder,windlist):
    """
    Function imports Wind data in csv format, using the filename to create a datetime index.
    Filename follows the NOAA NAM formatting scheme where the datetime is embedded in the filename.
    See the NOAA site: https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale
    """
     #our U and V constants we are expecting from the files
    U = 'UGRD_P0_L103_GLC0'
    V= 'VGRD_P0_L103_GLC0'

    try:
        files = os.listdir(import_folder)
    except:
        logging.error("We could not open the folder specified: {} from our current directory {}"
                    .format(import_folder,os.getcwd()))
        return


    data = []
    logging.info("Loading wind data from disk: STARTING")
    for i in files:
        tmp = read_TWDB_NAM_csv(i,import_folder,[U,V],convertUVwinds=True)
        if tmp is None:
            logging.error("Quitting abnormally, see errors from above")
            return
        else:
            data.append(tmp)
    logging.info("Loading wind data from disk: COMPLETED - with {} records".format(len(data)))


    #combine the list of dataframes data[] into one giant frame...
    df = pd.concat(data, axis=0)
    df.sort_values(by=['Datetime'],inplace=True)
    logging.debug("Created one dataframe with record length {} from {} to {}".format(len(df),df['Datetime'].min(),df['Datetime'].max()))
    logging.debug("Our dataframe looks like: \n {} \n {}".format(df.head(2),df.tail(2)))

    Print_Winds_TXBLEND_FMT(df,windlist,TMP_folder)
    #add tar.gz operation for output_folder

    outputfile = os.path.join(OUTPUT_folder,"twdbq.tar")
    make_tarfile(outputfile, TMP_folder)
