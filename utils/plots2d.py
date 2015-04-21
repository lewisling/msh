#!/usr/bin/env python

import sys
import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
import argparse

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility to plot benchmark results as bars in 
		isometric projection. Input file should contain three columns:
		parameter1, parameter2 and value linked with them. 
		Parameter 2 will be located on x-axis, parameter 1 as legend,
		value on y-axis.''')
parser.add_argument(
	"infile", 
	help = "input file with plot data",
	nargs='?', 
	type = argparse.FileType('r'),
	default = sys.stdin)
parser.add_argument(
	"param1_name",
	help = "description of first parameter")
parser.add_argument(
	"param2_name",
	help = "description of second parameter")
parser.add_argument(
	"value_name",
	help = "description of value")
parser.add_argument(
	"-lp", "--legend_position",
	help = "value of legend position for matplotlib",
	type = int,
	default = 0)
parser.add_argument(
	"-a", "--alpha",
	help = "allow to define transparency of bars",
	type = float,
	default = 0.5)
parser.add_argument(
	"-r", "--round_factor",
	help = "allow to define factor used to determine min and max values \
		of plot",
	type = float,
	default = 10.0)
args = parser.parse_args()


# load data from stdin or input file
[param1, param2, values] = np.loadtxt(args.infile, unpack = True)
data_size = len(zip(param1, param2, values))
# get labels for parameters from input data
param1_ticks = sorted(set([str(i) for i in param1]))
param2_ticks = sorted(set([str(i) for i in param2]))
# match sorted labels with natural numbers starting from zero
param1_dict = dict(itertools.izip(param1_ticks, range(len(param1_ticks))))
param2_dict = dict(itertools.izip(param2_ticks, range(len(param2_ticks))))
# change param1 and param2 to match above numbers
param1 = [param1_dict[str(i)] for i in param1]
param2 = [param2_dict[str(i)] for i in param2]


# constants for chart ploting
default_colors = ('r', 'g', 'b', 'c', 'y', 'p')
bar_offset = 0.1
# variables calculated on the basis of constants and input data
n_bars = len(param1_ticks)
n_groups = len(param2_ticks)
index = np.arange(n_groups)
bar_width = (1.0 - 2 * bar_offset) / n_bars

# plotting
fig, ax = plt.subplots()

for i in set(param1):
	plt.bar(bar_offset + index + i * bar_width, 
		[v for (p1, v) in zip(param1, values) if p1 == i], 
		bar_width,
		alpha = args.alpha,
		color = default_colors[i],
		label = args.param1_name + ' = ' + param1_ticks[i])

plt.xlabel(args.param2_name)
plt.ylabel(args.value_name)
plt.xticks(index + 0.5, param2_ticks)
ax.set_ylim(
	math.floor(min(values) * args.round_factor) / args.round_factor, 
	math.ceil(max(values) * args.round_factor) / args.round_factor)
plt.legend(loc = args.legend_position)

plt.tight_layout()
plt.show()
