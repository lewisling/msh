#!/usr/bin/env python

import sys
import os
import glob
import time
import argparse
import numpy as np
import cv2
import xml.etree.ElementTree as xmlreader
import modules.facecropper

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility which crop faces from given \
		video sequence and save them in target directory.''')
parser.add_argument(
	"stream_path",
	help = "path to a video stream (accept only multiplefiles-type stream!)")
parser.add_argument(
	"target_path",
	help = "path to a directory where cropped faces will be written in \
		different subdirectories to each id")
parser.add_argument(
	"id_type",
	help = "choose sequence type",
	choices = ["xml", "person"])
parser.add_argument(
	"id_path",
	help = "path to xml with id information or person id")
parser.add_argument(
	"face_cascade_path",
	help = "path to face HaarCascade")
parser.add_argument(
	"eyepair_cascade_path",
	help = "path to eyepair HaarCascade")
parser.add_argument(
	"-s", "--cropped_image_size",
	help = "cropped image dimmension in pixels",
	default = 96,
	type = int)
parser.add_argument(
	"-p", "--eyes_position",
	help = "y eyes position in cropped image, given as percentage of \
		croped image height",
	default = 0.33,
	type = float)
parser.add_argument(
	"-w", "--eyes_width",
	help = "determines percentage of eyes width in cropped image width",
	default = 0.67,
	type = float)
parser.add_argument(
	"-t", "--output_type",
	help = "output images type",
	default = "pgm",
	choices = ["pgm", "png", "bmp"])
parser.add_argument(
	"-pf", "--prefix",
	help = "prefix added to output files")
parser.add_argument(
	"-he", "--histogram_equalization",
	help = "enable histogram equalization of output images",
	action = "store_true")
args = parser.parse_args()


## initializing variables

begin_time = time.time()

if args.stream_path[len(args.stream_path) - 1] != '/':
	args.stream_path += '/'
if args.target_path[len(args.target_path) - 1] != '/':
	args.target_path += '/'
if not os.path.exists(args.target_path):
	try:
		os.mkdir(args.target_path)
	except:
		print "Can't mkdir target directories"
		exit()
	
# frames_info[frame_path, person_id, left_eye, right_eye]
# only frames which contains someone are loaded
# it assumed that frame contains at most one face
# in case of id_type = person eye coords are filled with "-1"
frames_info = []
if args.id_type == "xml":
	try:
		xmltree = xmlreader.parse(args.id_path)
	except:
		print "ID file cannot be opened"
		exit()
	dataset = xmltree.getroot()
	for frame in dataset:
		if len(frame) == 1:
			frame_name = frame.get("number")
			for person in frame:
				if len(person) == 2:
					person_id = person.get("id")
					eye_coord = []
					for eyes in person:
						eye_coord.append(
							(int(eyes.get('x')), int(eyes.get('y'))))
					frames_info.append([
						args.stream_path + frame_name + ".jpg", 
						person_id, eye_coord[0], eye_coord[1]])
elif args.id_type == "person":
	frames_paths = sorted(glob.glob(args.stream_path + "*.jpg"))
	for frame_path in frames_paths:
		frames_info.append([frame_path, args.id_path, (-1, -1), (-1, -1)])
else:
	pass
	
try:
	face_cropper = facecropper.FaceCropper(
		args.face_cascade_path, args.eyepair_cascade_path,
		target_image_size = args.cropped_image_size,
		eyes_position = args.eyes_position, 
		eyes_width = args.eyes_width,
		histogram_equalization = args.histogram_equalization)
except:
	raise
	
target_image_size = (args.cropped_image_size, args.cropped_image_size)

if args.prefix:
	files_prefix = args.prefix
else:
	stream_path = args.stream_path[:len(args.stream_path) - 1]
	stream_name = stream_path[stream_path.rfind("/") + 1:]
	files_prefix = stream_name


## checking for subjects directories existence in target_path
## and possibly creating them if not exists

try:
	if args.id_type == "xml":
		for _, person_id, _, _ in frames_info:
			if not os.path.exists(args.target_path + person_id):
				os.mkdir(args.target_path + person_id)
	elif args.id_type == "person":
		if not os.path.exists(args.target_path + args.id_path):
			os.mkdir(args.target_path + args.id_path)
	else:
		pass
except:
	print "Can't mkdir target directories"
	exit()
	

## main processing

for (frame_path, person_id, left_eye, right_eye) in frames_info:
	frame_img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
	if frame_img == None:
		print "Reading sequence failed"
		break
	face_images = face_cropper.get_face_images(frame_img)
	if len(face_images) == 1:
		for face_image in face_images:
			frame_name = frame_path[
				frame_path.rfind('/') + 1:frame_path.rfind(".")]
			cv2.imwrite(
				args.target_path + person_id + '/' +
				files_prefix + '-' + frame_name + 
				'.' + args.output_type, 
				face_image)

finish_time = time.time()						
print "Cropping images from " + args.stream_path + \
	" took " + str(round(finish_time - begin_time)) + " seconds" 
print "Exiting..."
