Copyright (c) 2015, Albert Malina
All rights reserved.

msh (mlnSpyHole) is a program for detecting and identifying people based 
on processing video stream. Found faces are processed to determine the identity
of the detected people. Results are sent to stdout.

Project is written in Python 2, uses python-opencv for face recognition 
and identification and python-skimage for getting video stream from some 
IP cameras.

Project also includes tools for training face recognizer 
and perform various efficiency tests:

mshBenchmark - performs various efficiency tests

mshFacerecTrain - trains face recognizer. Results are written to XML.
