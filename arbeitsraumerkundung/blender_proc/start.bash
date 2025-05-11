#!/bin/bash
# config

# python file
PATH_TO_PY=./main.py

# file of txt file with camera positions
PATH_TO_CAM_POS=/home/andi/BlenderProc/examples/resources/pirat_cam_pos

# blender file containing semantic seg info
# TODO convert to only directory so that more scenes can be loaded
# or describe certain scenes in main script
PATH_TO_BLEND_FILE=/home/andi/3dfiles/pirat.blend

# path to folder that gets stored plots
PATH_TO_OUTPUT=./outputs

blenderproc run $PATH_TO_PY $PATH_TO_CAM_POS $PATH_TO_BLEND_FILE $PATH_TO_OUTPUT
