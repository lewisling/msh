#!/usr/bin/env python

import sys
import time
import argparse
import numpy
import cv2
import xml.etree.ElementTree as xmlreader
import modules.facecropper as facecropper

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


## initializing variables

if args.stream_path[len(args.stream_path) - 1] != '/':
	args.stream_path += '/'

n_total_faces = 0
n_correct_faces = 0
n_incorrect_faces = 0

n_correct_eyepairs = 0
n_incorrect_eyepairs = 0

min_fps = 0.0
avg_fps = 0.0
max_fps = 0.0

n_correct_recognitions = 0
n_incorrect_recognitions = 0
min_confidence = 0.0
avg_confidence = 0.0
max_confidence = 0.0
min_incorrect_confidence = 0.0


## initializing objects

try:
	face_cropper = facecropper.FaceCropper(
		args.face_cascade_path, args.eyepair_cascade_path,
		args.face_cascade_sf, args.eyepair_cascade_sf,
		args.face_cascade_mn, args.eyepair_cascade_mn,
		args.cropped_image_size,
		args.eyes_position, args.eyes_width,
		args.histogram_equalization,
		False)
except:
	raise
	
if args.facerec_method != "none":
	if args.facerec_method == "eigenfaces":
		face_recognizer = cv2.createEigenFaceRecognizer(
			0, args.facerec_threshold)
	elif args.facerec_method == "fisherfaces":
		face_recognizer = cv2.createFisherFaceRecognizer(
			0, args.facerec_threshold)
	elif args.facerec_method == "lbph":
		face_recognizer = cv2.createLBPHFaceRecognizer(
			1, 8, 8, 8, args.facerec_threshold)
	else:
		pass
	try:
		face_recognizer.load(args.facerec_model_path)
	except:
		print "Something went wrong face recognizer model, exiting..."
		exit()
else:
	pass
	
# frames_info[frame_path, person_id, left_eye, right_eye]
# It is assumed that frame contains at most one face.
# In case of groundtruth file created by mshGrabber 
# eye coords are filled with "-1".
frames_info = []
try:
	xmltree = xmlreader.parse(args.groundtruth_xml)
except:
	print "groundtruth xml cannot be opened"
	exit()
dataset = xmltree.getroot()
for frame in dataset:
	eye_coord = []
	frame_name = frame.get("number")
	# frame with a person
	if len(frame) == 1:
		for person in frame:
			person_id = person.get("id")
			# groundtruth from chokepoint
			if len(person) == 2:
				for eyes in person:
					eye_coord.append((int(eyes.get('x')), int(eyes.get('y'))))
			# "groundtruth" created by mshGrabber
			else:
				eye_coord.append((-1, -1))
				eye_coord.append((-1, -1))
	# frame without or with more than one person
	else:
		person_id = None
		eye_coord.append((-1, -1))
		eye_coord.append((-1, -1))
	frames_info.append([
		args.stream_path + frame_name + ".jpg", 
		person_id, eye_coord[0], eye_coord[1]])


## benchmark

begin_time = time.time()

for (frame_path, person_id, left_eye, right_eye) in frames_info:
	frame_img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
	if frame_img == None:
		print "Reading sequence failed"
		break
	face_cropper.get_face_images(frame_img)
	faces = face_cropper.get_facecascade_results()
	# for every bounding-box in frame...
	for (x, y, w, h) in faces:
		# check if there is a person...
		if(person_id == None):
			# if not, then bounding-box is incorrect...
			n_incorrect_faces += 1
		else:
			# ...if so, then check if someone's face is surrounded 
			# by the bounding-box and has its eyes therein	
			if(
				(left_eye[0] >= x and left_eye[0] <= (x + w)) and \
				(left_eye[1] >= y and left_eye[1] <= (y + h)) and \
				(right_eye[0] >= x and right_eye[0] <= (x + w)) and \
				(right_eye[1] >= y and right_eye[1] <= (y + h))):
					n_correct_faces += 1
			else:
				n_incorrect_faces += 1
	eyepairs = face_cropper.get_eyepaircascade_results()
	# the same way as above but for eyepairs
	for eyepair in eyepairs:
		for (ex, ey, ew, eh) in eyepair:
			if(person_id == None):
				n_incorrect_eyepairs += 1
			else:
				if(
					(left_eye[0] >= ex and left_eye[0] <= (ex + ew)) and \
					(left_eye[1] >= ey and left_eye[1] <= (ey + eh)) and \
					(right_eye[0] >= ex and right_eye[0] <= (ex + ew)) and \
					(right_eye[1] >= ey and right_eye[1] <= (ey + eh))):
						n_correct_eyepairs += 1
				else:
					n_incorrect_eyepairs += 1
	if(person_id != None):	
		n_total_faces += 1

finish_time = time.time()


## printing benchmark results

print args.face_cascade_sf, \
	args.face_cascade_mn, \
	(n_correct_faces + n_incorrect_faces), \
	n_correct_faces, \
	n_incorrect_faces, \
	n_total_faces, \
	n_correct_eyepairs, \
	n_incorrect_eyepairs, \
	len(frames_info), \
	round(finish_time - begin_time, 2)
