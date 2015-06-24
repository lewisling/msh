#!/usr/bin/env python

import modules.defaultvalues as dv
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
	"stream_path",
	help = "path to the video stream")
parser.add_argument(
	"facerec_model_path",
	help = "path to the directory which containts XML file with model state \
		for chosen face recognition method")
parser.add_argument(
	"-t", "--stream_type",
	help = "type of a given stream",
	choices = ["onefile", "multiplefiles", "stream"],
	default = "onefile")
parser.add_argument(
	"-m", "--facerec_method",
	help = "choose face recognition method for which training is performed",
	choices = ["eigenfaces", "fisherfaces", "lbph"],
	default = "lbph")
parser.add_argument(
	"-n", "--no_osd",
	help = "disable on-screen informations",
	action = "store_true")
parser.add_argument(
	"-rf", "--reference_faces_path",
	help = "enable displaying miniatures of detected id, \
		taken from given path")
parser.add_argument(
	"-fcp", "--face_cascade_path",
	help = "path to face HaarCascade",
	default=dv.face_cascade_path)
parser.add_argument(
	"-ecp", "--eyepair_cascade_path",
	help = "path to eyepair HaarCascade",
	default=dv.eyepair_cascade_path)
parser.add_argument(
	"-fsf", "--face_cascade_sf",
	help = "face detection algorithm parameter - scale_factor",
	default = dv.face_cascade_sf,
	type = float)
parser.add_argument(
	"-fmn", "--face_cascade_mn",
	help = "face detection algorithm parameter - min_neighbors",
	default = dv.face_cascade_mn,
	type = int)
parser.add_argument(
	"-esf", "--eyepair_cascade_sf",
	help = "eyepair detection algorithm parameter - scale_factor",
	default = dv.eyepair_cascade_sf,
	type = float)
parser.add_argument(
	"-emn", "--eyepair_cascade_mn",
	help = "eyepair detection algorithm parameter - min_neighbors",
	default = dv.eyepair_cascade_mn,
	type = int)
parser.add_argument(
	"-s", "--cropped_image_size",
	help = "cropped image dimmension in pixels",
	default = dv.target_image_size,
	type = int)
parser.add_argument(
	"-minf", "--min_face_size",
	help = "minimum possible face size",
	default = dv.min_face_size,
	type = int)
parser.add_argument(
	"-maxf", "--max_face_size",
	help = "maximum possible face size",
	default = dv.max_face_size,
	type = int)		
parser.add_argument(
	"-p", "--eyes_position",
	help = "y eyes position in cropped image, given as percentage of \
		croped image height",
	default = dv.eyes_position,
	type = float)
parser.add_argument(
	"-w", "--eyes_width",
	help = "determines percentage of eyes width in cropped image width",
	default = dv.eyes_width,
	type = float)
parser.add_argument(
	"-he", "--histogram_equalization",
	help = "enable histogram equalization in processing",
	action = "store_true")
parser.add_argument(
	"-ft", "--facerec_threshold",
	help = "face recognition threshold parameter, \
		bigger means less accurate",
	default = sys.float_info.max,
	type = float)
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
	stream_reader = streamreader.MultipleFiles(args.stream_path, float('inf'))
elif args.stream_type == "stream":
	stream_reader = streamreader.Stream(args.stream_path, args.max_fps)
else:
	pass

if args.reference_faces_path != None:
	if args.reference_faces_path[len(args.reference_faces_path) - 1] != '/':
		args.reference_faces_path += '/'
		
if args.facerec_model_path[len(args.facerec_model_path) - 1] != '/':
	args.facerec_model_path += '/'
args.facerec_model_path = args.facerec_model_path + \
	"model-" + args.facerec_method + ".xml"

try:
	face_cropper = facecropper.FaceCropper(
		args.face_cascade_path, args.eyepair_cascade_path,
		args.face_cascade_sf, args.eyepair_cascade_sf,
		args.face_cascade_mn, args.eyepair_cascade_mn,
		args.cropped_image_size,
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

	if not args.no_osd:
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
