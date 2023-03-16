# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 16:52:21 2021

@author: joako360
"""
import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))
from utils.download import download_menu, download_data
from utils.transform import translate_gdf
import osmnx as ox


# TODO: include in a terrn2/tobj/odef => zip pipeline
# TODO: add file destination argument
if __name__ == "__main__":
    tobj = open("roads.tobj", "w+")
    headers = ("x", "y", "z", "rx", "ry", "rz", "odefname (without .odef file extension)")
    tobj.write('// ' + "\t".join(headers))

    data = download_data(*download_menu())
    x_0 = data['x_0']
    y_0 = data['y_0']
    nodes = ox.graph_to_gdfs(data['roads'], nodes = True, edges = False)
    nodes_trns = translate_gdf(nodes, x_0, y_0)
    tobj.write("//some roads\n")

    for index, row in nodes_trns.iterrows():
        y = float(row["elevation"])
        x, z = float(row["geometry"].x), -float(row["geometry"].y)
        tobj.write(f"{x}, {y}, {z}, 0.0, 0.0, 0.0, road-crossing\n")
        
    tobj.close()
