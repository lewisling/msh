#!/usr/bin/env python

import sys
import os
import time
import datetime
import argparse
import cv2
import lxml.etree as xmlwriter
import modules.streamreader as streamreader

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

target_path = args.target_path[:len(args.target_path) - 1]
target_name = target_path[target_path.rfind("/") + 1:]
xml_path = args.target_path + target_name + ".xml"

grabbing_active = False

# checking if xml file in target directory exists and trying to create it,
# then, if creating was succesfull, formating basic xml, saving it and exit
try:
	open(xml_path, 'a').close()
except IOError:
	print "ERROR: Can't touch XML file in target directory"
	exit()
else:
	try:
		xmltree = xmlwriter.parse(xml_path)
	except xmlwriter.XMLSyntaxError:
		# when document is empty or something its content is deleted
		# and basic xml document is prepared
		open(xml_path, 'w').close()
		root = xmlwriter.Element("dataset")
		root.set("name", target_name)
		xmltree = xmlwriter.ElementTree(root)
dataset_root = xmltree.getroot()


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
	if grabbing_active:
		frame_name = person_id + date.strftime("-%Y_%m_%d-%H_%M_%S_%f")
		frame_entry = xmlwriter.SubElement(dataset_root, "frame")
		frame_entry.set("number", frame_name)
		person_entry = xmlwriter.SubElement(frame_entry, "person")
		person_entry.set("id", str(person_id))
		cv2.imwrite(
			args.target_path + frame_name + ".jpg", 
			stream_reader.current_frame)
	
	if args.on_screen_info:
		if grabbing_active:
			cv2.putText(
				stream_reader.current_frame, 
				"RECORDING ACTIVE", 
				(0, 12), 
				cv2.FONT_HERSHEY_PLAIN, 1.0, (128, 128, 128), 2)
		else:
			cv2.putText(
				stream_reader.current_frame, 
				"RECORDING NOT ACTIVE", 
				(0, 12), 
				cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
		cv2.putText(
			stream_reader.current_frame, 
			"FPS: " + str(round(1 / frame_time, 1)), 
			(0, 25), 
			cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
	cv2.imshow("mlnSpyHole - main window", stream_reader.current_frame)
	
	pressed_key = cv2.waitKey(1) & 0xFF
	if pressed_key == ord('q'):
		cv2.destroyAllWindows()
		break
	elif pressed_key == ord('r'):
		grabbing_active = not grabbing_active
	else:
		pass
		
	frame_time = time.time() - begin_time

try:	
	xmltree.write(xml_path, pretty_print = True, xml_declaration = True)
except:
	print "ERROR: Failed to write " + \
		xml_path + " file with frames description"
finally:
	print "Exiting..."
