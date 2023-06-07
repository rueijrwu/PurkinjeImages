import numpy as np
from functools import reduce
import operator
from bokeh.models import ColumnDataSource
import pickle

def create_bokeh_rays(data, infinite_object=None):
    rays = data["RAYS"]
    dim_value = data["DIM"]["Axis"].values()
    dim_code, dim_shape = data["DIM"]["Info"].values()

    source_rays_list = [ColumnDataSource(), ColumnDataSource()]
    dim_init_idx = None
    dim_init_name = None
    for idx in range(reduce(operator.mul, dim_shape)):
        uIdx = np.unravel_index(idx, dim_shape)
        dim_item_value = list(map(
            lambda arr, idx : arr[idx].astype(dtype=int),
            dim_value, uIdx
        ))
        name = dim_code.format(*dim_item_value)
        
        if dim_init_idx is None and all([val == 0 for val in dim_item_value]):
            dim_init_idx = idx
            dim_init_name = name
        for tIdices, source_rays in zip([[0], [1, 2]], source_rays_list):
            XX = []
            YY = []
            for tIdx in tIdices:
                xx = rays[tuple(uIdx) + (slice(None), tIdx, 2)]
                yy = rays[tuple(uIdx) + (slice(None), tIdx, 1)]
                if infinite_object is not None:
                    if np.isinf(xx[0]) :
                        xx[0] = infinite_object
                    if np.isinf(yy[0]) :
                        yy[0] = infinite_object
                XX.append(xx.tolist())
                YY.append(yy.tolist())
            if len(XX) == 1:
                XX = XX[0]
                YY = YY[0]
            source_rays.add(XX, name="{:s}x".format(name))
            source_rays.add(YY, name="{:s}y".format(name))

    if dim_init_idx is not None:
        uIdx = np.unravel_index(dim_init_idx, dim_shape)
        for tIdices, source_rays in zip([[0], [1, 2]], source_rays_list):
            XX = []
            YY = []
            for tIdx in tIdices:
                xx = rays[tuple(uIdx) + (slice(None), tIdx, 2)]
                yy = rays[tuple(uIdx) + (slice(None), tIdx, 1)]
                if infinite_object is not None:
                    if np.isinf(xx[0]) :
                        xx[0] = infinite_object
                    if np.isinf(yy[0]) :
                        yy[0] = infinite_object
                XX.append(xx.tolist())
                YY.append(yy.tolist())
            if len(XX) == 1:
                XX = XX[0]
                YY = YY[0]
            source_rays.add(XX, name="x".format(name))
            source_rays.add(YY, name="y".format(name))
        dim_init_idx = uIdx

    init_dict = {
        "index": dim_init_idx,
        "name": dim_init_name,
    }
    return init_dict, *source_rays_list

def save_rays(filename, data):
    with open(filename, 'wb') as handle:
        pickle.dump(
            data,
            handle, protocol=pickle.HIGHEST_PROTOCOL
        )

def read_rays(filename):
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)
        return data

def create_bokeh_eye_profile_from_file(filename):
    with open(filename, 'rb') as handle:
        eye_profile_data = pickle.load(handle)
        return create_bokeh_eye_profile(eye_profile_data)

def create_bokeh_eye_profile(data):
    eye_rotation = data["EyeRotation"].astype(dtype=int)
    eye_profiles = data["Profile"]
    source_eye = ColumnDataSource()
    for rIdx, rot in enumerate(eye_rotation):
        if rot == 0:
            init_idx = rIdx
        ex = eye_profiles[0, rIdx, :, :]
        ey = eye_profiles[1, rIdx, :, :]
        source_eye.add(ex.tolist(), name="ER{:d}x".format(rot))
        source_eye.add(ey.tolist(), name="ER{:d}y".format(rot))

    ex = eye_profiles[0, init_idx, :, :]
    ey = eye_profiles[1, init_idx, :, :] 
    source_eye.add(ex.tolist(), name="x")
    source_eye.add(ey.tolist(), name="y")
    return source_eye

# def save_bokeh_rays(
#         filename, desc, init_dict, source_C_rays, source_M_rays):
#     with open(filename, 'wb') as handle:
#         pickle.dump(
#             {
#                 "Desc" : desc,
#                 "InitialState" : init_dict,
#                 "ChiefRays" : source_C_rays,
#                 "MarginalRays" : source_M_rays
#             },
#             handle, protocol=pickle.HIGHEST_PROTOCOL)
        
# def save_bokeh_rays_from_raw(
#         filename, data, infinite_object=None):
#     init_dict, source_C_rays, source_M_rays = \
#         create_bokeh_rays(
#             data, 
#             infinite_object=infinite_object
#         )

#     save_bokeh_rays(
#         filename,
#         data["DIM"],
#         init_dict, 
#         source_C_rays, 
#         source_M_rays
#     )

# def read_bokeh_rays(filename):
#     with open(filename, 'rb') as handle:
#         data = pickle.load(handle)
#         return data.values()
    

#
# out_data = {
#     "RAYS" : rays,
#     "DIM" : {
#         "Axis" : {
#             "SourceAngle" : SOURCE_ANGLE,
#             "EyeRotation" : ROTATIONS
#         },
#         "Info" : {
#             "Code" : "SA{:d}ER{:d}",
#             "Shape" : [SOURCE_ANGLE.size, ROTATIONS.size]
#         }
#     },
#     "INFO" : {
#         "SurfaceIndex" : SURFACES
#     }
# }
