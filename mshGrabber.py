#!/usr/bin/env python

import sys
import os
import time
import datetime
import argparse
import cv2
import streamreader

## commandline parsing
# TODO: write nicer description and helps...

parser = argparse.ArgumentParser(
	description = '''Small utility to grab frames from given stream \
		and save them in a specified dir''')
parser.add_argument(
	"stream_type",
	help = "type of a given stream",
	choices = ["onefile", "stream"])
parser.add_argument(
	"stream_path",
	help = "path to the video stream")
parser.add_argument(
	"target_path",
	help = "path to a directory where grabbed frames will be written")
parser.add_argument(
	"identifier",
	help = "id of person in sequence",
	type = int)
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

if args.identifier <= 0:
	print "Person id should be > 0"
	exit()
	
if args.max_fps <= 0:
	print "FPS limiter should be set at value > 0"
	exit()


## initializing variables and objects

if args.stream_type == "onefile":
	stream_reader = streamreader.OneFile(args.stream_path, args.max_fps)
elif args.stream_type == "stream":
	stream_reader = streamreader.Stream(args.stream_path, args.max_fps)
else:
	pass
	
if args.stream_path[len(args.stream_path) - 1] != '/':
	args.stream_path += '/'
if args.target_path[len(args.target_path) - 1] != '/':
	args.target_path += '/'
if not os.path.exists(args.target_path):
	try:
		os.mkdir(args.target_path)
	except:
		print "Can't mkdir target directories"
		exit()

person_id = str(args.identifier).rjust(4, '0')

## main loop with frame grabbing

frame_time = sys.float_info.max
while(True):
	begin_time = time.time()
	
	try:
		stream_reader.read()
	except IOError:
		print "Something went wrong with stream"
		break
		
	date = datetime.datetime.now()
	cv2.imwrite(
		args.target_path + 
		person_id + 
		date.strftime("-%Y_%m_%d-%H_%M_%S_%f") + ".jpg", 
		stream_reader.current_frame)
	
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
