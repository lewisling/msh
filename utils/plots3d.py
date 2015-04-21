#!/usr/bin/env python

import sys
import itertools
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import argparse

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility to plot benchmark results as bars in 
		isometric projection. Input file should contain three columns. 
		first and second describe location of a bar in 2d space,
		third column is height of the bar''')
parser.add_argument(
	"infile", 
	help = "input file with plot data",
	nargs='?', 
	type = argparse.FileType('r'),
	default = sys.stdin)
parser.add_argument(
	"xlabel",
	help = "description of x axis")
parser.add_argument(
	"ylabel",
	help = "description of y axis")
parser.add_argument(
	"zlabel",
	help = "description of z axis")
parser.add_argument(
	"-a", "--alpha",
	help = "allow to define transparency of bars",
	type = float,
	default = 0.75)
args = parser.parse_args()

# consants
bar_dim = 0.5
# load data from stdin or input file
[x, y, values] = np.loadtxt(args.infile, unpack = True)
data_size = len(zip(x, y, values))
# get labels for axes ticks from input data
x_ticks = sorted(set([str(i) for i in x]))
y_ticks = sorted(set([str(i) for i in y]))
x_dict = dict(itertools.izip(x_ticks, range(len(x_ticks))))
y_dict = dict(itertools.izip(y_ticks, range(len(y_ticks))))
# change x and y to match ticks
x = [x_dict[str(i)] for i in x]
y = [y_dict[str(i)] for i in y]
# find bounds, multiply, round and scale values to get percents and nice bars
min_value = math.floor(min(values) * 10.0) * 10
values = [i * 100 - min_value for i in values]
# add offset (for nicer bar positions in final plot)
x = [i - (bar_dim / 2.0) for i in x]
y = [i - (bar_dim / 2.0) for i in y]
# prepare color array, highest bar is marked as red
colors = np.empty(data_size, dtype = np.unicode_)
colors.fill('b')
colors[np.argmax(values)] = 'r'

fig = plt.figure()
ax = fig.add_subplot(111, projection = "3d")
ax.bar3d(
	x, y, [min_value] * data_size, 
	bar_dim, bar_dim, values, 
	alpha = args.alpha, color = colors, zsort = "max", antialiased = True)
ax.set_xlabel(args.xlabel)
ax.set_ylabel(args.ylabel)
ax.set_zlabel(args.zlabel)

plt.xticks(range(len(x_ticks)), x_ticks)
plt.yticks(range(len(y_ticks)), y_ticks)
plt.show()
