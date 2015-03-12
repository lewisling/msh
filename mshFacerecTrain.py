#!/usr/bin/env python

from sys import argv
import os
import fnmatch
import numpy as np
import cv2
import argparse

## commandline parsing
## TODO: write nicer description and helps...
parser = argparse.ArgumentParser(
	description = '''Small utility which trains face recognizer \
		and save results in XML file. Result file can be used later in \
		application that rely on Eigenfaces or Fisherfaces.''')
parser.add_argument(
	"cropped_faces_dir", 
	help = "path to properly prepared directory which contains cropped faces")
parser.add_argument(
	"-q", "--quiet",
	help = "disable output verbosity",
	action = "store_true")
parser.add_argument(
	"method",
	help = "choose face recognition method for which training is performed",
	choices = ["eigenfaces", "fisherfaces"])
args = parser.parse_args()

## initializing variables
cropped_faces_dir = args.cropped_faces_dir
train_faces_image = []
train_faces_index = []

## fixing cropped_faces_dir  
if cropped_faces_dir[len(cropped_faces_dir) - 1] == '/':
	cropped_faces_dir = cropped_faces_dir[:len(cropped_faces_dir) - 1]
	
## resursive processing of given directory
## TODO: maybe add support for different types of frames, not only .pgm?
for root, dirs, names in os.walk(cropped_faces_dir):
	if dirs == []:
		for name in names:
			if fnmatch.fnmatch(name, '*.pgm'):
				path = os.path.join(root, name)
				im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
				index = root[root.rfind("/") + 1:]
				train_faces_image.append(np.asarray(im, dtype = np.uint8))
				train_faces_index.append(index)
				
train_faces_index = np.asarray(train_faces_index, dtype = np.int32)

## training chosen face recognizer
if args.method == "eigenface":
	face_recognizer = cv2.createEigenFaceRecognizer()
else:
	face_recognizer = cv2.createFisherFaceRecognizer()
face_recognizer.train(
	np.asarray(train_faces_image), 
	np.asarray(train_faces_index))	
	
## saving trained set
xmlfile_name = cropped_faces_dir[cropped_faces_dir.rfind("/") + 1:]
xmlfile_name = xmlfile_name + "-" + args.method
face_recognizer.save(cropped_faces_dir + "/" + xmlfile_name + ".xml")

## TODO: sending report to stdout
if not args.quiet:
	print face_recognizer.getInt("ncomponents")
