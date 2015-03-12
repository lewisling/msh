#!/usr/bin/env python

from sys import argv
import numpy
import cv2
import xml.etree.ElementTree as ET
import time

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

scale_factor = float(argv[1])
min_neighbors = int(argv[2])
xml_file = argv[3]
sequence_path = argv[4]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

n_frames = 0
n_total_faces = 0
n_correct_faces = 0
n_incorrect_faces = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start_time = time.time()

tree = ET.parse(xml_file)
dataset = tree.getroot()

for frame in dataset:
	frame_img = cv2.imread(sequence_path + frame.get('number') + ".jpg")
	
	frame_gray = cv2.cvtColor(frame_img, cv2.COLOR_RGB2GRAY)
	faces = \
		face_cascade.detectMultiScale(frame_gray, scale_factor, min_neighbors)

	# dla kazdego wykrytego bounding-boxa w danej ramce...
	for (x, y, w, h) in faces:
		# sprawdzam czy w danej ramce w ogole jest rzeczywiscie jakas twarz...
		if(len(frame) == 0):
			# ...jesli nie to znaczy ze ten bbox jest bledny i do odrzucenia...
			n_incorrect_faces += 1
		else:
			# ...a jesli tak, sprawdzam czy ktoras 
			# z osob ktora rzeczywiscie tam jest...
			face_in_bbox = False
			
			for person in frame:
				# ...ma swoje oczy wewnatrz wykrytego bounding-boxa
				n_eyes_in_bbox = 0
				
				for eyes in person:
					eye_x = int(eyes.get('x'))
					eye_y = int(eyes.get('y'))
					
					if((eye_x >= x and eye_x <= (x + w)) and \
						(eye_y >= y and eye_y <= (y + h))):
						n_eyes_in_bbox += 1
					
				if(n_eyes_in_bbox == 2):
					face_in_bbox = face_in_bbox ^ True
					
			if(face_in_bbox == True):
				n_correct_faces += 1
			else:
				n_incorrect_faces += 1
		
	n_total_faces += len(frame)
	n_frames += 1

stop_time = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

xml_name = xml_file[xml_file.rfind("/") + 1:]

print xml_name, \
	scale_factor, \
	min_neighbors, \
	(n_correct_faces + n_incorrect_faces), \
	n_correct_faces, \
	n_incorrect_faces, \
	n_total_faces, \
	n_frames, \
	round(stop_time - start_time, 2)  

#print "Setting for scale_factor: %s" % scale_factor
#print "Setting for min_neighbors: %s" % min_neighbors
#print "Detected faces: %s" % (n_correct_faces + n_incorrect_faces)
#print "	Correct detected faces: %s" % n_correct_faces
#print "	Incorrect detected faces: %s" % n_incorrect_faces
#print "Real faces: %s" % n_total_faces
#print "Processed frames: %s" % n_frames
#print "Execution time: %s" % (stop_time - start_time)  
