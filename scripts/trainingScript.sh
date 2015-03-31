#!/bin/bash

cropped_faces_dir="/home/mln/learn/STUDIA/mgr/chokepoint/cropped_faces/"
script_path="/home/mln/code/python-projects/msh/"
script_name="mshFacerecTrainer.py"
results_file="/home/mln/code/python-projects/traintimes.txt"

methods="lbph eigenfaces fisherfaces"

for path in $cropped_faces_dir* ; do
	if [ -d "$path" ]; then
		cd $path
		for sequence in * ; do
			if [ -d "$sequence" ]; then
				for method in $methods ; do
					echo "$sequence $method"
					python $script_path$script_name \
					$path/$sequence $method \
					-hc ~/code/python-projects/tmp/haarcascade_frontalface_default.xml >> $results_file
				done
			fi
		done
	fi
done

systemctl poweroff
