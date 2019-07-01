# define the study sites as label : query
# places = {'北京市': {'state': 'Beijing', 'country': 'China'}}

import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
import geopandas as gpd
import logging as lg

ox.config(log_console=True, use_cache=True)
weight_by_length = False

print(ox.__version__)


def _gdf_from_places(queries):
    """
    Create a GeoDataFrame from a list of place names to query.

    Parameters
    ----------
    queries : list
        list of query strings or structured query dicts to geocode/download, one
        at a time
    gdf_name : string
        name attribute metadata for GeoDataFrame (this is used to save shapefile
        later)
    buffer_dist : float
        distance to buffer around the place geometry, in meters

    Returns
    -------
    GeoDataFrame
    """
    # create an empty GeoDataFrame then append each result as a new row
    gdf = gpd.GeoDataFrame()
    for query in queries:
        gdf = gdf.append(ox.gdf_from_place(query['query_str'], query['which_result']))

    # reset the index, name the GeoDataFrame
    gdf = gdf.reset_index().drop(labels='index', axis=1)
    gdf.gdf_name = 'unnamed'

    # set the original CRS of the GeoDataFrame to default_crs, and return it
    gdf.crs = ox.settings.default_crs
    ox.utils.log('Finished creating GeoDataFrame with {} rows from {} queries'.format(len(gdf), len(queries)))
    return gdf


# define the study sites as label : query
places = {'大连': {'query_str': '大连市', 'which_result': 2},
#'广州': {'query_str': '广州市', 'which_result': 2},
#'天津': {'query_str': '天津市', 'which_result': 2},
#'北京': {'query_str': '北京市', 'which_result': 2},
#'上海': {'query_str': '上海市', 'which_result': 2},
'武汉': {'query_str': '武汉市', 'which_result': 2},
#          '长沙': {'query_str': 'changsha, hunan, China', 'which_result': 2},
          # '济南': 'jinan, shandong, China',
          # '重庆': {'state': 'Chongqing', 'country': 'China'},
#          '成都': {'query_str': '成都市, 四川省, 中国', 'which_result': 1}
}

# verify OSMnx geocodes each query to what you expect
gdf = _gdf_from_places(places.values())
print(gdf)


def reverse_bearing(x):
    return x + 180 if x < 180 else x - 180


bearings = {}
for place in sorted(places.keys()):

    # get the graph
    query = places[place]['query_str']
    which_result = places[place]['which_result']
    G = ox.graph_from_place(query, network_type='drive',which_result=which_result)

    # calculate edge bearings
    Gu = ox.add_edge_bearings(ox.get_undirected(G))

    if weight_by_length:
        # weight bearings by length (meters)
        city_bearings = []
        for u, v, k, d in Gu.edges(keys=True, data=True):
            city_bearings.extend([d['bearing']] * int(d['length']))
        b = pd.Series(city_bearings)
        bearings[place] = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop='True')
    else:
        # don't weight bearings, just take one value per street segment
        b = pd.Series([d['bearing'] for u, v, k, d in Gu.edges(keys=True, data=True)])
        bearings[place] = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop='True')


def count_and_merge(n, bearings):
    # make twice as many bins as desired, then merge them in pairs
    # prevents bin-edge effects around common values like 0° and 90°
    n = n * 2
    bins = np.arange(n + 1) * 360 / n
    count, _ = np.histogram(bearings, bins=bins)

    # move the last bin to the front, so eg 0.01° and 359.99° will be binned together
    count = np.roll(count, 1)
    return count[::2] + count[1::2]


# function to draw a polar histogram for a set of edge bearings
def polar_plot(ax, bearings, n=36, title=''):
    bins = np.arange(n + 1) * 360 / n
    count = count_and_merge(n, bearings)
    _, division = np.histogram(bearings, bins=bins)
    frequency = count / count.sum()
    division = division[0:-1]
    width = 2 * np.pi / n

    ax.set_theta_zero_location('N')
    ax.set_theta_direction('clockwise')

    x = division * np.pi / 180
    bars = ax.bar(x, height=frequency, width=width, align='center', bottom=0, zorder=2,
                  color='#003366', edgecolor='k', linewidth=0.5, alpha=0.7)

    ax.set_ylim(top=frequency.max())

    title_font = {'family': 'SimHei', 'size': 24, 'weight': 'bold'}
    xtick_font = {'family': 'SimHei', 'size': 10, 'weight': 'bold', 'alpha': 1.0, 'zorder': 3}
    ytick_font = {'family': 'SimHei', 'size': 9, 'weight': 'bold', 'alpha': 0.2, 'zorder': 3}

    ax.set_title(title.upper(), y=1.05, fontdict=title_font)

    ax.set_yticks(np.linspace(0, max(ax.get_ylim()), 5))
    yticklabels = ['{:.2f}'.format(y) for y in ax.get_yticks()]
    yticklabels[0] = ''
    ax.set_yticklabels(labels=yticklabels, fontdict=ytick_font)

    xticklabels = ['N', '', 'E', '', 'S', '', 'W', '']
    ax.set_xticklabels(labels=xticklabels, fontdict=xtick_font)
    ax.tick_params(axis='x', which='major', pad=-2)


# create figure and axes
n = len(places)
ncols = int(np.ceil(np.sqrt(n)))
nrows = int(np.ceil(n / ncols))
figsize = (ncols * 5, nrows * 5)
fig, axes = plt.subplots(nrows, ncols, figsize=figsize, subplot_kw={'projection': 'polar'})

# plot each city's polar histogram
for ax, place in zip(axes.flat, sorted(places.keys())):
    polar_plot(ax, bearings[place].dropna(), title=place)

# add super title and save full image
suptitle_font = {'family': 'Century Gothic', 'fontsize': 60, 'fontweight': 'normal', 'y': 1.07}
# fig.suptitle('City Street Network Orientation', **suptitle_font)
fig.tight_layout()
fig.subplots_adjust(hspace=0.35)
fig.savefig('street-orientations.png', dpi=120, bbox_inches='tight')
plt.close()
