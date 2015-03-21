#!/usr/bin/env python

import sys
import os
import glob
import argparse
import numpy as np
import cv2
import xml.etree.ElementTree as xmlreader

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
parser.add_argument(
	"-pf", "--prefix",
	help = "prefix added to output files")
args = parser.parse_args()


## initializing variables

if args.stream_path[len(args.stream_path) - 1] != '/':
	args.stream_path += '/'
if args.target_path[len(args.target_path) - 1] != '/':
	args.target_path += '/'
	
if args.id_type == "xml":
	# frames_content[frame_name, person_id, left_eye, right_eye]
	# only frames which contains someone are loaded
	# it assumed that frame contains at most one face
	frames_content = []
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
					frames_content.append(
						[frame_name, person_id, eye_coord[0], eye_coord[1]])
elif args.id_type == "person":
	pass
else:
	pass
	
face_cascade = cv2.CascadeClassifier(args.face_cascade_path)
if face_cascade.empty():
	print "Something went wrong with face HaarCascade, exiting..."
	exit()
eyepair_cascade = cv2.CascadeClassifier(args.eyepair_cascade_path)
if face_cascade.empty():
	print "Something went wrong with eyepair HaarCascade, exiting..."
	exit()
	
target_image_size = (args.cropped_image_size, args.cropped_image_size)

if args.prefix:
	files_prefix = args.prefix
else:
	stream_path = args.stream_path[:len(args.stream_path) - 1]
	stream_name = stream_path[stream_path.rfind("/") + 1:]
	files_prefix = stream_name


## checking for subjects directories existence in target_path
## and possibly creating them if not exists

if args.id_type == "xml":
	for _, person_id, _, _ in frames_content:
		if not os.path.exists(args.target_path + person_id):
			os.mkdir(args.target_path + person_id)
elif args.id_type == "person":
	if not os.path.exists(args.target_path + args.id_path):
		os.mkdir(args.target_path + args.id_path)
else:
	pass


## creating array with frames paths to process further

if args.id_type == "xml":
	frames_paths = []
	for i, _, _, _ in frames_content:
		frames_paths.append(args.stream_path + i + ".jpg")
elif args.id_type == "person":
	frames_paths = sorted(glob.glob(args.stream_path + "*.jpg"))
	pass
else:
	pass
	

## main processing

for frame in frames_paths:
	try:
		frame_img = cv2.imread(frame, cv2.IMREAD_GRAYSCALE)
	except:
		print "Reading sequence failed"
		break
	faces = face_cascade.detectMultiScale(frame_img, 1.5, 6)
	for (x, y, w, h) in faces:
		face_area = frame_img[y:(y + h), x:(x + w)]
		eyes = eyepair_cascade.detectMultiScale(face_area, 1.01, 5)
		if len(eyes) == 1:
			for (ex, ey, ew, eh) in eyes:			
				face_size = ew / args.eye_width
				# xy between eyes in frame_img
				eyes_center_x = ex + ew / 2 + x
				eyes_center_y = ey + eh / 2 + y
				face_x = eyes_center_x - (face_size / 2)
				face_y = eyes_center_y - (face_size * args.eye_position)
				print face_x, face_y, face_size
				if (face_x >= 0 and face_y >= 0 and
					face_x + face_size < frame_img.shape[1] and 
					face_y + face_size < frame_img.shape[0]):
					face_img = frame_img[
						face_y:(face_y + face_size), 
						face_x:(face_x + face_size)]
					face_img = cv2.resize(face_img, target_image_size)
					# TODO: cropped_face_img saving

cv2.destroyAllWindows()
print "Exiting..."
