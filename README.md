# python-nask-esa
Script for getting data filtered or full from [NASK ESA](https://esa.nask.pl/) Air Quality project.

## Usage
Can be used to list filtered view per (city, postal-code, street or full school name) or without any filtering all schools at once in two modes:
* JSON output
* Table human readable

Allow for easy importing the real time data into timeseries databases using [Influxdata Telegraf](https://github.com/influxdata/telegraf).
Two modes available:
* Telegraf interval exec with output parsing [exec](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec)
* Sending into [Telegraf HTTP input](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/http) via HTTP in Influx format

With filtering we can generate metrics for example in whole city or postal-code in our neigborhood without knowing specific school (station id) whoch is more effective by grabbing all data in one API call.
### Help
```
python3 nask_esa.py --help
usage: nask_esa.py [-h] [-d] [-c CITY] [-p POST_CODE] [-s STREET] [-n SCHOOL_NAME] [-m {human,raw,telegraf-exec,telegraf-http}] [-o LONGITUDE] [-a LATITUDE] [-t TELEGRAF_HTTP_URL]

options:
  -h, --help            show this help message and exit
  -d, --debug
  -c CITY, --city CITY
  -p POST_CODE, --post-code POST_CODE
  -s STREET, --street STREET
  -n SCHOOL_NAME, --school-name SCHOOL_NAME
  -m {human,raw,telegraf-exec,telegraf-http}, --mode {human,raw,telegraf-exec,telegraf-http}
  -o LONGITUDE, --longitude LONGITUDE
  -a LATITUDE, --latitude LATITUDE
  -t TELEGRAF_HTTP_URL, --telegraf-url TELEGRAF_HTTP_URL
  ```
  
 ### Modes
 Script can be used in multiple modes to output data in:
 * JSON with proper indent for better reading
 * Human readable table formating
 * [Telegraf](https://github.com/influxdata/telegraf) HTTP listener sending in influx format 
 * [Telegraf](https://github.com/influxdata/telegraf) as Exec output in influx format
 
 ### Filtering
 All available attributes based on API can be used for filtering. Some like school name are very difficult to use as there is Full School name there, but there are more usable options like:
 * -c CITY, --city CITY
 * -p POST_CODE, --post_code POST_CODE
 * -s STREET, --street STREET
 * -n SCHOOL_NAME, --school_name SCHOOL_NAME
 * -o LONGITUDE, --longitude LONGITUDE
 * -a LATITUDE, --latitude LATITUDE
 
 ### Usage examples
 ```
 python3 nask_esa.py -m raw --longitude=21.00131621 --latitude=50.00814381
[
    {
        "details": {
            "name": "SPOŁECZNA SZKOŁA PODSTAWOWA NR 1 IM. KS.PROF. JÓZEFA TISCHNERA W TARNOWIE",
            "street": "UL. GUMNISKA",
            "post_code": "33-100",
            "city": "TARNÓW",
            "longitude": "21.00131621",
            "latitude": "50.00814381"
        },
        "measurements": {
            "humidity_avg": 83.44166666666666,
            "pressure_avg": 1006.4916666666667,
            "temperature_avg": 5.075,
            "pm10_avg": 51.525,
            "pm25_avg": 42.06666666666667
        },
        "timestamp": "2023-01-04 16:37:50"
    }
]
 ```
