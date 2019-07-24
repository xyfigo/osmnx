import networkx as nx
import osmnx as ox
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
ox.config(use_cache=True, log_console=True)
print(ox.__version__)

g=ox.graph_from_address("中建·国际港, 大兴区, 北京市, 中国", distance=1000, distance_type="bbox",network_type='drive')
g_progect=ox.project_graph(g)
fig,ax=ox.plot_graph(g_progect)