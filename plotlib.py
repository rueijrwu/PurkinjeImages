#%%
import numpy as np
from bokeh.plotting import figure
import pickle
from bokeh.models import ColumnDataSource
import operator
from functools import reduce
from bokeh.models import Range1d, BoxZoomTool, WheelZoomTool, HoverTool
from bokeh.models import Arrow, OpenHead, TeeHead

class RaysData(object):
    def __init__(self, rays, axis, code, dtype=np.double, name=""):
        if rays is not None:
            if not isinstance(rays, np.ndarray):
                rays = np.array(rays, dtype=dtype)
            if len(rays.shape) < 3:
                raise ValueError("Shape of rays is incompatible. len(shape) > 2")
        self.rays = rays
        self.axis = axis
        self.code = code
        if rays is not None:
            self.shape = list(rays.shape[:-3])
        else:
            self.shape = None
        self.name = name

    @staticmethod
    def from_dict(data, dict_name=None):
        ret = RaysData(None, None, None)
        ret.rays = data["RAYS"]
        ret.axis = data["DIM"]["Axis"]
        ret.code = data["DIM"]["Info"]["Code"]
        ret.shape = list(ret.rays.shape[:-3])
        if dict_name:
            ret.name = dict_name
        return ret

    @staticmethod
    def from_file(filename, is_dict=False, **kwargs):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)
            if is_dict:
                data = RaysData.from_dict(data, **kwargs)
            return data


class CrossSectionPlot(object):
    def __init__(self, shared_layout=None):
        self.source_C_rays = ColumnDataSource()
        self.source_M_rays = ColumnDataSource()
        self.rays_init_idx = None
        self.rays_init_name = None
        self.rays_reversed_y = False 
        if shared_layout:
            self.source_eye = shared_layout.source_eye
            self.source_lens = shared_layout.source_lens
            self.source_stop = shared_layout.source_stop
            self.source_plane = shared_layout.source_plane
        else:
            self.source_eye = ColumnDataSource()
            self.source_stop = ColumnDataSource()
            self.source_lens = ColumnDataSource()
            self.source_plane = ColumnDataSource()

    def set_rays(self, data, reversed_y=False):
        if not isinstance(data, RaysData):
            raise TypeError("Incompatible data. Require RaysData")
        
        axis_value = data.axis.values()
        axis_code = data.code
        axis_shape = data.shape

        rays_init_idx = None
        rays_init_name = None
        source_rays_list = [self.source_C_rays, self.source_M_rays]

        yscale = -1 if reversed_y else 1
        for idx in range(reduce(operator.mul, axis_shape)):
            uIdx = np.unravel_index(idx, axis_shape)
            axis_item_value = list(map(
                lambda arr, idx : arr[idx].astype(dtype=int),
                axis_value, uIdx
            ))
            name = axis_code.format(*axis_item_value)
            
            if rays_init_idx is None and all([val == 0 for val in axis_item_value]):
                rays_init_idx = idx
                rays_init_name = name
            for tIndices, source_rays in zip([[0], [1, 2]], source_rays_list):
                XX = []
                YY = []
                for tIdx in tIndices:
                    xx = data.rays[tuple(uIdx) + (slice(None), tIdx, 2)]
                    yy = yscale * data.rays[tuple(uIdx) + (slice(None), tIdx, 1)]
                    XX.append(xx.tolist())
                    YY.append(yy.tolist())
                if len(XX) == 1:
                    XX = XX[0]
                    YY = YY[0]
                source_rays.add(XX, name="{:s}x".format(name))
                source_rays.add(YY, name="{:s}y".format(name))

        if rays_init_idx is not None:
            uIdx = np.unravel_index(rays_init_idx, axis_shape)
            for tIndices, source_rays in zip([[0], [1, 2]], source_rays_list):
                XX = []
                YY = []
                for tIdx in tIndices:
                    xx = data.rays[tuple(uIdx) + (slice(None), tIdx, 2)]
                    yy = yscale * data.rays[tuple(uIdx) + (slice(None), tIdx, 1)]
                    XX.append(xx.tolist())
                    YY.append(yy.tolist())
                if len(XX) == 1:
                    XX = XX[0]
                    YY = YY[0]
                source_rays.add(XX, name="x".format(name))
                source_rays.add(YY, name="y".format(name))
            rays_init_idx = uIdx

        self.rays_reversed_y = reversed_y
        self.rays_init_idx = rays_init_idx
        self.rays_init_name = rays_init_name

    def set_rays_from_file(self, 
            filepath, 
            reversed_y=False,
            is_dict=False,
            dict_name=""):
        self.set_rays(
            RaysData.from_file(
                filepath, 
                is_dict=is_dict, 
                dict_name=dict_name), 
            reversed_y=reversed_y)

    def set_layout(self, 
                   eye_profile_data, 
                   plane_profile_data,
                   margin=5):
        # eye
        eye_rotation = eye_profile_data["EyeRotation"].astype(dtype=int)
        eye_profiles = eye_profile_data["Profile"]
        for rIdx, rot in enumerate(eye_rotation):
            if rot == 0:
                init_idx = rIdx
            ex = eye_profiles[0, rIdx, :, :]
            ey = eye_profiles[1, rIdx, :, :]
            self.source_eye.add(ex.tolist(), name="ER{:d}x".format(rot))
            self.source_eye.add(ey.tolist(), name="ER{:d}y".format(rot))

        ex = eye_profiles[0, init_idx, :, :]
        ey = eye_profiles[1, init_idx, :, :] 
        self.source_eye.add(ex.tolist(), name="x")
        self.source_eye.add(ey.tolist(), name="y")

        # plane surface 
        # image
        plane_profiles = plane_profile_data["Profiles"]
        image = plane_profile_data["Image"]
        ix = plane_profiles[image, :, 0].reshape([-1, 2])
        iy = plane_profiles[image, :, 1] + \
            np.copysign(margin, plane_profiles[image, :, 1]).reshape([-1, 2])

        #stop
        stop = plane_profile_data["Stop"]
        sx = plane_profiles[stop, :, 0].reshape([-1, 2])
        sy = plane_profiles[stop, :, 1].reshape([2, -1])
        sx = np.vstack([sx, sx])
        sy = np.hstack([sy, sy + np.copysign(margin, sy)])
        self.source_stop.add(sx.tolist(), name="x")
        self.source_stop.add(sy.tolist(), name="y")

        # relay
        plane_profiles = plane_profile_data["Profiles"]
        relay = plane_profile_data["Relay"]
        rx = plane_profiles[relay, :, 0].reshape([-1, 2])
        ry = plane_profiles[relay, :, 1] + \
            np.copysign(margin, plane_profiles[image, :, 1]).reshape([-1, 2])
        self.source_lens.add(rx.tolist(), name="x")
        self.source_lens.add(ry.tolist(), name="y")


        XX = np.concatenate([ix, sx, rx])
        YY = np.concatenate([iy, sy, ry])
        self.source_plane.add(XX.tolist(), name="x")
        self.source_plane.add(YY.tolist(), name="y")

    def render(self, **kwargs):
        self.plot = figure(**kwargs)

        # system
        o_lin = self.plot.line(
            [-20, 430], [0, 0],
            line_width=1,
            line_color='black')

        origin = self.plot.circle(
            0, 0, 
            size=3,  
            fill_color="black", 
            line_width=0)

        # rays
        c_line = self.plot.line(
            x='x', y='y', 
            source=self.source_C_rays,
            legend_label="Chief ray",
            line_width=1,
            line_color='blue')
        
        m_line = self.plot.multi_line(
            xs='x', ys='y', 
            source=self.source_M_rays,
            legend_label="Marginal ray",
            line_width=1,
            line_color='red')

        # surface profile
        eye_profiles = self.plot.multi_line(
            'x', 'y', source=self.source_eye,
            line_width=1,
            line_color='black')

        plane_profiles = self.plot.multi_line(
            'x', 'y', source=self.source_plane,
            line_width=1,
            line_color='black')
        
        #arrow
        oh = OpenHead(line_color='black', line_width=1,size=8)
        xx = np.array(self.source_lens.data['x'])
        yy = np.array(self.source_lens.data['y'])
        for idx in range(xx.shape[0]):
            self.plot.add_layout(
                Arrow(
                    x_start=xx[idx, 0], 
                    y_start=yy[idx, 0], 
                    x_end=xx[idx, 1], 
                    y_end=yy[idx, 1],
                    start=oh,
                    end=oh, 
                    line_color='black', 
                    line_width=1
                )
            )

        # stop bar    
        th = TeeHead(line_color='black', line_width=1,size=8)
        xx = np.array(self.source_stop.data['x'])
        yy = np.array(self.source_stop.data['y'])
        for idx in range(xx.shape[0]):
            self.plot.add_layout(
                Arrow(
                    x_start=xx[idx, 0], 
                    y_start=yy[idx, 0], 
                    x_end=xx[idx, 1], 
                    y_end=yy[idx, 1],
                    start=th,
                    end=None,
                    line_color='black', 
                    line_width=1
                )
            )
        self.plot.title.align = "left"
        self.plot.legend.location = "top_left"
        self.plot.legend.click_policy="hide"

    def set_x_range(self, val1, val2):
        self.plot.x_range = Range1d(val1, val2)

    def set_y_range(self, val1, val2):
        self.plot.y_range = Range1d(val1, val2)


class TracePlot(object):
    def __init__(self):
        self.source_p4_cy = ColumnDataSource()

    def set_rays(self, p4_data, reversed_y=False):
        cy4 = p4_data.rays[:, :, -1, 0, 1]
        eye_rotation = p4_data.axis["EyeRotation"]
        source_angle = p4_data.axis["SourceAngle"]
        for sIdx, sang in enumerate(source_angle.astype(dtype=int)):
            self.source_p4_cy.add(
                cy4[sIdx, :].tolist(), name="SA{:d}".format(sang))
        idx = int((cy4.shape[0] - 1) / 2)
        self.source_p4_cy.add(eye_rotation.tolist(), name='x')
        self.source_p4_cy.add(cy4[idx, :].tolist(), name='y')

    def set_rays_from_file(self, 
            filepath, 
            reversed_y=False,
            is_dict=False,
            dict_name=""):
        self.set_rays(
            RaysData.from_file(
                filepath, 
                is_dict=is_dict, 
                dict_name=dict_name), 
            reversed_y=reversed_y)
        
    def render(self, **kwargs):
        self.plot = figure()

        # system
        p4_trace = self.plot.line(
            x='x', y='y',
            source=self.source_p4_cy,
            legend_label="P4",
            line_width=1,
            line_color='blue')
        
        self.plot.title.align = "center"
        self.plot.legend.location = "top_left"
        self.plot.legend.click_policy="mute"

    def set_x_range(self, val1, val2):
        self.plot.x_range = Range1d(val1, val2)

    def set_y_range(self, val1, val2):
        self.plot.y_range = Range1d(val1, val2)

