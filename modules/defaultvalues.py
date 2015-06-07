#!/usr/bin/env python

face_cascade_path = "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
face_cascade_sf = 1.5
face_cascade_mn = 6

eyepair_cascade_path = "/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_big.xml"
eyepair_cascade_sf = 1.05
eyepair_cascade_mn = 3

eyes_position = 0.3
eyes_width = 0.95

target_image_size = 96
min_face_size = 16
max_face_size = 256
histogram_equalization = False


if __name__ == "__main__":
	# TODO: print all default values
	pass
