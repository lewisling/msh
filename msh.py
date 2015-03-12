#!/usr/bin/env python

import cv2
import streamreader
from sys import argv

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

stream_path = argv[1]
haar_cascade_xml_path = argv[2]

face_cascade = cv2.CascadeClassifier(haar_cascade_xml_path)
stream_reader = streamreader.MultipleFiles(stream_path)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

while(True):
	try:
		gray_frame = stream_reader.read()
	except:
		print "End of stream"
		break
		
	faces = face_cascade.detectMultiScale(gray_frame, 2, 5)
	for (x,y,w,h) in faces:
		cv2.rectangle(
		stream_reader.current_frame, 
		(x, y), (x + w, y + h), (255, 0, 0), 2)
  
	cv2.imshow("mlnSpyHole - main window", stream_reader.current_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break
		
print "Exiting..."
