#%%
from plotlib import RaysData
rays_data = RaysData.from_file("./data/rays.pk", is_dict=True)
rays_data.rays[10, 0, -1, 0, 1]



# #%%
# import numpy as np
# from utility import read_rays, save_rays, mirror_source
# rays_data = read_rays("rays_old.pk")
# save_rays('rays.pk', mirror_source(rays_data))

# #%%
# rays = rays_data["RAYS"]
# SOURCE_ANGLE, EYE_ROTATION = rays_data["DIM"]["Axis"].values()

# #%%
# MID_SOURCE = SOURCE_ANGLE.size - 1
# MID_ROT = int((EYE_ROTATION.size - 1)/2)

# shape = list(rays.shape)
# shape[0] = int(2 * MID_SOURCE + 1)
# new_rays = np.zeros(shape, dtype=rays.dtype)
# new_rays[MID_SOURCE:] = rays

# NEW_SOURCE_ANGLE = np.zeros([shape[0],], dtype=SOURCE_ANGLE.dtype)
# for sIdx in range(MID_SOURCE+1):
#     NEW_SOURCE_ANGLE[MID_SOURCE-sIdx] = -SOURCE_ANGLE[sIdx]
#     for rIdx in range(EYE_ROTATION.size):
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 0] = rays[sIdx, -1-rIdx, :, :, 0]
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 1] = -rays[sIdx, -1-rIdx, :, :, 1]
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 2] = rays[sIdx, -1-rIdx, :, :, 2]
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 3] = rays[sIdx, -1-rIdx, :, :, 3]
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 4] = -rays[sIdx, -1-rIdx, :, :, 4]
#         new_rays[MID_SOURCE-sIdx, rIdx, :, :, 5] = rays[sIdx, -1-rIdx, :, :, 5]
# NEW_SOURCE_ANGLE[MID_SOURCE:] = SOURCE_ANGLE

# new_rays_data = {
#     "RAYS" : new_rays,
#     "DIM" : {
#         "Axis" : {
#             "SourceAngle" : NEW_SOURCE_ANGLE,
#             "EyeRotation" : EYE_ROTATION
#         },
#         "Info" : {
#             "Code" : "SA{:d}ER{:d}",
#             "Shape" : [NEW_SOURCE_ANGLE.size, EYE_ROTATION.size]
#         }
#     },
#     "INFO" : {
#         "SurfaceIndex" : rays_data["INFO"]["SurfaceIndex"]
#     }
# }
# save_rays('rays.pk', new_rays_data)
# %%
