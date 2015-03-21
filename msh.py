#!/usr/bin/env python

import sys
import glob
import time
import argparse
import numpy as np
import cv2
import streamreader

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Main program which perform processing on the given \
		video stream and send results to stdout.''')
parser.add_argument(
	"stream_type",
	help = "type of a given stream",
	choices = ["onefile", "multiplefiles", "stream"])
parser.add_argument(
	"stream_path",
	help = "path to the video stream")
parser.add_argument(
	"haar_cascade_path",
	help = "path to XML file which contains trained HaarCascade")
parser.add_argument(
	"facerec_method",
	help = "face recognition method",
	choices = ["eigenfaces", "fisherfaces", "lbph"])
parser.add_argument(
	"facerec_model_path",
	help = "path to XML file with model state for chosen \
		face recognition method")
parser.add_argument(
	"-o", "--on_screen_info",
	help = "enable on-screen informations",
	action = "store_true")
parser.add_argument(
	"-rf", "--reference_faces_path",
	help = "enable displaying miniatures of detected id, \
		taken from given path")
parser.add_argument(
	"-v", "--verbose",
	help = "print various informations to stdout",
	action = "store_true")
parser.add_argument(
	"-sf", "--scale_factor",
	help = "one of the face detection algorithm parameters",
	default = 1.5,
	type = float)
parser.add_argument(
	"-mn", "--min_neighbors",
	help = "one of the face detection algorithm parameters",
	default = 6,
	type = int)
parser.add_argument(
	"-ft", "--facerec_threshold",
	help = "face recognition threshold parameter, \
		bigger means less accurate",
	default = sys.float_info.max,
	type = float)
args = parser.parse_args()


## initializing variables and objects

if args.stream_type == "onefile":
	stream_reader = streamreader.OneFile(args.stream_path)
elif args.stream_type == "multiplefiles":
	stream_reader = streamreader.MultipleFiles(args.stream_path)
else:
	stream_reader = streamreader.Stream(args.stream_path)
face_cascade = cv2.CascadeClassifier(args.haar_cascade_path)

if args.reference_faces_path:
	reference_faces_indices = []
	reference_faces_images = []
	reference_faces_paths = sorted(
		glob.glob(args.reference_faces_path + '*.pgm'))
	for path in reference_faces_paths:
		index = int(path[path.rfind("/") + 1:path.rfind(".")])
		reference_faces_indices.append(index)
		face_img = cv2.imread(path)
		reference_faces_images.append(face_img)
	reference_faces = dict(
		zip(reference_faces_indices, reference_faces_images))

if args.facerec_method == "eigenfaces":
	face_recognizer = cv2.createEigenFaceRecognizer(0, args.facerec_threshold)
elif args.facerec_method == "fisherfaces":
	face_recognizer = cv2.createFisherFaceRecognizer(0, args.facerec_threshold)
else:
	face_recognizer = cv2.createLBPHFaceRecognizer(
		1, 8, 8, 8, args.facerec_threshold)
face_recognizer.load(args.facerec_model_path)

# temporary!
train_face_size = (96, 96)


while(True):
	begin_time = time.time()
	
	try:
		gray_frame = stream_reader.read()
	except:
		print "End of stream"
		break
		
	faces = face_cascade.detectMultiScale(
		gray_frame, args.scale_factor, args.min_neighbors)
	for (x, y, w, h) in faces:
		face_img = gray_frame[y:(y + h), x:(x + w)]
		face_img = cv2.resize(face_img, train_face_size)
		[label, confidence] = face_recognizer.predict(np.asarray(face_img))
		cv2.rectangle(
			stream_reader.current_frame, 
			(x, y), (x + w, y + h), (255, 255, 255), 1)
		if label != -1:
			cv2.putText(
				stream_reader.current_frame, 
				"ID: " + str(label) + " , conf.: " + str(round(confidence)), 
				(x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
			if args.reference_faces_path:
				cv2.imshow("mlnSpyHole - face window", reference_faces[label])
		
	finish_time = time.time()

	if args.on_screen_info:
		cv2.putText(
			stream_reader.current_frame, 
			"FPS: " + str(round(1 / (finish_time - begin_time), 1)), 
			(0, 12), 
			cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
	cv2.imshow("mlnSpyHole - main window", stream_reader.current_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break
	
		
print "Exiting..."
