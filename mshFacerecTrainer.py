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
parser.add_argument(
	"-hc", "--haar_cascade_path",
	help = "if given, cropped face images are preprocesed by face detector \
		(some kind of normalization)")
args = parser.parse_args()


## initializing variables

train_faces_images = []
train_faces_indexes = []
cropped_faces_dir = args.cropped_faces_dir
if args.haar_cascade_path:
	face_cascade = cv2.CascadeClassifier(args.haar_cascade_path)
	if face_cascade.empty():
		print "Something went wrong with Haar Cascade, exiting..."
		exit()
		
# temporary!
train_face_size = (96, 96)


## fixing cropped_faces_dir  

if cropped_faces_dir[len(cropped_faces_dir) - 1] == '/':
	cropped_faces_dir = cropped_faces_dir[:len(cropped_faces_dir) - 1]
	
	
## resursive processing of given directory
# TODO: maybe add support for different types of frames, not only .pgm?

begin_time = time.time()

for root, dirs, names in os.walk(cropped_faces_dir):
	if dirs == []:
		for name in names:
			if fnmatch.fnmatch(name, '*.pgm'):
				path = os.path.join(root, name)
				face = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
				if args.haar_cascade_path:
					haar_faces = face_cascade.detectMultiScale(face, 1.01, 5)
					if len(haar_faces) != 1:
						continue
					[x, y, w, h] = haar_faces[0]
					face = face[y:(y + h), x:(x + w)]
					face = cv2.resize(face, train_face_size)
				train_faces_images.append(np.asarray(face, dtype = np.uint8))
				index = root[root.rfind("/") + 1:]
				train_faces_indexes.append(index)
train_faces_indexes = np.asarray(train_faces_indexes, dtype = np.int32)


## training chosen face recognizer

if args.method == "eigenfaces":
	face_recognizer = cv2.createEigenFaceRecognizer()
elif args.method == "fisherfaces":
	face_recognizer = cv2.createFisherFaceRecognizer()
else:
	face_recognizer = cv2.createLBPHFaceRecognizer()
face_recognizer.train(
	np.asarray(train_faces_images), 
	np.asarray(train_faces_indexes))	
	
finish_time = time.time()
	
	
## saving trained set

xmlfile_name = cropped_faces_dir[cropped_faces_dir.rfind("/") + 1:]
xmlfile_name = xmlfile_name + "-" + args.method
face_recognizer.save(cropped_faces_dir + "/" + xmlfile_name + ".xml")


## TODO: sending report to stdout

if not args.quiet:
	if args.method != "lbph":
		print face_recognizer.getInt("ncomponents")
	print xmlfile_name \
		+ ": " \
		+ str(round(finish_time - begin_time, 2)) \
		+ " seconds"
