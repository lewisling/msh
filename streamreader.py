#!/usr/bin/env python

import glob
import cv2
from skimage import io


class StreamReader(object):
	
	
	def __init__(self, path):
		self.path = path
		print "~~~~~~ StreamReader created ~~~~~~"
		print "Stream path: " + self.path
		
	def __del__(self):
		print "~~~~~~ StreamReader destroyer triggered ~~~~~~"
		
	def read(self):
		pass
		
		
class MultipleFiles(StreamReader):
	

	def __init__(self, path):
		super(MultipleFiles, self).__init__(path)
		print "Stream type: multiplefiles"
		self._frames_paths = iter(sorted(glob.glob(self.path + "*.jpg")))
		
	def __del__(self):
		super(MultipleFiles, self).__del__()
		
	def read(self):
		self.current_frame = cv2.imread(next(self._frames_paths))
		self.gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2GRAY)
		return self.gray_frame

		
class OneFile(StreamReader):
	

	def __init__(self, path):
		super(OneFile, self).__init__(path)
		print "Stream type: onefile"
		
	def __del__(self):
		super(OneFile, self).__del__()
		
	def read(self):
		self.current_frame = io.imread(self.path)
		self.gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
		return self.gray_frame
		
		
class Stream(StreamReader):
	

	def __init__(self, path):
		super(Stream, self).__init__(path)
		print "Stream type: stream"
		self._stream = cv2.VideoCapture(self.path)
		
	def __del__(self):
		super(Stream, self).__del__()
		
	def read(self):
		_, self.current_frame = self._stream.read()
		self.gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
		return self.gray_frame
