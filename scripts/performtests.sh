#!/bin/bash

E_WRONG_ARGS=85

n_first_phase_args=2
n_second_phase_args=4
n_third_phase_args=6
n_fourth_phase_args=8
required_parameters="database_path output_path"
optional_parameters="[face_cascade_sf face_cascade_nm \
[eyepair_cascade_sf eyepair_cascade_nm \
[opt_face_cascade_sf opt_face_cascade_nm]]]"
script_parameters="$required_parameters $optional_parameters"

database_path=$1
output_path=$2
face_cascade_path=\
"/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
eyepair_cascade_path=\
"/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_big.xml"
log_path=$output_path"logfile"

facedetect_development_sequences="P1E_S1_C1 P1E_S2_C2 P1E_S3_C3 P1E_S4_C1"
face_cascade_sfs="1.1 1.2 1.5 2.0 3.0 5.0"
face_cascade_mns="2 3 4 5 6"
eyepair_cascade_sfs="1.01 1.1 1.2 1.4 1.8 2.0"
eyepair_cascade_mns="2 3 4 5 6"
eyes_positions="0.2 0.25 0.3 0.35"
eyes_widths="0.8 0.85 0.9 0.95"

facerec_development_sequences1="P1E_S1_C1 P1E_S2_C2	P1L_S1_C1 P1L_S2_C2"
facerec_development_sequences2="P2E_S2_C2/P2E_S2_C2.1 P2E_S1_C3/P2E_S1_C3.1 \
P2L_S2_C2/P2L_S2_C2.1 P2L_S1_C1/P2L_S1_C1.1"
facerec_evaluation_sequences1="P1E_S3_C3 P1E_S4_C1 P1L_S3_C3 P1L_S4_C1"
facerec_evaluation_sequences2="P2E_S4_C2/P2E_S4_C2.1 P2E_S3_C1/P2E_S3_C1.1 \
P2L_S4_C2/P2L_S4_C2.1 P2L_S3_C3/P2L_S3_C3.1"
facerec_methods="eigenfaces fisherfaces lbph"


# perform tests of face detector (without eyepair detector yet) 
# and save results in file
test_face_detector ()
{
	echo "First phase"
}

# perform tests of eyepair detector with fixed parameters of 
# face detector (accurate) and save results in file
test_eyepair_detector ()
{
	echo "Second phase"
}

# crop faces using scale_factors and min_neighbors parameters
# for accurate face and eyepair detection and 
# defined set of cropping parameters
crop_faces ()
{
	echo "Crop faces"
	for i in $facerec_development_sequences1 $facerec_development_sequences2
	do
		echo $database_path$i
	done
}

# train face recognition models from sets of cropped faces
train_facerec_models ()
{
	echo "Train face recognition models"
	for i in $facerec_development_sequences1 $facerec_development_sequences2
	do
		echo $output_path$i
	done
}

# test face recognizer against all trained models, using accurate 
# eyepair detector parameters and selected face detector parameters
# (fast but enough accurate)
test_face_recognizer ()
{
}


case "$#" in
	$n_first_phase_args)
		test_face_detector
		;;
	$n_second_phase_args)
		test_eyepair_detector
		;;
	$n_third_phase_args)
		crop_faces
		train_facerec_models
		;;
	$n_fourth_phase_args)
		test_face_recognizer
		;;
	*)
		echo "Usage: `basename $0` $script_parameters"
		exit $E_WRONG_ARGS
		;;
esac

exit
