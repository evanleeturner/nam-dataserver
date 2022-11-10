.. nam-dataserver documentation master file, created by
   sphinx-quickstart on Tue Aug 30 13:35:34 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

nam-dataserver
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. |br| raw:: html

    <br>


This is the Texas Water Development Board (TWDB) running example for nam-dataserver.
The TWDB runs a legacy hydrodynamic model, TxBLEND for their oil response
program (https://www.twdb.texas.gov/surfacewater/bays/oil_spill/index.asp).  this
model requires wind data forecasts at specific grid points within the model.
|br|
|br|
This listing of model grid points, the resulting NAM column names, and folder
preferences are fed into the nam-dataserver functions to download, collate, and
prepare input for the TxBLEND model code.
|br|
|br|
This script is run daily using a cronscript.  NOTE that cronscripts require hard
paths (eg. paths that must start from the root directory '/').  The script also
runs with the working directory as the user who calls it.  Therefore, we need to
pay close attention to paths within nam-dataserver and set a hard path to the
home of the running user (here the example runs in my home directory).
|br|
|br|
For running on a fresh computer for the first time, it is required to backfill
NAM download data using the function BackFillNAM.  TxBLEND requires 50 days
of wind data in 3-hourly format to start a single model run.

An example code snippet would be:

.. code-block:: python
    
    starttime = datetime.datetime(2022,7,2,8,0)
    endtime = datetime.datetime(2022,8,25,10,0)
    BackFillNAM(starttime,endtime)


Installation
==================


1.  Find the most current anaconda release on https://www.anaconda.com/products/distribution .  Use curl in your 
terminal to download the file and install. 

.. code-block:: bash

    curl -O https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
    bash Anaconda3-2022.05-Linux-x86_64.sh

2. Then, install the following necessary packages.
 
.. code-block:: bash

    conda create --name pynio_env --channel conda-forge pynio

Restart your terminal, activate the pynio environment to install the next packages...  


.. code-block:: bash

    conda activate pynio
    conda install -c anaconda xarray
    conda install -c anaconda pandas
    pip3 install lxml
    pip3 install tabulate

.. note::
    You can use **conda config --set auto_activate_base false** to not activate anaconda when you start a fresh terminal every login.

3. **SPECIFIC TO TWDB TxBLEND WIND DOWNLOADS** In order for the system to maintain a current download of the NAM forcast you will need to install the program in the crontab.  
Add this line to activate your conda environment in the crontab and to download the latest wind files:

.. code-block:: bash

    SHELL=/bin/bash
    source /home/eturner/anaconda3/bin/activate pynio_env; python3 /home/eturner/nam-dataserver/examples/twdb/twdb-txblend-winds.py

TWDB Run Example
=========================

The TWDB running example program lives in ~/examples/twdb/twdb-txblend-winds and should be called through a 
cronscript.  The program is:

.. code-block:: python

    #!/home/eturner/anaconda3/envs/pyn_env/bin/python3
    import os
    import logging
    import pandas as pd
    from namdataserver import download_latest, BackFillNAM,csv2pandas
    from namdataserver import match_grb, make_tarfile, read_TWDB_NAM_csv, Convert_TWDB,Print_Winds_TXBLEND_FMT    

    logging.info("Stating main TWDB NAM download script")
    home = "/home/eturner"    #must set this to the correct path!
    root_dir = os.path.join(home,"nam-dataserver")
    latest_dir = os.path.join(root_dir,"downloaded_data" ,"latest")
    processed_dir = os.path.join(root_dir,"downloaded_data", "twdb")
    NAM_column_listings = ["UGRD_P0_L103_GLC0","VGRD_P0_L103_GLC0"]
    output_dir = "/var/www/html/bays_estuaries/NAM-WINDS/"
    TWDB_Dir = os.path.join(root_dir,"examples", "twdb")

    #download latest NAM files
    download_latest()

    #open the TWDB station listing and create a pandas dataframe
    twdb_stations = csv2pandas(os.path.join(TWDB_Dir ,"NAMwinds.latlist.csv"))
    logging.debug("Read twdb station file with head \n {twdb_stations}".format(twdb_stations=twdb_stations))

    logging.info("Begin stripping needed data from NAM files using match_grb().")
    match_grb(latest_dir,NAM_column_listings,twdb_stations,processed_dir)
    logging.info("Converting stripped NAM values from csv to fixed width format.")
    Convert_TWDB(processed_dir,output_dir,root_dir+"tmp_working",twdb_stations)
    logging.info("Completed TWDB nam-dataserver script")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
