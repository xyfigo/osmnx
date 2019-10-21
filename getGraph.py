#import osmnx as ox
#G = ox.graph_from_place('石家庄市', network_type='drive')
#ox.plot_graph(G)
import osmnx as ox
ox.config(log_console=True, use_cache=True)
ox.__version__

# get the walking network for piedmont
G = ox.graph_from_place('思明区', network_type='drive')
fig, ax = ox.plot_graph(G)