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
cropped_faces_path=$output_path"cropped_faces/"

log_file=$output_path"logfile"
facedetector_results_file=$output_path"results_facedetector"
eyepairdetector_results_file=$output_path"results_eyepairdetector"
trainer_results_file=$output_path"results_trainer"
recognizer_results_file=$output_path"results_recognizer"

face_cascade_sfs="1.1 1.2 1.5 2.0 3.0"
face_cascade_mns="3 4 5 6"
eyepair_cascade_sfs="1.01 1.05 1.1 1.2"
eyepair_cascade_mns="3 4 5 6"
eyes_positions="0.2 0.25 0.3 0.35"
eyes_widths="0.7 0.8 0.9 0.95"

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
facerec_groups="1_1 1_2 2_1 2_2"

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
	print_log ENDLOG FINISH LOG $log_file
	echo -e | tee -a $log_file
	exit $1
}

# test last command result
# $1 - name of function in which tested call occured 
test_last_call ()
{
	rc=$?
	if [ $rc -ne 0 ]
	then
		print_log ERROR FAILED $1 $log_file
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
	print_log INFO BEGIN $FUNCNAME $log_file
	for resolution in $sequences_resolutions
	do
		# only these sequence need to be resized
		for i in $facerec_dev_sequences $facerec_eval_sequences
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
				print_log INFO SKIPPED $output_path$resolution/$i $log_file
				continue
			fi
		done
	done
	print_log INFO FINISH $FUNCNAME $log_file
}

# perform tests of face detector (without eyepair detector yet) 
# and save results in file
test_face_detector ()
{
	print_log INFO BEGIN $FUNCNAME $log_file
	for sequence in $facerec_dev_sequences2
	do
		print_log INFO "BENCHMARK-FACEDETECT-800x600-$sequence" \
			$FUNCNAME $log_file
		for sf in $face_cascade_sfs
		do
			for mn in $face_cascade_mns
			do
				# call it with fast values for eyepair and face recognition,
				# because these results are ignored here
				mshBenchmark.py \
					$database_path$sequence \
					$groundtruths_path$(basename $sequence)".xml" \
					$face_cascade_path $sf $mn \
					$eyepair_cascade_path 10.0 1 \
					"none" "none" 0.5 1.0 \
					-minf 16 -maxf 256 \
					>> $facedetector_results_file"-800x600-"$(basename $sequence)
				test_last_call $FUNCNAME
			done
		done
	done
	# perform tests for prescaled lower resolution sequences
	for resolution in $sequences_resolutions
	do
		for sequence in $facerec_dev_sequences
		do
			print_log INFO "BENCHMARK-FACEDETECT-$resolution-$sequence" \
				$FUNCNAME $log_file
			for sf in $face_cascade_sfs
			do
				for mn in $face_cascade_mns
				do
					mshBenchmark.py \
						$output_path$resolution/$sequence \
						$groundtruths_path$(basename $sequence)".xml" \
						$face_cascade_path $sf $mn \
						$eyepair_cascade_path 10.0 1 \
						"none" "none" 0.5 1.0 \
						-r $resolution -minf 16 -maxf 256 \
						>> $facedetector_results_file-$resolution-$(basename $sequence)
					test_last_call $FUNCNAME
				done
			done
		done
	done
	print_log INFO FINISH $FUNCNAME $log_file
}

# perform tests of eyepair detector with fixed parameters of 
# face detector (accurate) and save results in file
# $1, $2 - scale_factor and min_neighbors for face detector used in this test
test_eyepair_detector ()
{
	print_log INFO BEGIN $FUNCNAME $log_file
	for sequence in $facerec_dev_sequences
	do
		print_log INFO "BENCHMARK-EYEPAIRDETECT-800x600-$sequence" \
			$FUNCNAME $log_file
		for sf in $eyepair_cascade_sfs
		do
			for mn in $eyepair_cascade_mns
			do
				mshBenchmark.py \
					$database_path$sequence \
					$groundtruths_path$(basename $sequence)".xml" \
					$face_cascade_path $1 $2 \
					$eyepair_cascade_path $sf $mn \
					"none" "none" 0.5 1.0 -minf 36 -maxf 182 \
					>> $eyepairdetector_results_file"-800x600-"$(basename $sequence)
				test_last_call $FUNCNAME
			done
		done
	done
	print_log INFO FINISH $FUNCNAME $log_file
}

# crop faces using scale_factors and min_neighbors parameters
# for accurate face and eyepair detection and 
# defined set of cropping parameters
# $1, $2 - parameters for face cascade
# $3, $4 - parameters for eyepair cascade
crop_faces ()
{
	print_log INFO BEGIN $FUNCNAME $log_file
	for eyes_pos in $eyes_positions
	do
		for eyes_width in $eyes_widths
		do		
			for group in {1..2}
			do
				sequences_array_name="facerec_dev_sequences${group}"
				for sequence in ${!sequences_array_name}
				do
					mshCropper.py \
						$database_path$sequence \
						$cropped_faces_path"G"$group-$eyes_pos-$eyes_width/ \
						$groundtruths_path$(basename $sequence)".xml" \
						$face_cascade_path $1 $2 $eyepair_cascade_path $3 $4 \
						-p $eyes_pos -w $eyes_width
					test_last_call $FUNCNAME
				done
			done
		done
	done
	print_log INFO FINISH $FUNCNAME $log_file
}

# train face recognition models from sets of cropped faces
train_facerec_models ()
{
	print_log INFO BEGIN $FUNCNAME $log_file
	for eyes_pos in $eyes_positions
	do
		for eyes_width in $eyes_widths
		do
			for method in $facerec_methods
			do
				echo "mshTrainer.py" \
					"$cropped_faces_path"G1"-$eyes_pos-$eyes_width/" \
					"$method -q >> $trainer_results_file"
				echo "mshTrainer.py" \
					"$cropped_faces_path"G2"-$eyes_pos-$eyes_width/" \
					"$method -q >> $trainer_results_file"
			done
		done
	done | parallel -j4
	test_last_call $FUNCNAME
	print_log INFO FINISH $FUNCNAME $log_file
}

# test face recognizer against all trained models, using accurate 
# eyepair detector parameters and selected face detector parameters
# (fast but enough accurate)
# $1, $2 - parameters for face cascade
# $3, $4 - parameters for eyepair cascade
# TODO: remove these ugly long lines...
test_face_recognizer ()
{
	print_log INFO BEGIN $FUNCNAME $log_file
	for eyes_pos in $eyes_positions
	do
		for eyes_width in $eyes_widths
		do
			print_log INFO \
				"TEST800x600-eyes_pos:$eyes_pos eyes_w-$eyes_width" \
				$FUNCNAME $log_file
			for group in {1..2}
			do
				sequences_array_name="facerec_eval_sequences${group}"
				for sequence in ${!sequences_array_name}
				do
					for method in $facerec_methods
					do
						mshBenchmark.py \
							$database_path$sequence \
							$groundtruths_path$(basename $sequence)".xml" \
							$face_cascade_path $1 $2 $eyepair_cascade_path $3 $4 \
							$method \
							$cropped_faces_path"G"$group-$eyes_pos-$eyes_width/"G"$group-$eyes_pos-$eyes_width-$method".xml" \
							$eyes_pos $eyes_width \
							>> $recognizer_results_file"-800x600-"$(basename $sequence)
						test_last_call $FUNCNAME
					done
				done
			done
		done
	done
	for resolution in $sequences_resolutions
	do
		for eyes_pos in $eyes_positions
		do
			for eyes_width in $eyes_widths
			do
				print_log INFO \
					"TEST$resolution-eyes_pos:$eyes_pos eyes_w-$eyes_width" \
					$FUNCNAME $log_file
				for group in {1..2}
				do
					sequences_array_name="facerec_eval_sequences${group}"
					for sequence in ${!sequences_array_name}
					do
						for method in $facerec_methods
						do
							mshBenchmark.py \
								$output_path$resolution/$sequence \
								$groundtruths_path$(basename $sequence)".xml" \
								$face_cascade_path $1 $2 $eyepair_cascade_path $3 $4 \
								$method \
								$cropped_faces_path"G"$group-$eyes_pos-$eyes_width/"G"$group-$eyes_pos-$eyes_width-$method".xml" \
								$eyes_pos $eyes_width -r $resolution \
								>> $recognizer_results_file"-$resolution-"$(basename $sequence)
							test_last_call $FUNCNAME
						done
					done
				done
			done
		done
	done
	print_log INFO FINISH $FUNCNAME $log_file
}

print_log STARTLOG BEGIN LOG $log_file

case "$#" in
	$n_first_phase_args)
		make_dirs $output_path
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
		test_face_recognizer \
			$opt_face_cascade_sf $opt_face_cascade_nm \
			$eyepair_cascade_sf $eyepair_cascade_nm
		;;
	*)
		echo "Usage: $(basename $0) $script_params"
		atexit $E_WRONG_ARGS
		;;
esac

atexit 0
