#!/usr/bin/env python

from sys import argv
import time
import argparse
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
	choices = ["eigenfaces", "fisherfaces"])
parser.add_argument(
	"facerec_model_path",
	help = "path to XML file with model state for chosen \
		face recognition method")
parser.add_argument(
	"-v", "--verbose",
	help = "enable on-screen informations",
	action = "store_true")
parser.add_argument(
	"-sf", "--scale_factor",
	help = "one of the face detection algorithm parameters",
	default = 1.3,
	type = float)
parser.add_argument(
	"-mn", "--min_neighbors",
	help = "one of the face detection algorithm parameters",
	default = 5,
	type = int)
args = parser.parse_args()


## initializing variables and objects

if args.stream_type == "onefile":
	stream_reader = streamreader.OneFile(args.stream_path)
elif args.stream_type == "multiplefiles":
	stream_reader = streamreader.MultipleFiles(args.stream_path)
else:
	stream_reader = streamreader.Stream(args.stream_path)
face_cascade = cv2.CascadeClassifier(args.haar_cascade_path)


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
		cv2.rectangle(
		stream_reader.current_frame, 
		(x, y), (x + w, y + h), (255, 255, 255), 2)
		
	finish_time = time.time()

	if args.verbose:
		cv2.putText(
			stream_reader.current_frame, 
			"FPS: " + str(round(1 / (finish_time - begin_time), 2)), 
			(0, 12), 
			cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
	cv2.imshow("mlnSpyHole - main window", stream_reader.current_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break
	
		
print "Exiting..."
