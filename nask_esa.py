#!/usr/bin/env python3

import argparse
import requests
import json
import re
import time
import pandas as pd
from typing import List

def get_json(url):
    # requests
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    json_data = r.json()
    json_data["request_stats"] = add_api_stats(r, json_data)
    return json_data

def time_epoch(timestamp):
    pattern = '%Y-%m-%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(timestamp, pattern)))
    return epoch

def add_measurement(global_tags, tags, fields, timestamp):
    # TODO add global tags to item tags from school
    formated_struct = {}
    formated_struct["details"] = tags
    formated_struct["measurements"] = fields
    formated_struct["timestamp"] = timestamp
    return formated_struct

def dedup_dicts(items: List[dict]):
    dedu = [json.loads(x) for x in set(json.dumps(item, sort_keys=True) for item in items)]
    return dedu

def add_api_stats(requests_data, struct_list):
    dict_struct = {}
    dict_struct["request_time"] = requests_data.elapsed.total_seconds()
    dict_struct["status_code"] = requests_data.status_code
    return dict_struct

def get_struct(json_data, mode, global_tags, city, post_code, street, name, longitude, latitude):
    formated_list = []
    for item in json_data["smog_data"]:
        # check if item is not None and exact match normalized to lowered
        if city is not None:
           if item["school"]["city"] is not None:
              if item["school"]["city"].lower() == city.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if post_code is not None:
           if item["school"]["post_code"] is not None:
              if item["school"]["post_code"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if street is not None:
           if item["school"]["street"] is not None:
              if item["school"]["street"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if name is not None:
           if item["school"]["name"] is not None:
              if item["school"]["name"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if longitude is not None:
           if item["school"]["longitude"] is not None:
              if item["school"]["longitude"] == longitude:
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if latitude is not None:
           if item["school"]["latitude"] is not None:
              if item["school"]["latitude"] == latitude:
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        if city is None and post_code is None and street is None and name is None and longitude is None and latitude is None:
              formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
    # uniq items
    return_list = dedup_dicts(formated_list)
    return return_list # json with fields + tags

def data_output(measurement_name, measurement_name_stats, formated_struct, url, mode, debug, json_data):
    if mode == "telegraf-exec" or mode == "telegraf-http":
       epo = int(time.time())
       curr_epoch = str(epo).split(".")[0][::-1].zfill(19)[::-1]
       stats_status = {}
       for item in formated_struct:
          fields = item["measurements"]
          tags = item["details"]
          fields_list = []
          for kfield, vfield in fields.items():
              if vfield is not None:
                 vfield = "%.4f" % vfield
                 field = "{k}={v}".format(k=kfield, v=vfield)
                 fields_list.append(field)
          tags_list = []
          for ktag, vtag in tags.items():
                      tag = "{k}={v}".format(k=ktag, v=vtag)
                      tags_list.append(tag)
          tags = ",".join(tags_list)
          # escape al chars that are not allowed in influx protocol https://archive.docs.influxdata.com/influxdb/v0.9/write_protocols/write_syntax/#escaping-characters
          ntags=tags.replace(" ","\ ")
          fields = ",".join(fields_list)
          data_string = '{measurement},{tag} {field} {epoch}'.format(measurement=measurement_name, field=fields, tag=ntags, epoch=curr_epoch)
          if mode == "telegraf-http":
                r = requests.post(url, data=data_string.encode('utf-8'))
                if r.status_code != 204 and debug:
                   print(data_string)
                   print(r.json())
                if r.status_code in stats_status:
                   stats_status[r.status_code] += 1
                else:
                   stats_status[r.status_code] = 1
                # send internal stats about summary of each return coddes writing to telegraf influxdb listener - easy to monitor how many metrics sensing and which one ends with proper codes
                for code, count in stats_status.items():
                    http_write_request_time = r.elapsed.total_seconds()
                    esa_api_request_time = json_data["request_stats"]["request_time"]
                    esa_api_status_code = json_data["request_stats"]["status_code"]
                    data_stats = '{measurement},code={code} count={count},write_request_time={http_write_request_time},esa_api_request_time={api_request_time},esa_api_status_code={api_status_code} {epoch}'.format(measurement=measurement_name_stats, code=code, api_request_time=esa_api_request_time, api_status_code=esa_api_status_code, http_write_request_time=http_write_request_time, count=count, epoch=curr_epoch)
                    # same url used as used in metrics sending
                    requests.post(url, data_stats.encode('utf-8'))
                if debug:
                   print(stats_status)
          if mode == "telegraf-exec":
             print(data_string)
    if mode == "json":
         # list of JSON output with indent for better reading
         print(json.dumps(formated_struct, indent=4, ensure_ascii=False))
    if mode == "table":
         # human readable table output
         for item in formated_struct:
             data_frame = pd.DataFrame.from_dict(item)
             print(data_frame)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--debug', action="store_true", default=False, dest='debug')
  parser.add_argument('-c', '--city', action="store", default=None, dest='city')
  parser.add_argument('-p', '--post-code', action="store", default=None, dest='post_code')
  parser.add_argument('-s', '--street', action="store", default=None, dest='street')
  parser.add_argument('-n', '--school-name', action="store", default=None, dest='school_name')
  parser.add_argument('-m', '--mode', action="store", default="json", dest='mode', choices=['table', 'json', 'telegraf-exec', 'telegraf-http'])
  parser.add_argument('-o', '--longitude', action="store", default=None, dest='longitude')
  parser.add_argument('-a', '--latitude', action="store", default=None, dest='latitude')
  parser.add_argument('-t', '--telegraf-url', action="store", default="http://localhost:8186/write", dest='telegraf_http_url')
  args = parser.parse_args()

  debug=args.debug

  mode = args.mode # available raa, human or http outputs
  measurement_name = "nask_esa" # for metrics generation and sending
  measurement_name_stats = "nask_esa_stats" # this measurement name will be used for stats generated in telegraf-http sending
  esa_api_url = "https://public-esa.ose.gov.pl/api/v1/smog"

  # telegraf url for listener in telegraf used to accept HTTP data in InfluxData format
  # https://github.com/influxdata/telegraf/blob/master/plugins/inputs/influxdb_listener/README.md
  telegraf_http_url = args.telegraf_http_url

  # static global tags
  global_tags = {}

  # arguments values
  city=args.city
  post_code=args.post_code
  street=args.street
  school_name=args.school_name
  longitude=args.longitude
  latitude=args.latitude

  # source
  # get JSON data via API call
  json_data = get_json(esa_api_url)

  # transform
  # prepare to formated structure
  formated_struct = get_struct(json_data, mode, global_tags, city, post_code, street, school_name, longitude, latitude)

  # send
  # output data based on mode
  data_output(measurement_name, measurement_name_stats, formated_struct, telegraf_http_url, mode, debug, json_data)

if __name__ == '__main__':
    main()
