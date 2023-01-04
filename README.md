# python-nask-esa
Script for getting data filtered or full from [NASK ESA](https://esa.nask.pl/) Air Quality project.

## Usage
Can be used to list filtered view per (city, postal-code, street or full school name) or without any filtering all schools at once.

Allow for easy importing the real time data into timeseries databases using [Influxdata Telegraf](https://github.com/influxdata/telegraf).
Two modes available:
* Telegraf interval exec with output parsing [exec](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec)
* Sending into [Telegraf HTTP input](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/http) via HTTP in Influx format

### Help
```
python3 nask_esa.py --help
usage: nask_esa.py [-h] [-d] [-c CITY] [-p POST_CODE] [-s STREET] [-n SCHOOL_NAME] [-m {human,raw,telegraf}]

options:
  -h, --help            show this help message and exit
  -d
  -c CITY
  -p POST_CODE
  -s STREET
  -n SCHOOL_NAME
  -m {human,raw,telegraf}
  ```
  
 ### Modes
 Script can be used in multiple modes to output data in:
 * JSON with proper indent for better reading
 * Human readable table formating
 * telegraf HTTP sending in influx format 
 * telegraf exec output in influx format
 
 
