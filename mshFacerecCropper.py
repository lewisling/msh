#!/usr/bin/env python

import sys
import glob
import argparse
import numpy as np
import cv2
import xml.etree.ElementTree as xmlreader
import streamreader

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility which crop faces from given \
		video sequence and save them in target directory.''')
parser.add_argument(
	"stream_type",
	help = "type of a given stream",
	choices = ["multiplefiles", "stream"])
parser.add_argument(
	"stream_path",
	help = "path to a video stream")
parser.add_argument(
	"target_path",
	help = "path to a directory where cropped faces will be written")
parser.add_argument(
	"id_type",
	help = "choose sequence type",
	choices = ["xml", "person"])
parser.add_argument(
	"id_path",
	help = "path to xml with id information or person id")
parser.add_argument(
	"-p", "--eye_position",
	help = "y eyes position in cropped image, given as percentage of \
		croped image height",
	default = 0.33,
	type = float)
parser.add_argument(
	"-w", "--eye_width",
	help = "determines percentage of eyes width in cropped image width",
	default = 0.67,
	type = float)
parser.add_argument(
	"-s", "--cropped_image_size",
	help = "cropped image dimmension in pixels",
	default = 96,
	type = int)
parser.add_argument(
	"-t", "--output_type",
	help = "output images type",
	default = "pgm",
	choices = ["pgm", "png", "bmp"])
args = parser.parse_args()


## initializing variables

if args.stream_type == "multiplefiles":
	stream_reader = streamreader.MultipleFiles(args.stream_path)
else:
	stream_reader = streamreader.Stream(args.stream_path)
	
if args.id_type == "xml":
	# frames_content[frame_name, person_id, left_eye, right_eye]
	# only frames which contains someone are loaded
	# it assumed that frame contains at most one face
	frames_content = []
	xmltree = xmlreader.parse(args.id_path)
	dataset = xmltree.getroot()
	for frame in dataset:
		if len(frame) == 1:
			frame_name = frame.get('number')
			for person in frame:
				if len(person) == 2:
					person_id = person.get('id')
					eye_coord = []
					for eyes in person:
						eye_coord.append(
							(int(eyes.get('x')), int(eyes.get('y'))))
					frames_content.append(
						[frame_name, person_id, eye_coord[0], eye_coord[1]])
else:
	pass
	
cropped_image_size = (args.cropped_image_size, args.cropped_image_size)
