#%%
import numpy as np
import pickle
from bokeh.models import ColumnDataSource

#%%
eye_profiles = np.load("./data/eye_profiles.npy")

ex = eye_profiles[:, 1, :]
ey = eye_profiles[:, 0, :]
EYE_ROTATION = np.linspace(-40, 40, 81)
EYE_ROTATION_RAD = np.deg2rad(EYE_ROTATION)

#%%
eye_profiles = np.zeros([2, EYE_ROTATION_RAD.size, 5, 50], dtype=np.double)
for rIdx, rot in enumerate(EYE_ROTATION_RAD):
    cs = np.cos(rot)
    ss = np.sin(rot)
    eye_profiles[0, rIdx, :, :] = ex * cs - ey * ss
    eye_profiles[1, rIdx, :, :] =  ex * ss + ey * cs

#%%
eye_profile_data = {
    "EyeRotation" :  EYE_ROTATION,
    "Profile" : eye_profiles
}

outfile = "./data/eye_profile.pk"
with open(outfile, 'wb') as handle:
    pickle.dump(
        eye_profile_data,
        handle, protocol=pickle.HIGHEST_PROTOCOL
    )
