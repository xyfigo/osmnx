import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
import geopandas as gpd
import collections

def reverse_bearing(x):
    return x + 180 if x < 180 else x - 180

ox.config(log_console=True, use_cache=True)
weight_by_length = False

print(ox.__version__)
query="石家庄市"
which_result=1
weight_by_length=False




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
def polar_plot(ax, place, frequency, bearings, n=1, title=''):
    bins = np.arange(n + 1) * 360 / n
    #count = count_and_merge(n, bearings)
    _, division = np.histogram(bearings, bins=bins)

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

#ox.gdf_from_place(query, which_result)
G = ox.graph_from_place(query, network_type='drive', which_result=which_result)
Gu = ox.add_edge_bearings(ox.get_undirected(G))

if weight_by_length:
    # weight bearings by length (meters)
    city_bearings = []
    for u, v, k, d in Gu.edges(keys=True, data=True):
        city_bearings.extend([d['bearing']] * int(d['length']))
    b = pd.Series(city_bearings)
    bearings = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop='True')
else:
    # don't weight bearings, just take one value per street segment
    b = pd.Series([d['bearing'] for u, v, k, d in Gu.edges(keys=True, data=True)])
    bearings = pd.concat([b, b.map(reverse_bearing)]).reset_index(drop='True')
print(bearings)

count = count_and_merge(36, bearings.dropna())
#计算频率并记录
frequencyLocal = count / count.sum()
# 计算熵并记录
entropy = np.add.reduce(-frequencyLocal * np.log(frequencyLocal))
print('Frenquency: {}, Entropy: {}'.format(frequencyLocal,entropy))

# n = len(places)
# ncols = int(np.ceil(np.sqrt(n)))
# nrows = int(np.ceil(n / ncols))
# figsize = (ncols * 5, nrows * 5)
# fig, axes = plt.subplots(nrows, ncols, figsize=figsize, subplot_kw={'projection': 'polar'})
#
# entropy={}
# frequency={}
# #计算熵并按照熵进行城市排序
# for ax, place in zip(axes.flat, places.keys()):
#     count = count_and_merge(1, bearings[place].dropna())
#     #计算频率并记录
#     frequencyLocal = count / count.sum()
#     frequency[place]=frequencyLocal
#     # 计算熵并记录
#     entropy[place] = np.add.reduce(-frequencyLocal * np.log(frequencyLocal))
#
# sorted_entropy=collections.OrderedDict(sorted(entropy.items(),key = lambda x:x[1]))
# # plot each city's polar histogram
# for ax, place in zip(axes.flat, sorted_entropy):
#     polar_plot(ax, place, frequency[place], bearings[place].dropna(), title=place)
#
# # add super title and save full image
# suptitle_font = {'family': 'Century Gothic', 'fontsize': 60, 'fontweight': 'normal', 'y': 1.07}
# # fig.suptitle('City Street Network Orientation', **suptitle_font)
# fig.tight_layout()
# fig.subplots_adjust(hspace=0.35)
# fig.savefig('street-orientations0000.png', dpi=120, bbox_inches='tight')
# plt.close()
# print(sorted_entropy)
# print('Mission Successful')
