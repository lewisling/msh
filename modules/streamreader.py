#!/usr/bin/env python

import time
import glob
import cv2
from skimage import io


class StreamReader(object):
	
	
	def __init__(self, path, max_fps = float('inf'), debug = True):
		self.path = path
		self.fps = max_fps
		self._frame_time = 0
		self.debug = debug
		if self.debug:
			print "~~~~~~ StreamReader created ~~~~~~"
			print "Stream path: " + self.path
		
	def __del__(self):
		if self.debug:
			print "~~~~~~ StreamReader destroyer triggered ~~~~~~"
		
	def read(self):
		delay_time = self._frame_time + (1.0 / self.fps) - time.time()
		if delay_time > 0:
			time.sleep(delay_time)
		self._frame_time = time.time()
		
		
class MultipleFiles(StreamReader):
	

	def __init__(self, path):
		super(MultipleFiles, self).__init__(path)
		if self.debug:
			print "Stream type: multiplefiles"
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		self._frames_paths = iter(sorted(glob.glob(self.path + "*.jpg")))
		
	def __del__(self):
		super(MultipleFiles, self).__del__()
		
	def read(self):
		super(MultipleFiles, self).read()
		self.current_frame = cv2.imread(next(self._frames_paths))
		if self.current_frame == None:
			raise IOError("Failed to read stream")
		self.gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
		return self.gray_frame

		
class OneFile(StreamReader):
	

	def __init__(self, path, max_fps = 25.0):
		super(OneFile, self).__init__(path, max_fps)
		if self.debug:
			print "Stream type: onefile"
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		
	def __del__(self):
		super(OneFile, self).__del__()
		
	def read(self):
		super(OneFile, self).read()
		self.current_frame = io.imread(self.path)
		self.current_frame = cv2.cvtColor(
			self.current_frame, cv2.COLOR_BGR2RGB)
		self.gray_frame = cv2.cvtColor(
			self.current_frame, cv2.COLOR_RGB2GRAY)
		return self.gray_frame
		
		
class Stream(StreamReader):
	

	def __init__(self, path, max_fps = 25.0):
		super(Stream, self).__init__(path, max_fps)
		if self.debug:
			print "Stream type: stream"
			print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		try:
			int(self.path)
		except:
			self._stream = cv2.VideoCapture(self.path)
		else:
			self._stream = cv2.VideoCapture(int(self.path))
		
	def __del__(self):
		super(Stream, self).__del__()
		self._stream.release()
		
	def read(self):
		super(Stream, self).read()
		rc, self.current_frame = self._stream.read()
		if rc == False:
			raise IOError("Failed to read stream")
		self.gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
		return self.gray_frame


if __name__ == "__main__":
	import sys
	import argparse
	
	def main():
		## commandline parsing
		# TODO: write nicer description and helps...
		
		parser = argparse.ArgumentParser(
			description = '''Class used to abstract video sequence source''')
		parser.add_argument(
			"stream_type",
			help = "type of a given stream",
			choices = ["onefile", "multiplefiles", "stream"])
		parser.add_argument(
			"stream_path",
			help = "path to the video stream")
		parser.add_argument(
			"-o", "--on_screen_info",
			help = "enable on-screen informations",
			action = "store_true")
		parser.add_argument(
			"-f", "--max_fps",
			help = "allows to set fps limiter",
			default = 25.0,
			type = float)
		args = parser.parse_args()
		
		
		if args.stream_type == "onefile":
			stream_reader = OneFile(args.stream_path, args.max_fps)
		elif args.stream_type == "multiplefiles":
			stream_reader = MultipleFiles(args.stream_path)
		elif args.stream_type == "stream":
			stream_reader = Stream(args.stream_path, args.max_fps)
		else:
			pass
			
			
		frame_time = sys.float_info.max
		while(True):
			begin_time = time.time()
			
			try:
				stream_reader.read()
			except IOError:
				print "Something went wrong with stream"
				break
			except:
				print "End of stream"
				break
			
			if args.on_screen_info:
				cv2.putText(
					stream_reader.current_frame, 
					"FPS: " + str(round(1 / frame_time, 1)), 
					(0, 12), 
					cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
			cv2.imshow("mlnSpyHole - main window", stream_reader.current_frame)
			
			if cv2.waitKey(1) & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				break
				
			frame_time = time.time() - begin_time
					
		print "Exiting..."
		
		
	main()
