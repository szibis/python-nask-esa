#!/usr/bin/env python3

import argparse
import requests
import json
import re
import time
import pandas as pd

def get_json(url):
    # requests
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    json_data = r.json()
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

def get_struct(json_data, mode, global_tags, city, post_code, street, name):
    formated_list = []
    for item in json_data["smog_data"]:
        # check if item is not None and exact match normalized to lowered
        if city is not None:
           if item["school"]["city"] is not None:
              if item["school"]["city"].lower() == city.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        elif post_code is not None:
           if item["school"]["post_code"] is not None:
              if item["school"]["post_code"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        elif street is not None:
           if item["school"]["street"] is not None:
              if item["school"]["street"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        elif name is not None:
           if item["school"]["name"] is not None:
              if item["school"]["name"].lower() == post_code.lower():
                 formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
        else:
              formated_list.append(add_measurement(global_tags, item["school"], item["data"], item["timestamp"]))
           #if item["data"]['pressure_avg']:
           #   pressure_sea = item["data"]['pressure_avg'] / pow(1 - (0.0065 * 200) / (item["data"]['temperature_avg'] + 0.0065 * 200 + 273.15), 5.257)
           #   item["data"]['pressure_sea_avg'] = pressure_sea
    return formated_list # json with fields + tags

def data_output(measurement_name, formated_struct, url, mode):
    if mode == "telegraf":
       for item in formated_struct:
          fields = item["measurements"]
          tags = item["details"]
          epoch = time_epoch(item["timestamp"])
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
          fields = ",".join(fields_list)
          data_string = '{measurement},{tag} {field} {epoch}'.format(measurement=measurement_name, field=fields, tag=tags, epoch=epoch)
          if mode == "telegraf":
             try:
                r = requests.post(url, data=data_string.encode('utf-8'))
             except:
                print("Error sending ----> {}".format(data_string))
    if mode == "raw":
         # list of JSON output with indent for better reading
         print(json.dumps(formated_struct, indent=4, ensure_ascii=False))
    if mode == "human":
         # human readable table output
         for item in formated_struct:
             data_frame = pd.DataFrame.from_dict(item)
             print(data_frame)
              
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', action="store_true", default=False, dest='debug')
  parser.add_argument('-c', action="store", default=None, dest='city')
  parser.add_argument('-p', action="store", default=None, dest='post_code')
  parser.add_argument('-s', action="store", default=None, dest='street')
  parser.add_argument('-n', action="store", default=None, dest='school_name')
  parser.add_argument('-m', action="store", default="human", dest='mode', choices=['human', 'raw', 'telegraf'])
  args = parser.parse_args()

  mode = args.mode # available raa, human or http outputs
  measurement_name = "nask_esa" # for metrics generation and sending
  telegraf_http_url = 'http://localhost:8186/write'
  esa_api_url = "https://public-esa.ose.gov.pl/api/v1/smog"

  # static global tags
  global_tags = {}

  # arguments values
  city=args.city
  post_code=args.post_code
  street=args.street
  school_name=args.school_name

  # source
  # get JSON data via API call
  json_data = get_json(esa_api_url)

  # transform
  # prepare to formated structure
  formated_struct = get_struct(json_data, mode, global_tags, city, post_code, street, school_name)

  # send
  # output data based on mode
  data_output(measurement_name, formated_struct, telegraf_http_url, mode)

if __name__ == '__main__':
    main()
