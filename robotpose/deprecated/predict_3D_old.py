from deepposekit.models import load_model
from deepposekit.io import VideoReader
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyrealsense2 as rs
from robotpose.utils import *
import pickle
from robotpose import paths as p


# Compile PLY data if not already complied
if not os.path.isfile(p.ply_data):
    parsePLYs()

# Read ply data
ply_data = readBinToArrs(p.ply_data)

# Read in Actual angles from JSONs to compare predicted angles to
S_angles = readLinkXData(0)
L_angles = readLinkXData(1)
U_angles = readLinkXData(2)
B_angles = readLinkXData(4)

# Load model, make predictions
model = load_model(p.model_mult)
reader = VideoReader(p.VIDEO)
predictions = model.predict(reader)
pred_dict = predToDictList(predictions)
pred_dict_xyz = predToXYZdict(pred_dict, ply_data)

# Load video capture and make output
cap = cv2.VideoCapture(p.VIDEO)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(p.VIDEO.replace(".avi","_overlay.avi"),fourcc, 12.5, (640*2,480))

# Init predicted angle lists
S_pred = []
L_pred = []
U_pred = []
B_pred = []

ret, image = cap.read()

frame_height = image.shape[0]
frame_width = image.shape[1]

i = 0
while ret:
    over = np.zeros((480,640,3),dtype=np.uint8)
    coord_dict = pred_dict_xyz[i]
    
    # Predict S using the B joint position in reference to the R and U joints
    S_pred_ang_BR = XYangle(coord_dict['B'][0]-coord_dict['R'][0], coord_dict['B'][2]-coord_dict['R'][2],(1,6))
    S_pred_ang_LU = XYangle(coord_dict['B'][0]-coord_dict['U'][0], coord_dict['B'][2]-coord_dict['U'][2],(-1,5))

    # Take average of both angles (one tends to overshoot, one tends to undershoot)
    # Likely will need to be changed when we get actual S angles
    S_pred_ang = np.mean([S_pred_ang_BR,S_pred_ang_LU])


    # Predict L
    L_pred_ang = XYZangle(coord_dict['L'], coord_dict['U'])

    BR_ang = XYZangle(coord_dict['B'], coord_dict['R'],(.5,-10))

    # Predict U
    U_pred_ang = L_pred_ang - BR_ang
    # Predict B
    B_pred_ang = XYZangle(coord_dict['T'], coord_dict['B'],(1,-10)) - BR_ang

    # Append to lists
    S_pred.append(S_pred_ang)
    L_pred.append(L_pred_ang)
    U_pred.append(U_pred_ang)
    B_pred.append(B_pred_ang)

    # Put depth info on overlay
    vizDepth(ply_data[i], over)
    #Visualize lines
    viz(image, over, predictions[i])

    dual = np.zeros((frame_height,frame_width*2,3),dtype=np.uint8)
    dual[:,0:frame_width] = image
    dual[:,frame_width:frame_width*2] = over

    out.write(dual)
    cv2.imshow("test",dual)
    cv2.waitKey(1)
    i+=1
    ret, image = cap.read()

cv2.destroyAllWindows()
cap.release()
out.release()


"""
Plotting Angles
"""

# Convert everything from radians to degrees
S_act = L_act = U_act = B_act = None
for a, b in zip(["S_act","L_act","U_act","B_act","S_pred","L_pred","U_pred","B_pred"],["S_angles","L_angles","U_angles","B_angles","S_pred","L_pred","U_pred","B_pred"]):
    globals()[a] = np.degrees(globals()[b])


# Make Subplots
fig, axs = plt.subplots(4,3)

# Plot Raw Angles
for idx, act, pred, label in zip(range(4),["S_act","L_act","U_act","B_act"],["S_pred","L_pred","U_pred","B_pred"],["S","L","U","B"]):
    axs[idx,0].set_title(f'Raw {label} Angle')
    axs[idx,0].plot(globals()[act])
    axs[idx,0].plot(globals()[pred])


# Offset Angles
S_offset = np.add(np.mean(np.subtract(S_act,S_pred)),S_pred)
L_offset = np.add(np.mean(np.subtract(L_act,L_pred)),L_pred)
U_offset = np.add(np.mean(np.subtract(U_act,U_pred)),U_pred)
B_offset = np.add(np.mean(np.subtract(B_act,B_pred)),B_pred)

for idx, act, offset, label in zip(range(4),["S_act","L_act","U_act","B_act"],["S_offset","L_offset","U_offset","B_offset"],["S","L","U","B"]):
    axs[idx,1].set_title(f'Offset {label} Angle')
    axs[idx,1].plot(globals()[act])
    axs[idx,1].plot(globals()[offset])



#Residuals
S_err = np.subtract(S_offset, S_act)
L_err = np.subtract(L_offset, L_act)
U_err = np.subtract(U_offset, U_act)
B_err = np.subtract(B_offset, B_act)

zeros_err = np.zeros(L_act.shape)

for idx, err, label in zip(range(4),["S_err","L_err","U_err","B_err"],["S","L","U","B"]):
    axs[idx,2].set_title(f'Angle {label} Error')
    axs[idx,2].plot(zeros_err)
    axs[idx,2].plot(globals()[err])


# Determine average errors
avg_S_err = np.mean(np.abs(S_err))
avg_L_err = np.mean(np.abs(L_err))
avg_U_err = np.mean(np.abs(U_err))
avg_B_err = np.mean(np.abs(B_err))
S_err_std = np.std(np.abs(S_err))
L_err_std = np.std(np.abs(L_err))
U_err_std = np.std(np.abs(U_err))
B_err_std = np.std(np.abs(B_err))

print("Average error in degrees (after an offset is applied):")
print(f"\tS: {avg_S_err}\n\tL: {avg_L_err}\n\tU: {avg_U_err}\n\tB: {avg_B_err}")
print("Stdev of error in degrees (after an offset is applied):")
print(f"\tS: {S_err_std}\n\tL: {L_err_std}\n\tU: {U_err_std}\n\tB: {B_err_std}")

plt.show()