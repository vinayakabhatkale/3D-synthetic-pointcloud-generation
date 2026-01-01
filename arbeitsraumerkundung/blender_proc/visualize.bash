#!/bin/bash

FRAME=$1
if [ -z "${FRAME}" ]; then
  FRAME=0
fi

blenderproc vis hdf5 outputs/$FRAME.hdf5 --depth_max 4
