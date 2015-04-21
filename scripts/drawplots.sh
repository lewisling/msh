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
		tests_path=$1
		;;
	*)
		echo "Usage: $(basename $0) tests_path"
		exit $E_WRONG_ARGS
		;;
esac

# TODO: face detection plots
#~ for resolution in $resolutions
#~ for resolution in "800x600"
#~ do
	#~ > $tests_path/results-facedetector-$resolution
	#~ for sf in $face_cascade_sfs
	#~ do
		#~ for mn in $face_cascade_mns
		#~ do
			#~ cat $tests_path/results_facedetector-$resolution-* | \
			#~ awk -vsf="$sf" -vmn="$mn" \
			#~ '{if($4 == sf && $5 == mn) \
				#~ {groundtruth_faces+=$2; \
					#~ correct_faces+=$6; incorrect_faces+=$7; \
					#~ fps+=$31; num+=1;}} \
				#~ END {print sf, mn, \
					#~ groundtruth_faces, correct_faces+incorrect_faces, \
					#~ correct_faces, incorrect_faces, fps/num}' \
					#~ >> $tests_path/results-facedetector-$resolution
		#~ done
	#~ done
	#~ # detected correctly vs present in sequence
	#~ cat $tests_path/results-facedetector-$resolution | \
	#~ awk '{print $2, $1, ($5/$3)*100}' | \
	#~ ./utils/plots2d.py \
	#~ "min neighbors" "scale factor" "correct detections [%]" -r 0.1
	#~ # detected incorrectly vs detected in general
	#~ cat $tests_path/results-facedetector-$resolution | \
	#~ awk '{print $2, $1, ($6/$4)*100}' | \
	#~ ./utils/plots2d.py \
	#~ "min neighbors" "scale factor" "errors [%]" -r 0.1
	#~ # detection speed (fps)
	#~ cat $tests_path/results-facedetector-$resolution | \
	#~ awk '{print $2, $1, $7}' | \
	#~ ./utils/plots2d.py \
	#~ "min neighbors" "scale factor" "fps" -r 0.1
#~ done 

# TODO: eyepair detection plots
#~ for resolution in $resolutions
for resolution in "800x600"
do
	> $tests_path/results-eyepairdetector-$resolution
	for sf in $eyepair_cascade_sfs
	do
		for mn in $eyepair_cascade_mns
		do
			cat $tests_path/results_eyepairdetector-$resolution-* | \
			awk -vsf="$sf" -vmn="$mn" \
			'{if($9 == sf && $10 == mn) \
				{groundtruth_faces+=$2; \
					correct_faces+=$11; incorrect_faces+=$12; \
					fps+=$31; num+=1;}} \
				END {print sf, mn, \
					groundtruth_faces, correct_faces+incorrect_faces, \
					correct_faces, incorrect_faces, fps/num}' \
					>> $tests_path/results-eyepairdetector-$resolution
		done
	done
	# detected correctly vs present in sequence
	cat $tests_path/results-eyepairdetector-$resolution | \
	awk '{print $2, $1, ($5/$3)*100}' | \
	./utils/plots2d.py \
	"min neighbors" "scale factor" "correct detections [%]" -r 0.1
	# detected incorrectly vs detected in general
	cat $tests_path/results-eyepairdetector-$resolution | \
	awk '{print $2, $1, ($6/$4)*100}' | \
	./utils/plots2d.py \
	"min neighbors" "scale factor" "errors [%]" -r 1.0
	# detection speed (fps)
	cat $tests_path/results-eyepairdetector-$resolution | \
	awk '{print $2, $1, $7}' | \
	./utils/plots2d.py \
	"min neighbors" "scale factor" "fps" -r 1.0
done 

# TODO: face recognition plots
#~ for resolution in $resolutions
#~ do
	#~ for method in $facerec_methods
	#~ do
		#~ > results_recognizer-$resolution-$method
		#~ for ep in $eyes_positions
		#~ do
			#~ for ew in $eyes_widths
			#~ do
				#~ cat results_recognizer-$resolution-* | \
				#~ awk -vep="$ep" -vew="$ew" -vmethod="$method" \
				#~ '{if($14 == method && $15 == ep && $16 == ew) \
					#~ {sum1+=$17; sum2+=($17+$18);}} \
					#~ END {print ep, ew, sum1/sum2}'
			#~ done
		#~ done >> results_recognizer-$resolution-$method
		#~ ./utils/plots.py $resolution-$method "eyepos" "eyew" "eff [%]"
	#~ done
#~ done
