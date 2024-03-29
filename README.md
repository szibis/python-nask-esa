# Python-Nask-ESA
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
python3 nask_esa.py -h
usage: nask_esa.py [-h] [-d] [-c CITY] [-p POST_CODE] [-s STREET] [-n SCHOOL_NAME] [-m {table,json,telegraf-exec,telegraf-http}] [-o LONGITUDE] [-a LATITUDE] [-t TELEGRAF_HTTP_URL] [-l TTL]

options:
  -h, --help            show this help message and exit
  -d, --debug
  -c CITY, --city CITY
  -p POST_CODE, --post-code POST_CODE
  -s STREET, --street STREET
  -n SCHOOL_NAME, --school-name SCHOOL_NAME
  -m {table,json,telegraf-exec,telegraf-http}, --mode {table,json,telegraf-exec,telegraf-http}
  -o LONGITUDE, --longitude LONGITUDE
  -a LATITUDE, --latitude LATITUDE
  -t TELEGRAF_HTTP_URL, --telegraf-url TELEGRAF_HTTP_URL
  -l TTL, --ttl TTL     Cache TTL for HTTP GET in elevation data and ESA API calls
```
   default for `-t TELEGRAF_HTTP_URL` is `http://localhost:8186/write`
   default for `-m {table,json,telegraf-exec,telegraf-http}, --mode {table,json,telegraf-exec,telegraf-http}` is `json`
  
 ### Modes
 Script can be used in multiple modes to output data in:
 * json - JSON with proper indent for better reading
 * table - Human readable table formating
 * telegraf-http - [Telegraf](https://github.com/influxdata/telegraf) HTTP listener sending in influx format 
 * telegraf-exec - [Telegraf](https://github.com/influxdata/telegraf) as Exec output in influx format
 
 ### Filtering
 All available attributes based on API can be used for filtering. Some like school name are very difficult to use as there is Full School name there, but there are more usable options like:
 * -c CITY, --city CITY
 * -p POST_CODE, --post_code POST_CODE
 * -s STREET, --street STREET
 * -n SCHOOL_NAME, --school_name SCHOOL_NAME
 * -o LONGITUDE, --longitude LONGITUDE
 * -a LATITUDE, --latitude LATITUDE
 
 With filtering we can add more to expand for example we would like to get all from specific city and extending by additional postal codes that belongs to some place close to city for example
 ```
 /usr/local/bin/python-nask-esa --mode json --city tarnów --post-code 33-101
 ```
 
 ### Usage examples
 
 #### Get data in RAW JSON - JSON reconstructed and rebuilded for telemetry purpose
 
 ```
 python3 nask_esa.py -m json --longitude=21.2213906 --latitude=52.2233683
[
    {
        "details": {
            "city": "WARSZAWA",
            "latitude": "52.2233683",
            "longitude": "21.2213906",
            "name": "SZKOŁA PODSTAWOWA NR 173 IM. GÓRNIKÓW POLSKICH W WARSZAWIE",
            "post_code": "05-077",
            "street": "INNE TRAKT BRZESKI"
        },
        "measurements": {
            "elevation": 104.8543701171875,
            "humidity_avg": 59.041666666666664,
            "pm10_avg": 19.816666666666666,
            "pm25_avg": 15.241666666666667,
            "pressure_avg": 1009.6666666666666,
            "pressure_sea_avg": 1021.8773859644494,
            "temperature_avg": 24.558333333333334
        },
        "timestamp": "2023-09-10 11:08:01"
    }
]
 ```
 #### Get data in Human readable table 
 
 ```
python3 nask_esa.py -m table --longitude=21.2213906 --latitude=52.2233683
                                                            details  measurements            timestamp
city                                                       WARSZAWA           NaN  2023-09-10 11:08:01
latitude                                                 52.2233683           NaN  2023-09-10 11:08:01
longitude                                                21.2213906           NaN  2023-09-10 11:08:01
name              SZKOŁA PODSTAWOWA NR 173 IM. GÓRNIKÓW POLSKICH...           NaN  2023-09-10 11:08:01
post_code                                                    05-077           NaN  2023-09-10 11:08:01
street                                           INNE TRAKT BRZESKI           NaN  2023-09-10 11:08:01
elevation                                                       NaN    104.854370  2023-09-10 11:08:01
humidity_avg                                                    NaN     59.041667  2023-09-10 11:08:01
pm10_avg                                                        NaN     19.816667  2023-09-10 11:08:01
pm25_avg                                                        NaN     15.241667  2023-09-10 11:08:01
pressure_avg                                                    NaN   1009.666667  2023-09-10 11:08:01
pressure_sea_avg                                                NaN   1021.877386  2023-09-10 11:08:01
temperature_avg                                                 NaN     24.558333  2023-09-10 11:08:01
 ```

## Observability

### Telegraf

#### Telegraf as Exec (https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec)

Example Telegraf configuration
```
[[inputs.exec]]
    interval = "10s"
    commands = ["/usr/local/bin/python-nask-esa --mode telegraf-exec --longitude=21.2213906 --latitude=52.2233683"]
    timeout = "10s"
    data_format = "influx"
[inputs.exec.tags]
    db = "nask-esa"
    
[[outputs.influxdb]]
    urls = ["http://192.168.1.11:8428"]
    database = "nask-esa"
    username = "nask-esa"
    skip_database_creation = true
    precision = "s"
    flush_interval = "30s"
    metric_buffer_limit = "20000"
[outputs.influxdb.tagpass]
    db = ["nask-esa"]
```
Above example will run our python script every 10 seconds in telegraf exec influxdata protocol formtat with additional db tag with 10 seconds timeout for operation.
After this Telegraf will output this produced metrics into InfluxDB output or any other telegraf suported output in this case VictoriaMetrics InfluxDB compatible listener with 20k metrics in memory buffer (nice if we have some network issues or external connectivity we will not lost any metric until this host restart).

####  Telegraf as HTTP writer to Telegraf listener (https://github.com/influxdata/telegraf/blob/master/plugins/inputs/influxdb_listener/README.md) 

Example Telegraf configuration
```
[[inputs.influxdb_listener]]
    service_address = ":8188"
    read_timeout = "10s"
    write_timeout = "10s"
    max_body_size = 0
[inputs.influxdb_listener.tags]
    db = "nask-esa"

[[outputs.influxdb]]
    urls = ["http://192.168.1.11:8428"]
    database = "nask-esa"
    username = "nask-esa"
    skip_database_creation = true
    precision = "s"
    flush_interval = "30s"
    metric_buffer_limit = "20000"
[outputs.influxdb.tagpass]
    db = ["nask-esa"]
```
and to use this we can start our script as cron every minute
```
/usr/local/bin/python-nask-esa --mode telegraf-http --longitude=21.2213906 --latitude=52.2233683 --telegraf-url http://localhost:8188/write
```
This just send data over HTTP to local or external Telegraf listener which is also used for stats and later is same as with exec. Telegraf will send to any output we create and buffer metrics.

#### Telegraf Exec vs HTTP

Main difference between exec and http is that with HTTP we have additional stats that include esa api calls and telegraf writing over http which allow us to monitor whole process end-to-end if all is working properly or if we have any degradation.
Exec allow only to see any issues in telegraf logs.
With HTTP we can run with `--debug` the whole script we use in Cron and will produce all info about Telegraf writing codes with count and all stats metrics that are produced and written to Telegraf.

### Metrics format

Main metrics and additional stats from HTTP sending will we under this measurements defined in script code
```
  measurement_name = "nask_esa" # for metrics generation and sending
  measurement_name_stats = "nask_esa_stats" # this measurement name will be used for stats generated in telegraf-http sending
```

#### Main metrics
Unde above measurement `nask_esa` we will have specific tags and fields. They comes JSON details and measurements. details will be exposed as tags and measurements as firelds.

Example:
```
nask_esa,city=WARSZAWA,latitude=52.2233683,longitude=21.2213906,name=SZKOŁA\ PODSTAWOWA\ NR\ 173\ IM.\ GÓRNIKÓW\ POLSKICH\ W\ WARSZAWIE,post_code=05-077,street=INNE\ TRAKT\ BRZESKI humidity_avg=90.1583,pm10_avg=51.0583,pm25_avg=32.8167,pressure_avg=999.1167,temperature_avg=3.4500 1673267291000000000
```
##### Fields
* humidity_avg
* pm10_avg
* pm25_avg
* pressure_avg
* temperature_avg
* pressure_sea_avg
* elevation
##### Tags
* city
* latitude
* longitude
* name
* post_code
* street
#### Stats metrics format
For stats with measurement name `nask_esa_stats` data we will produce fields and tags like bellow.

Example:
```
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.00306,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.003004,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.003053,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.004911,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.004465,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.004983,esa_api_request_time=0.138642 1673298668000000000
nask_esa_stats,write_status_code=204,esa_api_status_code=200 count=1,write_request_time=0.003016,esa_api_request_time=0.138642 1673298668000000000
```
##### Fields
* esa_api_request_time - ESA API request time measured from script running
* write_request_time - Write time over HTTP to Telegraf listener
##### Tags
* esa_api_status_code - HTTP status code from ESA API
* write_status_code - HTTP status code from Telegraf write
  
### Grafana
Based on Telegraf data we can graph the data
<img width="1768" alt="image" src="https://github.com/szibis/python-nask-esa/assets/329831/e5116333-a4fd-42bd-aa6d-0e0adf76cd5d">
<img width="1769" alt="image" src="https://github.com/szibis/python-nask-esa/assets/329831/2b15ce56-ebdb-4419-adac-14e07fcef115">
<img width="882" alt="image" src="https://github.com/szibis/python-nask-esa/assets/329831/4d56e70a-2e14-4e0c-a6be-cdbaaceaa63b">
We can also see internal stats for Telegraf processing and NASK API times for requests
<img width="874" alt="image" src="https://github.com/szibis/python-nask-esa/assets/329831/f3ecf7b5-9690-4258-acc9-c10e73d8625e">
<img width="879" alt="image" src="https://github.com/szibis/python-nask-esa/assets/329831/d9c7a2e8-0fb8-490f-ab07-c49cf721f9f2">

