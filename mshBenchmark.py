#!/usr/bin/env python

import sys
import time
import argparse
import numpy
import cv2
import xml.etree.ElementTree as ET

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility to perform various tests against
		given test sequence and XML file descibing its frames.''')
parser.add_argument(
	"stream_path",
	help = "path to a video stream (accept only multiplefiles-type stream!)")
parser.add_argument(
	"groundtruth_xml",
	help = "path to xml file with groundtruth for given video sequence")
parser.add_argument(
	"face_cascade_path",
	help = "path to face HaarCascade")
parser.add_argument(
	"face_cascade_sf",
	help = "face detection algorithm parameter - scale_factor",
	type = float)
parser.add_argument(
	"face_cascade_mn",
	help = "face detection algorithm parameter - min_neighbors",
	type = int)
parser.add_argument(
	"eyepair_cascade_path",
	help = "path to eyepair HaarCascade")
parser.add_argument(
	"eyepair_cascade_sf",
	help = "eyepair detection algorithm parameter - scale_factor",
	type = float)
parser.add_argument(
	"eyepair_cascade_mn",
	help = "eyepair detection algorithm parameter - min_neighbors",
	type = int)
parser.add_argument(
	"facerec_method",
	help = "face recognition method",
	choices = ["eigenfaces", "fisherfaces", "lbph", "none"])
parser.add_argument(
	"facerec_model_path",
	help = "path to XML file with model state for chosen \
		face recognition method")
parser.add_argument(
	"eyes_position",
	help = "y eyes position in cropped image, given as percentage of \
		cropped image height",
	type = float)
parser.add_argument(
	"eyes_width",
	help = "determines percentage of eyes width in cropped image width",
	type = float)
parser.add_argument(
	"-he", "--histogram_equalization",
	help = "enable histogram equalization in processing",
	action = "store_true")
parser.add_argument(
	"-ft", "--facerec_threshold",
	help = "face recognition threshold parameter",
	default = sys.float_info.max,
	type = float)
parser.add_argument(
	"-s", "--cropped_image_size",
	help = "cropped image dimmension in pixels",
	default = 96,
	type = int)
args = parser.parse_args()

exit()

scale_factor = float(argv[1])
min_neighbors = int(argv[2])
xml_file = argv[3]
sequence_path = argv[4]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


## initializing variables and objects

n_frames = 0
n_total_faces = 0
n_correct_faces = 0
n_incorrect_faces = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start_time = time.time()

tree = ET.parse(xml_file)
dataset = tree.getroot()

for frame in dataset:
	frame_img = cv2.imread(sequence_path + frame.get('number') + ".jpg")
	
	frame_gray = cv2.cvtColor(frame_img, cv2.COLOR_RGB2GRAY)
	faces = \
		face_cascade.detectMultiScale(frame_gray, scale_factor, min_neighbors)

	# dla kazdego wykrytego bounding-boxa w danej ramce...
	for (x, y, w, h) in faces:
		# sprawdzam czy w danej ramce w ogole jest rzeczywiscie jakas twarz...
		if(len(frame) == 0):
			# ...jesli nie to znaczy ze ten bbox jest bledny i do odrzucenia...
			n_incorrect_faces += 1
		else:
			# ...a jesli tak, sprawdzam czy ktoras 
			# z osob ktora rzeczywiscie tam jest...
			face_in_bbox = False
			
			for person in frame:
				# ...ma swoje oczy wewnatrz wykrytego bounding-boxa
				n_eyes_in_bbox = 0
				
				for eyes in person:
					eye_x = int(eyes.get('x'))
					eye_y = int(eyes.get('y'))
					
					if((eye_x >= x and eye_x <= (x + w)) and \
						(eye_y >= y and eye_y <= (y + h))):
						n_eyes_in_bbox += 1
					
				if(n_eyes_in_bbox == 2):
					face_in_bbox = face_in_bbox ^ True
					
			if(face_in_bbox == True):
				n_correct_faces += 1
			else:
				n_incorrect_faces += 1
		
	n_total_faces += len(frame)
	n_frames += 1

stop_time = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

xml_name = xml_file[xml_file.rfind("/") + 1:]

print xml_name, \
	scale_factor, \
	min_neighbors, \
	(n_correct_faces + n_incorrect_faces), \
	n_correct_faces, \
	n_incorrect_faces, \
	n_total_faces, \
	n_frames, \
	round(stop_time - start_time, 2)
