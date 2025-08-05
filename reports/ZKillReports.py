#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys

from dateutil.parser import isoparse
from datetime import timedelta

def convertISOTime(isotime):
    date_obj = isoparse(isotime)
    return date_obj

def daysInPast(date_obj, xdays):
    new_date = date_obj - timedelta(days=xdays)
    return new_date

def convertToIso(date_obj):
    return date_obj.isoformat()

def loadConfig():
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            sys.exit(1)

    else:
        print("config.json does not exist")
        sys.exit(1)

    return config


if __name__ == "__main__":
    my_iso = '2025-08-04T01:23:20Z'
    my_date = convertISOTime(my_iso)
    my_past = daysInPast(my_date, 1)
    print(my_date, my_past)
    print(convertToIso(my_past))

    myconfig = loadConfig()
    print(myconfig)


