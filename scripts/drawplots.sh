#!/bin/bash

E_WRONG_ARGS=85

# add parent directory (with msh apps) to PATH
PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd ):$PATH

face_cascade_sfs="1.1 1.2 1.5 2.0 3.0"
face_cascade_mns="3 4 5 6"
eyepair_cascade_sfs="1.01 1.05 1.1 1.2"
eyepair_cascade_mns="3 4 5 6"
eyes_positions="0.2 0.25 0.3"
eyes_widths="0.7 0.8 0.9 0.95"
resolutions="800x600 640x480 320x240"
facerec_methods="eigenfaces fisherfaces lbph"

case "$#" in
	1)
		cd $1
		;;
	*)
		echo "Usage: $(basename $0) tests_path"
		exit $E_WRONG_ARGS
		;;
esac

echo $(pwd)

# TODO: face detection plots
#~ for resolution in $resolutions
#~ do
	#~ > results-facedetector-$resolution
	#~ for sf in $face_cascade_sfs
	#~ do
		#~ for mn in $face_cascade_mns
		#~ do
			#~ cat results_facedetector-$resolution-* | \
			#~ awk -vsf="$sf" -vmn="$mn" \
			#~ '{if($4 == sf && $5 == mn) \
				#~ {groundtruth_faces+=$2; \
					#~ correct_faces+=$6; incorrect_faces+=$7; \
					#~ fps+=$31; num+=1;}} \
				#~ END {print sf, mn, \
					#~ groundtruth_faces, correct_faces+incorrect_faces, \
					#~ correct_faces, incorrect_faces, fps/num}' \
					#~ >> results-facedetector-$resolution
		#~ done
	#~ done
#~ done 

# TODO: eyepair detection plots
#~ for resolution in $resolutions
#~ do
	#~ > results-eyepairdetector-$resolution
	#~ for sf in $eyepair_cascade_sfs
	#~ do
		#~ for mn in $eyepair_cascade_mns
		#~ do
			#~ cat results_eyepairdetector-$resolution-* | \
			#~ awk -vsf="$sf" -vmn="$mn" \
			#~ '{if($4 == sf && $5 == mn) \
				#~ {groundtruth_faces+=$2; \
					#~ correct_faces+=$6; incorrect_faces+=$7; \
					#~ fps+=$31; num+=1;}} \
				#~ END {print sf, mn, \
					#~ groundtruth_faces, correct_faces+incorrect_faces, \
					#~ correct_faces, incorrect_faces, fps/num}' \
					#~ >> results-eyepairdetector-$resolution
		#~ done
	#~ done
#~ done 

# TODO: face recognition plots
for resolution in $resolutions
do
	for method in $facerec_methods
	do
		> results_recognizer-$resolution-$method
		for ep in $eyes_positions
		do
			for ew in $eyes_widths
			do
				cat results_recognizer-$resolution-* | \
				awk -vep="$ep" -vew="$ew" -vmethod="$method" \
				'{if($14 == method && $15 == ep && $16 == ew) \
					{sum1+=$17; sum2+=($17+$18);}} \
					END {print ep, ew, sum1/sum2}'
			done
		done >> results_recognizer-$resolution-$method
		#~ ./utils/plots.py $resolution-$method "eyepos" "eyew" "eff [%]"
	done
done
