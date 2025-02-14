# Software License Agreement (Apache 2.0 License)
#
# Copyright (c) 2021, The Ohio State University
# Center for Design and Manufacturing Excellence (CDME)
# The Artificially Intelligent Manufacturing Systems Lab (AIMS)
# All rights reserved.
#
# Author: Adam Exley

import os
from deepposekit.models import load_model
from deepposekit.io import VideoReader
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyrealsense2 as rs
from robotpose.utils import *
from robotpose import paths as p
from robotpose import Dataset

setMemoryGrowth()

# Load dataset
ds = Dataset('set7','B')

# Read in Actual angles from JSONs to compare predicted angles to
S_angles = ds.angles[:,0]
L_angles = ds.angles[:,1]
U_angles = ds.angles[:,2]
B_angles = ds.angles[:,4]

# Load model, make predictions
model = load_model(os.path.join(os.getcwd(),r'models\set10__B__CutMobilenet.h5'))
reader = VideoReader(ds.vid_path)
predictions = model.predict(reader)


# Load video capture and make output
cap = ds.vid
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(p.VIDEO.replace(".avi","_overlay.avi"),fourcc, 12.5, (ds.resolution[1]*2,ds.resolution[0]))

ret, image = cap.read()

frame_height = image.shape[0]
frame_width = image.shape[1]

i = 0
while ret:
    over = np.zeros((ds.resolution[0],ds.resolution[1],3),dtype=np.uint8)

    # Put depth info on overlay
    vizDepth_new(ds.ply[i], over)
    #vizDepth(ds.ply[i], over, ds.x_crop[i])
    #Visualize lines
    viz(image, over, predictions[i])

    dual = np.zeros((frame_height,frame_width*2,3),dtype=np.uint8)
    dual[:,0:frame_width] = image
    dual[:,frame_width:frame_width*2] = over

    out.write(dual)
    cv2.imshow("Output",dual)
    cv2.waitKey(1)
    i+=1
    ret, image = cap.read()

cv2.destroyAllWindows()
cap.release()
out.release()

