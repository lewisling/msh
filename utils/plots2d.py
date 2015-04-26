#!/usr/bin/env python

import sys
import itertools
import math
import csv
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
parser.add_argument(
	"-p1r", "--param1_reverse",
	help = "reverse sorting of param1 values",
	action = "store_true")
parser.add_argument(
	"-p2r", "--param2_reverse",
	help = "reverse sorting of param2 values",
	action = "store_true")
parser.add_argument(
	"-d", "--disable_legend_name",
	help = "disable displaying parameter name in legend",
	action = "store_true")
parser.add_argument(
	"-c", "--colors",
	help = "string with color names (first letter of color)")
args = parser.parse_args()


# load data from stdin or input file
[param1, param2, values] = np.loadtxt(
	args.infile, dtype = np.str, unpack = True)
# TEMPORARY: printing input data for manual checking with drawn plots
for (p1, p2, v) in zip(param1, param2, values):
	print p1, p2, v
# sorting input data
sorted_data = sorted(zip(param1, param2, values))
param1 = [p1 for (p1, _, _) in sorted_data]
param2 = [p2 for (_, p2, _) in sorted_data]
values = [v for (_, _, v) in sorted_data]
data_size = len(zip(param1, param2, values))
# get labels for parameters from input data
param1_ticks = sorted(set(param1), reverse = args.param1_reverse)
param2_ticks = sorted(set(param2), reverse = args.param2_reverse)
# match sorted labels with natural numbers starting from zero
param1_dict = dict(itertools.izip(param1_ticks, range(len(param1_ticks))))
param2_dict = dict(itertools.izip(param2_ticks, range(len(param2_ticks))))
# change param1 and param2 to match above numbers
param1 = [param1_dict[i] for i in param1]
param2 = [param2_dict[i] for i in param2]
# convert values from string to float
values = [float(i) for i in values]

# constants for chart ploting
if args.colors:
	colors = list(args.colors)
else:
	colors = ['r', 'g', 'b', 'c', 'y', 'p']
bar_offset = 0.1
# variables calculated on the basis of constants and input data
n_bars = len(param1_ticks)
n_groups = len(param2_ticks)
index = np.arange(n_groups)
bar_width = (1.0 - 2 * bar_offset) / n_bars

# plotting
fig, ax = plt.subplots()

for i in set(param1):
	if args.disable_legend_name:
		label = param1_ticks[i]
	else:
		label = args.param1_name + ' = ' + param1_ticks[i]
	plt.bar(bar_offset + i * bar_width + index, 
		[v for (p1, v) in zip(param1, values) if p1 == i], 
		bar_width,
		alpha = args.alpha,
		color = colors[i],
		label = label)

plt.xlabel(args.param2_name)
plt.ylabel(args.value_name)
plt.xticks(index + 0.5, param2_ticks)
ax.yaxis.grid(True)
ax.set_ylim(
	math.floor(min(values) * args.round_factor) / args.round_factor, 
	math.ceil(max(values) * args.round_factor) / args.round_factor)
if n_bars > 1:
	plt.legend(loc = args.legend_position)

plt.tight_layout()
plt.show()
