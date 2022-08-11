# Coastal-Winds

Coastal-Winds is a program used to download and collate data from the North American Mesoscale Forecast System (known as NAM)


https://www.ncei.noaa.gov/products/weather-climate-models/north-american-mesoscale

## Dependencies

This program depends on a number of packages, namely the pynio package for interacting with grib2 files.  This 
package can only run on a linux computer using the anaconda 'conda-forge' environment.

Setup instructions are:

1.  Find the most current anaconda release on https://www.anaconda.com/products/distribution .  Use curl in your 
terminal to download the file and install. 

```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash Anaconda3-2022.05-Linux-x86_64.sh

```
 Then, install the following necessary packages.
 
````bash
conda config --set auto_activate_base false
conda install -c anaconda xarray
conda install -c anaconda pandas
conda create --name pynio_env --channel conda-forge pynio
````
## Usage

```python
import coastal-winds


```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
