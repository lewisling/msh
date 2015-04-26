#!/bin/bash

E_WRONG_ARGS=85

# add parent directory (with msh apps) to PATH
PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd ):$PATH

face_cascade_sfs="1.1 1.2 1.5 2.0 3.0"
face_cascade_mns="3 4 5 6"
eyepair_cascade_sfs="1.01 1.05 1.1 1.2"
eyepair_cascade_mns="3 4 5 6"
eyes_positions="0.2 0.25 0.3 0.35"
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

resolutions="800x600"

# TODO: face detection plots
for resolution in $resolutions
do
	for sf in $face_cascade_sfs
	do
		for mn in $face_cascade_mns
		do
			cat $tests_path/results_facedetector-$resolution-* | \
			awk -vsf="$sf" -vmn="$mn" \
			'{if($4 == sf && $5 == mn) \
				{groundtruth_faces+=$2; correct_faces+=$6;}} \
				END {printf "detected_faces %s|%s %s\n", 
					sf, mn, \
					(correct_faces/groundtruth_faces)*100}'
			cat $tests_path/results_facedetector-$resolution-* | \
			awk -vsf="$sf" -vmn="$mn" \
			'{if($4 == sf && $5 == mn) \
				{correct_faces+=$6; incorrect_faces+=$7;}} \
				END {printf "incorrect_detections %s|%s %s\n", 
					sf, mn, \
					(incorrect_faces/(correct_faces+incorrect_faces))*100}'
		done
	done | ./utils/plots2d.py \
	"" "scale factor|min neighbors" \
	"detected faces | incorrect detections [%]" \
	-r 0.1 -d -c "gr"
done 
echo "--------"
# detection speed (fps), mean for each scale factor
for resolution in $resolutions
do
	for sf in $face_cascade_sfs
	do
		# min fps
		cat $tests_path/results_facedetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($4 == sf) \
			{fps+=$29; num+=1;}} \
			END {printf "min %s %s\n", sf, fps/num}'
		# max fps
		cat $tests_path/results_facedetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($4 == sf) \
			{fps+=$30; num+=1;}} \
			END {printf "max %s %s\n", sf, fps/num}'
		# avg fps
		cat $tests_path/results_facedetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($4 == sf) \
			{fps+=$31; num+=1;}} \
			END {printf "avg %s %s\n", sf, fps/num}'
	done | ./utils/plots2d.py "" "scale factor" "fps" -r 0.1 -p1r -d -lp 2
done
echo "--------"

# TODO: eyepair detection plots
for resolution in $resolutions
do
	for sf in $eyepair_cascade_sfs
	do
		for mn in $eyepair_cascade_mns
		do
			cat $tests_path/results_eyepairdetector-$resolution-* | \
			awk -vsf="$sf" -vmn="$mn" \
			'{if($9 == sf && $10 == mn) \
				{groundtruth_faces+=$2; correct_faces+=$11;}} \
				END {printf "detected_faces %s|%s %s\n", 
					sf, mn, \
					(correct_faces/groundtruth_faces)*100}'
			cat $tests_path/results_eyepairdetector-$resolution-* | \
			awk -vsf="$sf" -vmn="$mn" \
			'{if($9 == sf && $10 == mn) \
				{correct_faces+=$11; incorrect_faces+=$12;}} \
				END {printf "incorrect_detections %s|%s %s\n", 
					sf, mn, \
					(incorrect_faces/(correct_faces+incorrect_faces))*100}'
		done
	done | ./utils/plots2d.py \
	"" "scale factor|min neighbors" \
	"detected faces | incorrect detections [%]" \
	-r 0.1 -d -c "gr"
done 
echo "--------"
# detection speed (fps), mean for each scale factor
for resolution in $resolutions
do
	for sf in $eyepair_cascade_sfs
	do
		# min fps
		cat $tests_path/results_eyepairdetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($9 == sf) \
			{fps+=$29; num+=1;}} \
			END {printf "min %s %s\n", sf, fps/num}'
		# max fps
		cat $tests_path/results_eyepairdetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($9 == sf) \
			{fps+=$30; num+=1;}} \
			END {printf "max %s %s\n", sf, fps/num}'
		# avg fps
		cat $tests_path/results_eyepairdetector-$resolution-* | \
		awk -vsf="$sf" \
		'{if($9 == sf) \
			{fps+=$31; num+=1;}} \
			END {printf "avg %s %s\n", sf, fps/num}'
	done | ./utils/plots2d.py "" "scale factor" "fps" -r 0.1 -p1r -d -lp 2
done
echo "--------"

# TODO: face recognition plots
# classification efficiency
#~ for resolution in $resolutions
#~ do
	#~ for method in $facerec_methods
	#~ do
		#~ for ep in $eyes_positions
		#~ do
			#~ for ew in $eyes_widths
			#~ do
				#~ cat $tests_path/results_recognizer-$resolution-* | \
				#~ awk -vep="$ep" -vew="$ew" -vmethod="$method" \
				#~ '{if($14 == method && $15 == ep && $16 == ew) \
					#~ {sum1+=$17; sum2+=($17+$18);}} \
					#~ END {printf "%s %s,%s %s\n", \
						#~ method, ew, ep, (sum1/sum2)*100}'
			#~ done
		#~ done 
	#~ done | ./utils/plots2d.py \
	#~ "" "eyes width,eyes position" "efficiency [%]" -d -r 0.01
#~ done
#~ echo "--------"

# classification speed (fps)
#~ for resolution in $resolutions
#~ do
	#~ for method in $facerec_methods
	#~ do
		#~ # min fps
		#~ cat $tests_path/results_recognizer-$resolution-* | \
		#~ awk -vresolution="$resolution" -vmethod="$method" \
		#~ '{if($14 == method) \
			#~ {fps+=$29; num+=1;}} \
			#~ END {printf "min %s|%s %s\n", resolution, method, fps/num}'
		#~ # max fps
		#~ cat $tests_path/results_recognizer-$resolution-* | \
		#~ awk -vresolution="$resolution" -vmethod="$method" \
		#~ '{if($14 == method) \
			#~ {fps+=$30; num+=1;}} \
			#~ END {printf "max %s|%s %s\n", resolution, method, fps/num}'
		#~ # avg fps
		#~ cat $tests_path/results_recognizer-$resolution-* | \
		#~ awk -vresolution="$resolution" -vmethod="$method" \
		#~ '{if($14 == method) \
			#~ {fps+=$31; num+=1;}} \
			#~ END {printf "avg %s|%s %s\n", resolution, method, fps/num}'
	#~ done
#~ done | ./utils/plots2d.py "type" "resolution|method" "fps" -r 0.1 -lp 2 -p1r
for resolution in $resolutions
do
	for method in $facerec_methods
	do
		# min fps
		cat $tests_path/results_recognizer-$resolution-* | \
		awk -vresolution="$resolution" -vmethod="$method" \
		'{if($14 == method) \
			{fps+=$29; num+=1;}} \
			END {printf "min %s %s\n", method, fps/num}'
		# max fps
		cat $tests_path/results_recognizer-$resolution-* | \
		awk -vresolution="$resolution" -vmethod="$method" \
		'{if($14 == method) \
			{fps+=$30; num+=1;}} \
			END {printf "max %s %s\n", method, fps/num}'
		# avg fps
		cat $tests_path/results_recognizer-$resolution-* | \
		awk -vresolution="$resolution" -vmethod="$method" \
		'{if($14 == method) \
			{fps+=$31; num+=1;}} \
			END {printf "avg %s %s\n", method, fps/num}'
	done
done | ./utils/plots2d.py "type" "method" "fps" -r 0.1 -lp 2 -p1r -d
echo "--------"
