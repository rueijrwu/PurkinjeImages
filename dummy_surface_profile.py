#%%
from optialmodel import PurkinjeModel
import numpy as np
import pickle

rotationSurfaceIdx = 3
p4RayTracer = PurkinjeModel("./data/p4.zos", rotationSurfaceIdx)
if not p4RayTracer.isFileOpen:
    raise FileNotFoundError("File not found.")
p4RayTracer.setEyeRotationX(0)
PLANE_SURFACES = np.array([18, 19, 20, 21], dtype=int)
profiles = p4RayTracer.getDummySurfaceProfiles(PLANE_SURFACES)

#%%
data = {
    "Profiles" : profiles,
    "Surfaces" : PLANE_SURFACES,
    "Relay": [0, 2],
    "Stop" : 1,
    "Image" : 3
}

with open("./data/plane_profile.pk", 'wb') as handle:
    pickle.dump(
        data,
        handle, protocol=pickle.HIGHEST_PROTOCOL
    )
np.savez('./data/plane_profile.npz', data)

#%%
# margin = 10
# profiles = data["Profiles"]
# stop = data["Stop"]
# surfaces = data["Surfaces"]
# IDX = surfaces != stop
# xx = profiles[IDX, :, 0]
# yy = profiles[IDX, :, 1]
# yy = profiles[IDX, :, 1] + np.copysign(margin, profiles[IDX, :, 1])

# IDX = ~IDX
# sx = profiles[IDX, :, 0]
# sy = profiles[IDX, :, 1].transpose()

# #%%
# sxx = np.vstack([sx, sx])
# syy = np.hstack([sy, sy + np.copysign(margin, sy)])