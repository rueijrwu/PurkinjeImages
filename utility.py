import numpy as np
from functools import reduce
import operator
from bokeh.models import ColumnDataSource
import pickle

def create_bokeh_rays(data, reversed_y=False):
    rays = data["RAYS"]
    dim_value = data["DIM"]["Axis"].values()
    dim_code, dim_shape = data["DIM"]["Info"].values()
    yscale = -1 if reversed_y else 1
        
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
                yy = yscale * rays[tuple(uIdx) + (slice(None), tIdx, 1)]
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
                yy = yscale *rays[tuple(uIdx) + (slice(None), tIdx, 1)]
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

def create_bokeh_plane_profile_from_file(filename):
    with open(filename, 'rb') as handle:
        profile_data = pickle.load(handle)
        return create_bokeh_plane_profile(profile_data)

def create_bokeh_plane_profile(data, margin=10):
    source_plane = ColumnDataSource()
    profiles = data["Profiles"]
    stop = data["Stop"]
    surfaces = data["Surfaces"]
    IDX = surfaces != stop
    xx = profiles[IDX, :, 0]
    yy = profiles[IDX, :, 1] + np.copysign(margin, profiles[IDX, :, 1])

    IDX = ~IDX
    sx = profiles[IDX, :, 0]
    sy = profiles[IDX, :, 1].transpose()
    sxx = np.vstack([sx, sx])
    syy = np.hstack([sy, sy + np.copysign(margin, sy)])

    XX = np.concatenate([xx, sxx])
    YY = np.concatenate([yy, syy])
    source_plane.add(XX.tolist(), name="x")
    source_plane.add(YY.tolist(), name="y")
    return source_plane

def mirror_source(rays_data):
    #%%
    rays = rays_data["RAYS"]
    SOURCE_ANGLE, EYE_ROTATION = rays_data["DIM"]["Axis"].values()

    #%%
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

    new_rays_data = {
        "RAYS" : new_rays,
        "DIM" : {
            "Axis" : {
                "SourceAngle" : NEW_SOURCE_ANGLE,
                "EyeRotation" : EYE_ROTATION
            },
            "Info" : {
                "Code" : "SA{:d}ER{:d}",
                "Shape" : [NEW_SOURCE_ANGLE.size, EYE_ROTATION.size]
            }
        },
        "INFO" : {
            "SurfaceIndex" : rays_data["INFO"]["SurfaceIndex"]
        }
    }
    return new_rays_data