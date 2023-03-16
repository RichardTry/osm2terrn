# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 09:54:16 2021

@author: Joako360
"""
from math import ceil
from geopandas import GeoDataFrame
from networkx import MultiDiGraph
# TODO: removed imports 'graph_from_gdfs, graph_to_gdfs,'
from osmnx import project_graph, project_gdf
from shapely import affinity


# extract offset, x size, y size, map size and the itself from GeoDataFrame and return dict.
def data_from_gdf(gdf: GeoDataFrame) -> dict:
    d = {
        'x_0': float(gdf.bounds.minx),
        'y_0': float(gdf.bounds.maxy),
        'x_size': ceil(gdf.bounds.maxx - gdf.bounds.minx),
        'y_size': ceil(gdf.bounds.maxy - gdf.bounds.miny),
        'world_size': ceil(gdf.bounds.maxx - gdf.bounds.minx) * ceil(gdf.bounds.maxy - gdf.bounds.miny),
        'area': gdf
    }
    return d


def translate_all_geometry_cells(geom: GeoDataFrame, xoff=0.0, yoff=0.0, zoff=0.0) -> GeoDataFrame:
    r"""Returns a translated geometry shifted by offsets along each dimension.

    The general 3D affine transformation matrix for translation is:

        / 1  0  0 xoff \
        | 0  1  0 yoff |
        | 0  0  1 zoff |
        \ 0  0  0   1  /
    """
    # TODO: is it ok or this method fails sometimes?
    if geom.empty:
        return geom

    # fmt: off
    matrix = (1.0, 0.0, 0.0,
              0.0, 1.0, 0.0,
              0.0, 0.0, 1.0,
              xoff, yoff, zoff)
    geom["geometry"] = geom["geometry"].apply(lambda cell: affinity.affine_transform(cell, matrix))
    # fmt: on
    return geom


# translate GeoDataFrame with same CRS and bounds to new coordinates with x_0,y_0 as the new origin
def translate_gdf(gdf: GeoDataFrame, x_0 = None, y_0 = None) -> GeoDataFrame:
    x_0 = gdf.bounds.minx if x_0 is None else x_0
    y_0 = gdf.bounds.maxy if y_0 is None else y_0
    gdf_trns = gdf.copy()
    gdf_trns = translate_all_geometry_cells(gdf, xoff = x_0, yoff = y_0)
    return gdf_trns


# TODO: networks use only (?)
def translate_graph(G: MultiDiGraph, x_0: float, y_0: float) -> MultiDiGraph:
    G_trns = G.copy()
    G_trns.graph['x_0'] = x_0
    G_trns.graph['y_0'] = y_0
    for node in G_trns.nodes():
        G_trns.nodes[node]['x'] -= x_0
        G_trns.nodes[node]['y'] -= y_0
    return G_trns


def transform_gdf(gdf: GeoDataFrame, x_0 = None, y_0 = None) -> tuple:
    if len(gdf['geometry']) != 0:
        gdf_proj = project_gdf(gdf)
        gdf_trns = translate_gdf(gdf_proj, x_0, y_0)
        return gdf_trns
    else:
        print("GeoDataFrame must have a valid CRS and cannot be empty")
        return gdf


# TODO: networks use only (?)
def transform_graph(G: MultiDiGraph, x_0: float, y_0: float) -> tuple:
    G_proj = project_graph(G)
    G_trns = translate_graph(G_proj, x_0, y_0)
    return G_trns
        