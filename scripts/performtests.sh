#!/bin/bash

E_WRONG_ARGS=85

# add parent directory (with msh apps) to PATH
PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd ):$PATH

n_first_phase_args=2
n_second_phase_args=4
n_third_phase_args=6
n_fourth_phase_args=8
required_params="database_path output_path"
optional_params="[face_cascade_sf face_cascade_nm \
[eyepair_cascade_sf eyepair_cascade_nm \
[opt_face_cascade_sf opt_face_cascade_nm]]]"
script_params="$required_params $optional_params"

database_path=$1
output_path=$2
face_cascade_sf=$3
face_cascade_nm=$4
eyepair_cascade_sf=$5
eyepair_cascade_nm=$6
opt_face_cascade_sf=$7
opt_face_cascade_nm=$8
face_cascade_path=\
"/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
eyepair_cascade_path=\
"/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_big.xml"
groundtruths_path=$database_path"groundtruth/"
cropped_faces_path=$output_path"cropped_faces"

log_path=$output_path"logfile"
detector_results_path=$output_path"results_detector"
trainer_results_path=$output_path"results_trainer"
recognizer_results_path=$output_path"results_recognizer"

facedetect_dev_sequences="P1E_S1_C1"
face_cascade_sfs="1.1 1.2 1.5 2.0 3.0 5.0"
face_cascade_mns="2 3 4 5 6"
eyepair_cascade_sfs="1.01 1.1 1.2 1.4 1.8 2.0"
eyepair_cascade_mns="2 3 4 5 6"
eyes_positions="0.2 0.25 0.3 0.35"
eyes_widths="0.8 0.85 0.9 0.95"

sequences_resolutions="640x480 320x240"

facerec_dev_sequences1_1="P1E_S1_C1 P1E_S2_C2"
facerec_dev_sequences1_2="P1L_S1_C1 P1L_S2_C2"
facerec_dev_sequences2_1="P2E_S2_C2/P2E_S2_C2.1 P2E_S1_C3/P2E_S1_C3.1"
facerec_dev_sequences2_2="P2L_S2_C2/P2L_S2_C2.1 P2L_S1_C1/P2L_S1_C1.1"
facerec_dev_sequences1="$facerec_dev_sequences1_1 $facerec_dev_sequences1_2"
facerec_dev_sequences2="$facerec_dev_sequences2_1 $facerec_dev_sequences2_2"
facerec_dev_sequences="$facerec_dev_sequences1 $facerec_dev_sequences2"
facerec_eval_sequences1_1="P1E_S3_C3 P1E_S4_C1"
facerec_eval_sequences1_2="P1L_S3_C3 P1L_S4_C1"
facerec_eval_sequences2_1="P2E_S4_C2/P2E_S4_C2.1 P2E_S3_C1/P2E_S3_C1.1"
facerec_eval_sequences2_2="P2L_S4_C2/P2L_S4_C2.1 P2L_S3_C3/P2L_S3_C3.1"
facerec_eval_sequences1="$facerec_eval_sequences1_1 $facerec_eval_sequences1_2"
facerec_eval_sequences2="$facerec_eval_sequences2_1 $facerec_eval_sequences2_2"
facerec_eval_sequences="$facerec_eval_sequences1 $facerec_eval_sequences2"

facerec_methods="eigenfaces fisherfaces lbph"

# function for print logs
# $1 - message type
# $2, $3 - informations like action and function name
# $4 - destination file
print_log ()
{
	echo ["$1"] $(date +%Y_%m_%d-%H_%M_%S) " ---$2--- " "$3" | tee -a $4
}

# print information about finishing and exit
atexit ()
{
	print_log ENDLOG FINISH LOG $log_path
	echo -e "\n" | tee -a $log_path
	exit $1
}

# test last command result
# $1 - name of function in which tested call occured 
test_last_call ()
{
	rc=$?
	if [ $rc -ne 0 ]
	then
		print_log ERROR FAILED $1 $log_path
		atexit $rc
	fi
}


# function for creating directories (including necessary parent directories)
make_dirs ()
{
	if [ ! -d "$1" ]
	then
		mkdir -p $1
		if [ $? -ne 0 ]
		then
			atexit 1
		fi
	fi	
}

# perform resize of frames in test sequences and save them in output_path
resize_frames ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	for resolution in $sequences_resolutions
	do
		# only these sequence need to be resized
		for i in facedetect_dev_sequences $facerec_eval_sequences
		do
			if [ ! -d $output_path$resolution/$i ]
			then
				make_dirs $output_path$resolution/$i
				for file in $database_path$i/*.jpg
				do
					convert \
						-resize $resolution \
						$file \
						$output_path$resolution/$i"/"$(basename $file)
					test_last_call $FUNCNAME
				done
			else
				print_log INFO SKIPPED $output_path$resolution/$i $log_path
				continue
			fi
		done
	done
	print_log INFO FINISH $FUNCNAME $log_path
}

# perform tests of face detector (without eyepair detector yet) 
# and save results in file
test_face_detector ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	
	print_log INFO BENCHMARK-800x600 $FUNCNAME $detector_results_path
	for sequence in $facedetect_dev_sequences
	do
		for sf in $face_cascade_sfs
		do
			for mn in $face_cascade_mns
			do
				# call it with fast values for eyepair and face recognition,
				# because these results are ignored here
				mshBenchmark.py \
					$database_path$sequence \
					$groundtruths_path$sequence".xml" \
					$face_cascade_path $sf $mn \
					$eyepair_cascade_path 10.0 1 \
					"none" "none" 0.5 1.0 >> $detector_results_path
				test_last_call $FUNCNAME
			done
		done
	done
	
	# perform tests for prescaled lower resolution sequences
	for resolution in $sequences_resolutions
	do
		print_log INFO "BENCHMARK-$resolution" $FUNCNAME $detector_results_path
		for sequence in $facedetect_dev_sequences
		do
			for sf in $face_cascade_sfs
			do
				for mn in $face_cascade_mns
				do
					mshBenchmark.py \
						$output_path$resolution/$sequence \
						$groundtruths_path$sequence".xml" \
						$face_cascade_path $sf $mn \
						$eyepair_cascade_path 10.0 1 \
						"none" "none" 0.5 1.0 >> $detector_results_path
					test_last_call $FUNCNAME
				done
			done
		done
	done
	
	print_log INFO FINISH $FUNCNAME $log_path
}

# perform tests of eyepair detector with fixed parameters of 
# face detector (accurate) and save results in file
# $1, $2 - scale_factor and min_neighbors for face detector used in this test
test_eyepair_detector ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	print_log INFO BENCHMARK $FUNCNAME $detector_results_path
	for sequence in $facedetect_dev_sequences
	do
		for sf in $eyepair_cascade_sfs
		do
			for mn in $eyepair_cascade_mns
			do
				mshBenchmark.py \
					$database_path$sequence \
					$groundtruths_path$sequence".xml" \
					$face_cascade_path $1 $2 \
					$eyepair_cascade_path $sf $mn \
					"none" "none" 0.5 1.0 >> $detector_results_path
				test_last_call $FUNCNAME
			done
		done
	done
	print_log INFO FINISH $FUNCNAME $log_path
}

# crop faces using scale_factors and min_neighbors parameters
# for accurate face and eyepair detection and 
# defined set of cropping parameters
crop_faces ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	for sequence in $facerec_dev_sequences1_1
	do
		echo $database_path$sequence $cropped_faces_path/"G1_1/"
	done
	for sequence in $facerec_dev_sequences1_2
	do
		echo $database_path$sequence $cropped_faces_path/"G1_2/"
	done
	for sequence in $facerec_dev_sequences2_1
	do
		echo $database_path$sequence $cropped_faces_path/"G2_1/"
	done
	for sequence in $facerec_dev_sequences2_2
	do
		echo $database_path$sequence $cropped_faces_path/"G2_2/"
	done
	print_log INFO FINISH $FUNCNAME $log_path
}

# train face recognition models from sets of cropped faces
train_facerec_models ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	echo $cropped_faces_path/"G1_1/"
	echo $cropped_faces_path/"G1_2/"
	echo $cropped_faces_path/"G2_1/"
	echo $cropped_faces_path/"G2_2/"
	print_log INFO FINISH $FUNCNAME $log_path
}

# test face recognizer against all trained models, using accurate 
# eyepair detector parameters and selected face detector parameters
# (fast but enough accurate)
test_face_recognizer ()
{
	print_log INFO BEGIN $FUNCNAME $log_path
	for method in $facerec_methods
	do
		for sequence in $facerec_eval_sequences
		do
			echo $method $database_path$sequence"/"
		done
	done
	print_log INFO FINISH $FUNCNAME $log_path
}


# here comes "main" function
make_dirs $output_path
print_log STARTLOG BEGIN LOG $log_path

case "$#" in
	$n_first_phase_args)
		resize_frames
		test_face_detector
		;;
	$n_second_phase_args)
		test_eyepair_detector $face_cascade_sf $face_cascade_nm
		;;
	$n_third_phase_args)
		crop_faces \
			$face_cascade_sf $face_cascade_nm \
			$eyepair_cascade_sf $eyepair_cascade_nm
		train_facerec_models
		;;
	$n_fourth_phase_args)
		test_face_recognizer
		;;
	*)
		echo "Usage: $(basename $0) $script_params"
		atexit $E_WRONG_ARGS
		;;
esac

atexit 0
