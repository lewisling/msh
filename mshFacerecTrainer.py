#!/usr/bin/env python

from sys import argv
import os
import time
import fnmatch
import argparse
import numpy as np
import cv2

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility which trains face recognizer \
		and save model state in XML file. Result file can be used later in \
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
	choices = ["eigenfaces", "fisherfaces", "lbph"])
args = parser.parse_args()


## initializing variables

train_faces_images = []
train_faces_indices = []
cropped_faces_dir = args.cropped_faces_dir


## fixing cropped_faces_dir  

if cropped_faces_dir[len(cropped_faces_dir) - 1] == '/':
	cropped_faces_dir = cropped_faces_dir[:len(cropped_faces_dir) - 1]
	
	
## resursive processing of given directory
# TODO: maybe add support for different types of frames, not only .pgm?

begin_time = time.time()

for root, dirs, names in os.walk(cropped_faces_dir):
	if dirs == []:
		for name in names:
			if fnmatch.fnmatch(name, "*.pgm"):
				path = os.path.join(root, name)
				face = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
				train_faces_images.append(np.asarray(face, dtype = np.uint8))
				index = root[root.rfind('/') + 1:]
				train_faces_indices.append(index)
train_faces_indices = np.asarray(train_faces_indices, dtype = np.int32)


## training chosen face recognizer

if args.method == "eigenfaces":
	face_recognizer = cv2.createEigenFaceRecognizer()
elif args.method == "fisherfaces":
	face_recognizer = cv2.createFisherFaceRecognizer()
elif args.method == "lbph":
	face_recognizer = cv2.createLBPHFaceRecognizer()
else:
	pass
	
if not args.quiet:
	print "Begin training recognizer..."
face_recognizer.train(
	np.asarray(train_faces_images), 
	np.asarray(train_faces_indices))	
	
finish_time = time.time()
	
	
## saving trained set

sequence_name = cropped_faces_dir[cropped_faces_dir.rfind('/') + 1:]
xmlfile_name = sequence_name + '-' + args.method
if not args.quiet:
	print "Begin saving trained model..."
face_recognizer.save(cropped_faces_dir + '/' + xmlfile_name + ".xml")


## TODO: sending report to stdout

if not args.quiet:
	if args.method != "lbph":
		print face_recognizer.getInt("ncomponents")
	print xmlfile_name \
		+ ": " \
		+ str(round(finish_time - begin_time, 2)) \
		+ " seconds"
