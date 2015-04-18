#!/usr/bin/env python

import sys
import time
import argparse
import numpy as np
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
parser.add_argument(
	"-minf", "--min_face_size",
	help = "minimum possible face size",
	default = 0,
	type = int)
parser.add_argument(
	"-maxf", "--max_face_size",
	help = "maximum possible face size",
	default = 256,
	type = int)		
parser.add_argument(
	"-r", "--resolution",
	help = "resolution of processed stream, \
		used to scale coords from groundtruth",
	choices = ["640x480", "320x240"])
args = parser.parse_args()


## initializing variables

if args.stream_path[len(args.stream_path) - 1] != '/':
	args.stream_path += '/'

n_total_faces = 0
n_correct_faces = 0
n_incorrect_faces = 0

n_correct_eyepairs = 0
n_incorrect_eyepairs = 0

min_fps = sys.float_info.max
max_fps = 0.0

n_correct_recognitions = 0
n_incorrect_recognitions = 0
min_confidence = 0.0
max_confidence = sys.float_info.max
max_incorrect_confidence = sys.float_info.max
min_face_size = sys.maxint
max_face_size = 0
min_correct_face_size = sys.maxint
max_correct_face_size = 0

if args.resolution == "640x480":
	groundtruth_scale = 1.25
elif args.resolution == "320x240":
	groundtruth_scale = 2.5
else:
	groundtruth_scale = 1.0


## initializing objects

try:
	face_cropper = facecropper.FaceCropper(
		args.face_cascade_path, args.eyepair_cascade_path,
		args.face_cascade_sf, args.eyepair_cascade_sf,
		args.face_cascade_mn, args.eyepair_cascade_mn,
		args.cropped_image_size,
		args.min_face_size, args.max_face_size,
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
		sys.exit(1)
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
	sys.exit(1)
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
					eye_coord.append([int(eyes.get('x')), int(eyes.get('y'))])
			# "groundtruth" created by mshGrabber
			else:
				eye_coord.append([-1, -1])
				eye_coord.append([-1, -1])
	# frame without or with more than one person
	else:
		person_id = "0000"
		eye_coord.append([-1, -1])
		eye_coord.append([-1, -1])
	# apply groundtruth scaling
	eye_coord = [[int(x / groundtruth_scale), int(y / groundtruth_scale)]
		for [x, y] in eye_coord]
	frames_info.append([
		args.stream_path + frame_name + ".jpg", 
		person_id, eye_coord[0], eye_coord[1]])


## benchmark

begin_time = time.time()

for (frame_path, person_id, left_eye, right_eye) in frames_info:
	begin_frame_time = time.time()

	frame_img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
	if frame_img == None:
		print "Reading sequence failed"
		break
	face_images = face_cropper.get_face_images(frame_img)
	face_locations = face_cropper.get_face_locations()
	faces = face_cropper.get_facecascade_results()
	# for every bounding-box in frame...
	for (x, y, w, h) in faces:
		# check if there is a person...
		if person_id == None:
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
					if min(w, h) < min_face_size:
						min_face_size = min(w, h)
					if max(w, h) > max_face_size:
						max_face_size = max(w, h)
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
					
	# face recognition
	if args.facerec_method != "none":
		for face_img, (x, y, w, h) in zip(face_images, face_locations):
			[label, confidence] = face_recognizer.predict(np.asarray(face_img))
			if label == int(person_id):
				n_correct_recognitions += 1
				if min(w, h) < min_correct_face_size:
					min_correct_face_size = min(w, h)
				if max(w, h) > max_correct_face_size:
					max_correct_face_size = max(w, h)
			else:
				n_incorrect_recognitions += 1
				if confidence < max_incorrect_confidence:
					max_incorrect_confidence = confidence
			if confidence > min_confidence:
				min_confidence = confidence
			if confidence < max_confidence:
				max_confidence = confidence
			
	if person_id != "0000":	
		n_total_faces += 1
		
	frame_time = time.time() - begin_frame_time
	fps = 1 / frame_time
	if fps < min_fps:
		min_fps = fps
	if fps > max_fps:
		max_fps = fps

finish_time = time.time()


## printing benchmark results

avg_fps = len(frames_info) / (finish_time - begin_time)

print len(frames_info), \
	n_total_faces, '|', \
	args.face_cascade_sf, \
	args.face_cascade_mn, \
	n_correct_faces, \
	n_incorrect_faces, '|', \
	args.eyepair_cascade_sf, \
	args.eyepair_cascade_mn, \
	n_correct_eyepairs, \
	n_incorrect_eyepairs, '|', \
	args.facerec_method, \
	args.eyes_position, \
	args.eyes_width, \
	n_correct_recognitions, \
	n_incorrect_recognitions, '|', \
	round(min_confidence, 2), \
	round(max_confidence, 2), \
	round(max_incorrect_confidence, 2), '|', \
	min_face_size, \
	max_face_size, \
	min_correct_face_size, \
	max_correct_face_size, '|', \
	round(min_fps, 2), \
	round(max_fps, 2), \
	round(avg_fps, 2), '|', \
	round(finish_time - begin_time, 2)
