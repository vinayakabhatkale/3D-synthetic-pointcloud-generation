#!/bin/bash

blender --background --python /home/${USER}/arbeitsraumerkundung/pytorch-blender/scripts/install_btb.py
python3 -m pip install -r /home/${USER}/arbeitsraumerkundung/pytorch-blender/pkg_blender/requirements.txt

pip3 install -e /home/${USER}/arbeitsraumerkundung/pytorch-blender/pkg_pytorch
