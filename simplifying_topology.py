import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
import geopandas as gpd
import collections

ox.config(log_console=True, use_cache=True)
weight_by_length = False

print(ox.__version__)


# create a network around some (lat, lon) point but do not simplify it yet
location_point = (39.9057386, 116.3682035)
G = ox.graph_from_point(location_point, network_type='drive_service', distance=500, simplify=False)
# turn off strict mode and see what nodes we'd remove, in red
nc = ['b' if ox.is_endpoint(G, node) else 'r' for node in G.nodes()]
fig, ax = ox.plot_graph(G, node_color=nc, node_zorder=3)

# simplify the network
SG = ox.simplify_graph(G)
fig, ax = ox.plot_graph(SG, node_color='b', node_zorder=3)
