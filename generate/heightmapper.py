# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 15:08:09 2021

@author: Joako360
"""
from typing import Dict
from math import ceil, inf

import numpy as np
import requests

# TODO: path problems are irritating
import os
import sys
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../.."))
from utils.extras import AIRMAP_ELEVATION_API_KEY
# query the AirMap elevation API for the given boundary box.
# returns numpy array with elevaton map.


# TODO: WHAT DOES THIS THING DO? 0_o
def heightmapper(bounds: Dict) -> np.ndarray:
    # TODO: get rid of airmap and switch to TopoData
    api_key = AIRMAP_ELEVATION_API_KEY
    url = 'https://api.airmap.com/elevation/v1/ele/carpet?'
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json; charset=utf-8',
    }
    
    arc_lat = bounds['N'] - bounds['S']
    arc_lon = bounds['E'] - bounds['W']
    # The Airmap Elevation API has a 10.000 data limit, as each data is 1 arcsecond, the limit extent is 100 x 100 = 10.000
    # 36 = 3600 arcseconds per grade / 100 arcseconds limit for Airmap Elevation API
    n = ceil(arc_lat * 36.0)
    m = ceil(arc_lon * 36.0)
    lat_step = round(arc_lat / n, 5)
    lon_step = round(arc_lon / m, 5)
    lat_start = bounds['S']
    maxh = 0
    minh = inf
    h_stack = []

    # TODO: nested loop with unused counters
    for i in range(n):  # LAT
        tmp_lst = []
        lon_start = bounds['W']  # this will get the "cursor" to the "west margin" again
        lat_stop = lat_start + lat_step
        for j in range(m):  # LON
            lon_stop = (lon_start + lon_step)
            points = ",".join(str(x) for x in (lat_start, lon_start, lat_stop, lon_stop))
            res = requests.get(url, data = {"points": points}, headers = headers)
            if res.ok:
                data = res.json()["data"]
                tmp_lst.append(np.matrix(data['carpet']))
                maxh = data['stats']['max'] if data['stats']['max'] > maxh else maxh
                minh = data['stats']['min'] if data['stats']['min'] < minh else minh
            else:
                print('''Airmap Elevation API Error
                      Status code {}: {}'''.format(res.status_code, res.reason))
            lon_start = lon_stop
        lat_start = lat_stop
        h_stack.append(np.hstack(tmp_lst))

    # TODO: do we need the prints? maybe only in verbose mode
    print(minh)
    print(maxh)
    hm = np.vstack(h_stack)
    return hm