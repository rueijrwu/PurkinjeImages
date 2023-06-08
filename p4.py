#%%
from optialmodel import PurkinjeModel
import numpy as np
import plotlib
import pickle

#%% initialize
rotationSurfaceIdx = 3
p4RayTracer = PurkinjeModel("./data/p4.zos", rotationSurfaceIdx)
if not p4RayTracer.isFileOpen:
    raise FileNotFoundError("File not found.")
p4RayTracer.setEyeRotationX(0)

MAX_EYE_ROTATION = 15.0
MAX_SOURCE_ANGLE = 15.0
SURFACES = np.array(
    [1, 4, 5, 6, 7, 8, 11, 12, 13, 14, 18, 20, 21], dtype=int)


EYE_ROTATION = np.linspace(
    -MAX_EYE_ROTATION, MAX_EYE_ROTATION, 
    num=2*int(MAX_EYE_ROTATION)+1,
    dtype=np.double)
SOURCE_ANGLE = np.linspace(0.0, MAX_SOURCE_ANGLE, num=int(MAX_SOURCE_ANGLE)+1)

#%% do ray tracing
rays = np.zeros(
    [SOURCE_ANGLE.size, EYE_ROTATION.size, SURFACES.size, 3, 6], 
    dtype=np.double)
for aIdx, sourceAngle in enumerate(SOURCE_ANGLE):
    for rIdx, rot in enumerate(EYE_ROTATION):
        p4RayTracer.setEyeRotationX(rot)
        rays[aIdx, rIdx, ...] = \
            p4RayTracer.trace(sourceAngle, surfaces=SURFACES)
        
np.savez_compressed('./data/p4_S15_R15.npz', rays=rays)
#%% mirror data
MID_SOURCE = SOURCE_ANGLE.size - 1
MID_ROT = int((EYE_ROTATION.size - 1)/2)

shape = list(rays.shape)
shape[0] = int(2 * MID_SOURCE + 1)
new_rays = np.zeros(shape, dtype=rays.dtype)
new_rays[MID_SOURCE:] = rays

NEW_SOURCE_ANGLE = np.zeros([shape[0],], dtype=SOURCE_ANGLE.dtype)
for sIdx in range(MID_SOURCE+1):
    NEW_SOURCE_ANGLE[MID_SOURCE-sIdx] = -SOURCE_ANGLE[sIdx]
    for rIdx in range(EYE_ROTATION.size):
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 0] = rays[sIdx, -1-rIdx, :, :, 0]
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 1] = -rays[sIdx, -1-rIdx, :, :, 1]
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 2] = rays[sIdx, -1-rIdx, :, :, 2]
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 3] = rays[sIdx, -1-rIdx, :, :, 3]
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 4] = -rays[sIdx, -1-rIdx, :, :, 4]
        new_rays[MID_SOURCE-sIdx, rIdx, :, :, 5] = rays[sIdx, -1-rIdx, :, :, 5]
NEW_SOURCE_ANGLE[MID_SOURCE:] = SOURCE_ANGLE

#%%
axis = {
    "SourceAngle" : NEW_SOURCE_ANGLE,
    "EyeRotation" : EYE_ROTATION
}
data = plotlib.RaysData(new_rays, axis, "SA{:d}ER{:d}", "P4")
with open("./data/p4_S15_R15.pk", 'wb') as handle:
    pickle.dump(
        data,
        handle, protocol=pickle.HIGHEST_PROTOCOL
    )
#%% create data
# out_data = {
#     "RAYS" : rays,
#     "DIM" : {
#         "Axis" : {
#             "SourceAngle" : SOURCE_ANGLE,
#             "EyeRotation" : EYE_ROTATION
#         },
#         "Info" : {
#             "Code" : "SA{:d}ER{:d}",
#             "Shape" : [SOURCE_ANGLE.size, EYE_ROTATION.size]
#         }
#     },
#     "INFO" : {
#         "SurfaceIndex" : SURFACES
#     }
# }

#%% save file
# utility.save_rays('./data/rays_old.pk', out_data)
# out_data_new = utility.mirror_source(out_data)
# utility.save_rays('./data/rays.pk', out_data_new)
