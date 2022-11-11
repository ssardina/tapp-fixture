__author__ = "Sebastian Sardina"
__copyright__ = "Copyright 2021-2022"
__credits__ = []
__license__ = "Apache-2.0 license"
__email__ = "ssardina@gmail.com"
# __version__ = "1.0.1"
# __status__ = "Production"

import pyshorteners # https://pyshorteners.readthedocs.io/en/latest/
import json
import datetime
import calendar
import pandas as pd


###########################################################
# TOOLS
###########################################################
def next_day(cal_day=calendar.SATURDAY):
    today = datetime.date.today() #reference point.
    day = today + datetime.timedelta((cal_day-today.weekday()) % 7 )
    return day

def pretty_date(date : datetime.datetime):
    return date.strftime("%A %B %d, %Y (%Y/%m/%d)")

def compact_date(date : datetime.datetime):
    return date.strftime('%Y_%m_%d')


def print_json_pretty(data_json):
    print(json.dumps(data_json, sort_keys=True, indent=4))



# TinyURL shortener service
def shorten_url(url):
    s = pyshorteners.Shortener()
    try:
        return s.tinyurl.short(url)
    except:
        return s.dagd.short(url)



