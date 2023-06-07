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
MAX_SOURCE_ANGLE = 10
SURFACES = np.array(
    [1, 4, 5, 6, 7, 8, 11, 12, 13, 18, 20, 21], dtype=int)


EYE_ROTATION = np.linspace(
    -MAX_EYE_ROTATION, MAX_EYE_ROTATION, 
    num=2*int(MAX_EYE_ROTATION)+1,
    dtype=np.double)
SOURCE_ANGLE = np.linspace(0, MAX_SOURCE_ANGLE, num=MAX_SOURCE_ANGLE+1)

#%% do ray tracing
rays = np.zeros(
    [SOURCE_ANGLE.size, EYE_ROTATION.size, SURFACES.size, 3, 6], 
    dtype=np.double)
for aIdx, sourceAngle in enumerate(SOURCE_ANGLE):
    for rIdx, rot in enumerate(EYE_ROTATION):
        p4RayTracer.setEyeRotationX(rot)
        rays[aIdx, rIdx, ...] = \
            p4RayTracer.trace(sourceAngle, surfaces=SURFACES)
      
#%% create data
out_data = {
    "RAYS" : rays,
    "DIM" : {
        "Axis" : {
            "SourceAngle" : SOURCE_ANGLE,
            "EyeRotation" : EYE_ROTATION
        },
        "Info" : {
            "Code" : "SA{:d}ER{:d}",
            "Shape" : [SOURCE_ANGLE.size, EYE_ROTATION.size]
        }
    },
    "INFO" : {
        "SurfaceIndex" : SURFACES
    }
}

#%% save file
utility.save_rays('./data/rays_old.pk', out_data)
out_data_new = utility.mirror_source(out_data)
utility.save_rays('./data/rays.pk', out_data_new)
