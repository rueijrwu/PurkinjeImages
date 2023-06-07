#%%
from optialmodel import PurkinjeModel
#from utility import save_rays, save_bokeh_rays_from_raw
import numpy as np
import utility

#%% initialize
rotationSurfaceIdx = 3
p4RayTracer = PurkinjeModel("./data/LENS.zos", rotationSurfaceIdx)
if not p4RayTracer.isFileOpen:
    raise FileNotFoundError("File not found.")
p4RayTracer.setEyeRotationX(0)

MAX_EYE_ROTATION = 10.0
MAX_SOURCE_ANGLE = 5
SURFACES = np.array(
    [0, 4, 5, 6, 7, 8, 11, 12, 13, 18, 20, 21], dtype=int)

ROTATIONS = np.linspace(
    -MAX_EYE_ROTATION, MAX_EYE_ROTATION, 
    num=2*int(MAX_EYE_ROTATION)+1,
    dtype=np.double)
SOURCE_ANGLE = np.linspace(
    -MAX_SOURCE_ANGLE, MAX_SOURCE_ANGLE, 
    num=2*int(MAX_SOURCE_ANGLE)+1,
    dtype=np.double)

#%% do ray tracing
rays = np.zeros(
    [SOURCE_ANGLE.size, ROTATIONS.size, SURFACES.size, 3, 6], 
    dtype=np.double)
for aIdx, sourceAngle in enumerate(SOURCE_ANGLE):
    for rIdx, rot in enumerate(ROTATIONS):
        p4RayTracer.setEyeRotationX(rot)
        rays[aIdx, rIdx, ...] = \
            p4RayTracer.trace(sourceAngle, surfaces=SURFACES)
ROTATIONS = -ROTATIONS        
#%% create data
out_data = {
    "RAYS" : rays,
    "DIM" : {
        "Axis" : {
            "SourceAngle" : SOURCE_ANGLE,
            "EyeRotation" : ROTATIONS
        },
        "Info" : {
            "Code" : "SA{:d}ER{:d}",
            "Shape" : [SOURCE_ANGLE.size, ROTATIONS.size]
        }
    },
    "INFO" : {
        "SurfaceIndex" : SURFACES
    }
}

#%% save file
utility.save_rays('rays.pk', out_data)
