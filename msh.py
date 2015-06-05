#!/usr/bin/env python

import sys
import glob
import time
import argparse
import numpy as np
import cv2
import modules.streamreader as streamreader
import modules.facecropper as facecropper

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
	"face_cascade_path",
	help = "path to face HaarCascade")
parser.add_argument(
	"eyepair_cascade_path",
	help = "path to eyepair HaarCascade")
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
	"-fsf", "--face_cascade_sf",
	help = "face detection algorithm parameter - scale_factor",
	default = 1.5,
	type = float)
parser.add_argument(
	"-fmn", "--face_cascade_mn",
	help = "face detection algorithm parameter - min_neighbors",
	default = 6,
	type = int)
parser.add_argument(
	"-efs", "--eyepair_cascade_sf",
	help = "eyepair detection algorithm parameter - scale_factor",
	default = 1.01,
	type = float)
parser.add_argument(
	"-emn", "--eyepair_cascade_mn",
	help = "eyepair detection algorithm parameter - min_neighbors",
	default = 6,
	type = int)
parser.add_argument(
	"-ft", "--facerec_threshold",
	help = "face recognition threshold parameter, \
		bigger means less accurate",
	default = sys.float_info.max,
	type = float)
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
	"-p", "--eyes_position",
	help = "y eyes position in cropped image, given as percentage of \
		croped image height",
	default = 0.33,
	type = float)
parser.add_argument(
	"-w", "--eyes_width",
	help = "determines percentage of eyes width in cropped image width",
	default = 0.67,
	type = float)
parser.add_argument(
	"-he", "--histogram_equalization",
	help = "enable histogram equalization in processing",
	action = "store_true")
parser.add_argument(
	"-f", "--max_fps",
	help = "allows to set fps limiter",
	default = 25.0,
	type = float)
args = parser.parse_args()


## initializing variables and objects

if args.stream_type == "onefile":
	stream_reader = streamreader.OneFile(args.stream_path, args.max_fps)
elif args.stream_type == "multiplefiles":
	stream_reader = streamreader.MultipleFiles(args.stream_path)
elif args.stream_type == "stream":
	stream_reader = streamreader.Stream(args.stream_path, args.max_fps)
else:
	pass

try:
	face_cropper = facecropper.FaceCropper(
		args.face_cascade_path, args.eyepair_cascade_path,
		args.face_cascade_sf, args.eyepair_cascade_sf,
		args.face_cascade_mn, args.eyepair_cascade_mn,
		96,
		args.min_face_size, args.max_face_size,
		args.eyes_position, args.eyes_width,
		args.histogram_equalization)
except:
	raise

if args.reference_faces_path:
	reference_faces_indices = []
	reference_faces_images = []
	reference_faces_paths = sorted(
		glob.glob(args.reference_faces_path + "*.pgm"))
	for path in reference_faces_paths:
		index = int(path[path.rfind('/') + 1:path.rfind('.')])
		reference_faces_indices.append(index)
		face_img = cv2.imread(path)
		reference_faces_images.append(face_img)
	reference_faces = dict(
		zip(reference_faces_indices, reference_faces_images))

if args.facerec_method == "eigenfaces":
	face_recognizer = cv2.createEigenFaceRecognizer(0, args.facerec_threshold)
elif args.facerec_method == "fisherfaces":
	face_recognizer = cv2.createFisherFaceRecognizer(0, args.facerec_threshold)
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

# temporary!
train_face_size = (96, 96)


while(True):
	begin_time = time.time()
	
	try:
		gray_frame = stream_reader.read()
	except IOError:
		print "Something went wrong with stream"
		break
	except:
		print "End of stream"
		break
	face_images = face_cropper.get_face_images(gray_frame)
	face_locations = face_cropper.get_face_locations()
	for face_image, (x, y, w, h) in zip(face_images, face_locations):
		[label, confidence] = face_recognizer.predict(np.asarray(face_image))
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
		print "Detected id: " + str(label), \
			"\b, conf.: " + str(round(confidence)), \
			"\b, at: " + str(x) + ' ' + str(y), \
			"- " + str(x + w) + ' ' + str(y + h)
		
	finish_time = time.time()

	if args.on_screen_info:
		#~ faces = face_cropper.get_facecascade_results()
		#~ for(fx, fy, fw, fh) in faces:
			#~ cv2.rectangle(
				#~ stream_reader.current_frame, 
				#~ (fx, fy), (fx + fw, fy + fh), (255, 0, 0), 1)
		#~ eyepairs = face_cropper.get_eyepaircascade_results()
		#~ for eyepair in eyepairs:
			#~ for(ex, ey, ew, eh) in eyepair:
				#~ cv2.rectangle(
					#~ stream_reader.current_frame, 
					#~ (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 1)
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
