# nam-dataserver

nam-dataserver is a program used to download and collate data from the North American Mesoscale Forecast System (known as NAM).  Principally, the system holds a copy of the latest forecast on disk and responds to request for specific data.


https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale

## Dependencies

This program depends on a number of packages, namely the pynio package for interacting with grib2 files.  This 
package can only run on a **linux computer** using the anaconda 'conda-forge' environment.

## Installation

1.  Find the most current anaconda release on https://www.anaconda.com/products/distribution .  Use curl in your 
terminal to download the file and install. 

```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash Anaconda3-2022.05-Linux-x86_64.sh

```
 Then, install the following necessary packages.
 
````bash
conda create --name pynio_env --channel conda-forge pynio
````
restart your terminal, activate the pynio environment to install the next packages...  note: you can use conda config --set auto_activate_base false to not activate anaconda when you start a fresh terminal every login.

````bash
conda activate pynio
conda install -c anaconda xarray
conda install -c anaconda pandas
pip3 install lxml
````
## Usage

```python
import nam-dataserver


```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
