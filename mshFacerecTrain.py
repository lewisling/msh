#!/usr/bin/env python

from sys import argv
import os
import fnmatch
import numpy as np
import cv2

cropped_faces_dir = argv[1]

train_faces_image = []
train_faces_index = []
train_faces_filename = []

if cropped_faces_dir[len(cropped_faces_dir) - 1] == '/':
	cropped_faces_dir = cropped_faces_dir[:len(cropped_faces_dir) - 1]

for root, dirs, names in os.walk(cropped_faces_dir):
	if dirs == []:
		for name in names:
			if fnmatch.fnmatch(name, '*.pgm'):
				path = os.path.join(root, name)
				im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
				index = root[root.rfind("/") + 1:].lstrip('0')
				train_faces_image.append(np.asarray(im, dtype = np.uint8))
				train_faces_index.append(index)
				train_faces_filename.append(path)
				
train_faces_index = np.asarray(train_faces_index, dtype = np.int32)

face_recognizer = cv2.createEigenFaceRecognizer()
face_recognizer.train(
	np.asarray(train_faces_image), 
	np.asarray(train_faces_index))	

# TODO: print report after xml generation	
print face_recognizer.getInt("ncomponents")

xmlfile_name = cropped_faces_dir[cropped_faces_dir.rfind("/") + 1:]
face_recognizer.save(cropped_faces_dir + "/" + xmlfile_name + ".xml")
