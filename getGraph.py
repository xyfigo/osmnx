import osmnx as ox
G = ox.graph_from_place('石家庄市', network_type='drive')
ox.plot_graph(G)