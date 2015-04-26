#!/usr/bin/env python

import cv2


class FaceCropper(object):
	
			
	def __init__(
			self, 
			face_cascade_path, eyepair_cascade_path,
			face_cascade_sf = 1.5, eyepair_cascade_sf = 1.01,
			face_cascade_mn = 6, eyepair_cascade_nm = 6,
			target_image_size = 96,
			min_face_size = 0, max_face_size = 256,
			eyes_position = 0.35, eyes_width = 0.95,
			histogram_equalization = False,
			debug = True):
		self.face_cascade_sf = face_cascade_sf
		self.face_cascade_mn = face_cascade_mn
		self.eyepair_cascade_sf = eyepair_cascade_sf
		self.eyepair_cascade_nm = eyepair_cascade_nm
		self.target_image_size = (target_image_size, target_image_size)
		self.min_face_size = (min_face_size, min_face_size)
		self.max_face_size = (max_face_size, max_face_size)
		self.eyes_position = eyes_position
		self.eyes_width = eyes_width
		self.histogram_equalization = histogram_equalization
		self.debug = debug
		self._face_images = []
		self._face_locations = []
		
		self._face_cascade = cv2.CascadeClassifier(face_cascade_path)
		if self._face_cascade.empty():
			raise IOError("Face cascade loading failed")
		self._eyepair_cascade = cv2.CascadeClassifier(eyepair_cascade_path)
		if self._eyepair_cascade.empty():
			raise IOError("Eyepair cascade loading failed")
			
		if self.debug:
			print "~~~~~~ FaceCropper created ~~~~~~"
			print "Face cascade: " + str(face_cascade_path)
			print "scale factor: " + str(face_cascade_sf), 
			print "\b, min neighbors: " + str(face_cascade_mn) + '\n'
			print "Eyepair cascade: " + str(eyepair_cascade_path)
			print "scale factor: " + str(eyepair_cascade_sf),
			print "\b, min neighbors: " + str(eyepair_cascade_nm) + '\n'
			print "Eyes y-position: " + str(self.eyes_position), 
			print "\b, eyes width: " + str(self.eyes_width)
			print "Face size dimensions:",
			print "min: " + str(self.min_face_size), 
			print "\b, max: " + str(self.max_face_size)
			print "Cropped image dimensions:",
			print self.target_image_size
			print "Histogram equalization:",
			print self.histogram_equalization
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		
	def __del__(self):
		if self.debug:
			print "~~~~~~ FaceCropper destroyer triggered ~~~~~~"
		
	def get_face_images(self, frame_img):
		self._face_images = []
		self._face_locations = []
		self._facecascade_results = []
		self._eyepaircascade_results = []
		
		self._facecascade_results = self._face_cascade.detectMultiScale(
			frame_img, self.face_cascade_sf, self.face_cascade_mn,
			minSize = self.min_face_size, maxSize = self.max_face_size)
		for (x, y, w, h) in self._facecascade_results:
			face_area = frame_img[y:(y + h), x:(x + w)]
			eyes = self._eyepair_cascade.detectMultiScale(
				face_area, self.eyepair_cascade_sf, self.eyepair_cascade_nm)
			# adding bbox position to coords of detected eyepair
			eyes = [(ex + x, ey + y, ew, eh) for (ex, ey, ew, eh) in eyes]
			self._eyepaircascade_results.append(eyes)
			if len(eyes) == 1:
				for (ex, ey, ew, eh) in eyes:			
					face_size = ew / self.eyes_width
					# xy between eyes in frame_img
					eyes_center_x = ex + ew / 2
					eyes_center_y = ey + eh / 2
					face_x = eyes_center_x - (face_size / 2)
					face_y = eyes_center_y - (face_size * self.eyes_position)
					if (face_x >= 0 and face_y >= 0 and
						face_x + face_size < frame_img.shape[1] and 
						face_y + face_size < frame_img.shape[0]):
							face_img = frame_img[
								face_y:(face_y + face_size), 
								face_x:(face_x + face_size)]
							face_img = cv2.resize(
								face_img, self.target_image_size)
							if self.histogram_equalization:
								face_img = cv2.equalizeHist(face_img)
							self._face_images.append(face_img)
							self._face_locations.append([
								int(face_x), int(face_y), 
								int(face_size), int(face_size)])
							
		return self._face_images
		
	def get_facecascade_results(self):
		return self._facecascade_results
		
	def get_eyepaircascade_results(self):
		return self._eyepaircascade_results
							
	def get_face_locations(self):
		return self._face_locations
		
		
if __name__ == "__main__":
	import sys
	import argparse
	
	## commandline parsing
	# TODO: write nicer description and helps...
	
	parser = argparse.ArgumentParser(
		description = '''Class used to crop faces from given image, \
			based on face area detection and pair of eyes location.''')
	parser.add_argument(
		"image_path",
		help = "path to an image which is intended for processing")
	parser.add_argument(
		"face_cascade_path",
		help = "path to face HaarCascade")
	parser.add_argument(
		"eyepair_cascade_path",
		help = "path to eyepair HaarCascade")
	parser.add_argument(
		"-fsf", "--face_cascade_sf",
		help = "face detection algorithm parameter - scale_factor",
		default = 1.2,
		type = float)
	parser.add_argument(
		"-fmn", "--face_cascade_mn",
		help = "face detection algorithm parameter - min_neighbors",
		default = 6,
		type = int)
	parser.add_argument(
		"-esf", "--eyepair_cascade_sf",
		help = "eyepair detection algorithm parameter - scale_factor",
		default = 1.01,
		type = float)
	parser.add_argument(
		"-emn", "--eyepair_cascade_mn",
		help = "eyepair detection algorithm parameter - min_neighbors",
		default = 5,
		type = int)
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
	args = parser.parse_args()


	## initializing variables and objects
	
	try:
		face_cropper = FaceCropper(
			args.face_cascade_path, args.eyepair_cascade_path,
			args.face_cascade_sf, args.eyepair_cascade_sf,
			args.face_cascade_mn, args.eyepair_cascade_mn,
			args.cropped_image_size,
			args.min_face_size, args.max_face_size,
			args.eyes_position, args.eyes_width,
			args.histogram_equalization)
	except:
		raise
		
	frame = cv2.imread(args.image_path)
	if frame == None:
		print "Failed to load frame image, exiting..."
		exit()
		
	
	## testing

	gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	face_images = face_cropper.get_face_images(gray_frame)
	face_locations = face_cropper.get_face_locations()
	for face_image, (x, y, w, h) in zip(face_images, face_locations):
		cv2.imshow("Face: " + str(x) + ' ' + str(y), face_image)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
		print "Face location: " + str(x), str(y), str(w), str(h)
	cv2.imshow("Input frame", frame)
		
	if cv2.waitKey(0) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		exit()
