#%%
import numpy as np
import pickle
import plotlib
from bokeh.plotting import output_file, save
from bokeh.layouts import row, column, layout
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider
from bokeh.io import export_svg, export_svgs, show
#%%
# surface profiles 
with open('./data/eye_profile.pk', 'rb') as handle:
    eye_profile_data = pickle.load(handle)
with open('./data/plane_profile.pk', 'rb') as handle:
    plane_profile_data = pickle.load(handle)
p1_rays = plotlib.RaysData.from_file('./data/p1_S15_R15.pk')
p3_rays = plotlib.RaysData.from_file('./data/p3_S15_R15.pk')
p3inf_rays = plotlib.RaysData.from_file('./data/p3INF_S15_R15.pk')
p4_rays = plotlib.RaysData.from_file('./data/p4_S15_R15.pk')
#%%
# figure parameters
fig_width = 620
fig_height = 320
sizing_mode='scale_width'
tick_font_size = '12pt'
font_size = '12pt'
x_range = [-25, 150]
y_range = [-45, 45]

# trace_plot = plotlib.TracePlot()
# trace_plot.set_rays(p4_rays, reversed_y=True)
# trace_plot.render(
#     title="Trace",
#     x_axis_label='x [mm]', 
#     y_axis_label='y [mm]',
#     width=200,
#     height=200,
#     sizing_mode=sizing_mode,
#     match_aspect=True,
#     tools="pan,wheel_zoom,reset",
#     active_scroll ="wheel_zoom"
# )

# p1 cross-section plot
p1_cross = plotlib.CrossSectionPlot()
p1_cross.set_layout(eye_profile_data, plane_profile_data)
p1_cross.set_rays(p1_rays, reversed_y=True)
p1_cross.render(
    title="P1",
    x_axis_label='x [mm]', 
    y_axis_label='y [mm]',
    width=fig_width,
    height=fig_height,
    sizing_mode=sizing_mode,
    match_aspect=True,
    tools="pan,wheel_zoom,reset",
    active_scroll ="wheel_zoom",
    toolbar_location=None
)
p1_cross.set_x_range(*x_range)
p1_cross.set_y_range(*y_range)

p1_cross.plot.xaxis.axis_label_text_font_size = font_size
p1_cross.plot.yaxis.axis_label_text_font_size = font_size
p1_cross.plot.xaxis.major_label_text_font_size = tick_font_size
p1_cross.plot.yaxis.major_label_text_font_size = tick_font_size
p1_cross.plot.output_backend = "svg"
#show(p1_cross.plot)

# p3
p3_cross = plotlib.CrossSectionPlot(shared_layout=p1_cross)
p3_cross.set_layout(eye_profile_data, plane_profile_data)
p3_cross.set_rays(p3_rays, reversed_y=True)
p3_cross.render(
    title="P3",
    x_axis_label='x [mm]', 
    y_axis_label='y [mm]',
    width=fig_width,
    height=fig_height,
    sizing_mode=sizing_mode,
    match_aspect=True,
    tools="pan,wheel_zoom,reset",
    active_scroll ="wheel_zoom",
    x_range=p1_cross.plot.x_range,
    y_range=p1_cross.plot.y_range,
    toolbar_location=None
)
p3_cross.plot.xaxis.axis_label_text_font_size = font_size
p3_cross.plot.yaxis.axis_label_text_font_size = font_size
p3_cross.plot.xaxis.major_label_text_font_size = tick_font_size
p3_cross.plot.yaxis.major_label_text_font_size = tick_font_size
p3_cross.plot.output_backend = "svg"


# p3
p3inf_cross = plotlib.CrossSectionPlot(shared_layout=p1_cross)
p3inf_cross.set_layout(eye_profile_data, plane_profile_data)
p3inf_cross.set_rays(p3inf_rays, reversed_y=True)
p3inf_cross.render(
    title="P3 Infinity",
    x_axis_label='x [mm]', 
    y_axis_label='y [mm]',
    width=fig_width,
    height=fig_height,
    sizing_mode=sizing_mode,
    match_aspect=True,
    tools="pan,wheel_zoom,reset",
    active_scroll ="wheel_zoom",
    x_range=p1_cross.plot.x_range,
    y_range=p1_cross.plot.y_range
)
p3inf_cross.plot.xaxis.axis_label_text_font_size = font_size
p3inf_cross.plot.yaxis.axis_label_text_font_size = font_size
p3inf_cross.plot.xaxis.major_label_text_font_size = tick_font_size
p3inf_cross.plot.yaxis.major_label_text_font_size = tick_font_size
p3inf_cross.plot.output_backend = "svg"


# p4 cross-section plot
p4_cross = plotlib.CrossSectionPlot(shared_layout=p1_cross)
p4_cross.set_layout(eye_profile_data, plane_profile_data)
p4_cross.set_rays(p4_rays, reversed_y=True)
p4_cross.render(
    title="P4",
    x_axis_label='x [mm]', 
    y_axis_label='y [mm]',
    width=fig_width,
    height=fig_height,
    sizing_mode=sizing_mode,
    match_aspect=True,
    tools="pan,wheel_zoom,reset",
    active_scroll ="wheel_zoom",
    x_range=p1_cross.plot.x_range,
    y_range=p1_cross.plot.y_range,
    toolbar_location=None
)

p4_cross.plot.xaxis.axis_label_text_font_size = font_size
p4_cross.plot.yaxis.axis_label_text_font_size = font_size
p4_cross.plot.xaxis.major_label_text_font_size = tick_font_size
p4_cross.plot.yaxis.major_label_text_font_size = tick_font_size
p4_cross.plot.output_backend = "svg"
#%%
source_angle = p4_rays.axis["SourceAngle"]
source_angle_start = source_angle.min()
source_angle_end = source_angle.max()
source_angle_step = np.abs(source_angle[1] - source_angle[0])
source_angle_init = source_angle[p4_cross.rays_init_idx[0]]

eye_rotation = p4_rays.axis["EyeRotation"]
eye_rot_start = eye_rotation.min()
eye_rot_end = eye_rotation.max()
eye_rot_step = np.abs(eye_rotation[1] - eye_rotation[0])
eye_rot_init = eye_rotation[p4_cross.rays_init_idx[1]]

rot_slider = Slider(title="Eye Rotation [deg]: ", 
                    value=eye_rot_init, 
                    start=eye_rot_start, 
                    end=eye_rot_end, step=eye_rot_step)
source_slider = Slider(title="Source Angle [deg]: ", 
                    value=source_angle_init, 
                    start=source_angle_start, 
                    end=source_angle_end, step=source_angle_step)

slider_callback = CustomJS(
    args=dict(
        rot_slider=rot_slider,
        source_slider=source_slider,
        source_eye_profiles=p4_cross.source_eye,
        p1_C_rays=p1_cross.source_C_rays,
        p1_M_rays=p1_cross.source_M_rays,
        p3_C_rays=p3_cross.source_C_rays,
        p3_M_rays=p3_cross.source_M_rays,
        p3inf_C_rays=p3inf_cross.source_C_rays,
        p3inf_M_rays=p3inf_cross.source_M_rays,   
        p4_C_rays=p4_cross.source_C_rays,
        p4_M_rays=p4_cross.source_M_rays
    ), 
    code="""
        var rot = 'ER'+rot_slider.value;
        var name = 'SA'+source_slider.value+rot;
        source_eye_profiles.data['x']=source_eye_profiles.data[rot+'x'].slice(0);
        source_eye_profiles.data['y']=source_eye_profiles.data[rot+'y'].slice(0);
        p1_C_rays.data['x']=p1_C_rays.data[name+'x'].slice(0);
        p1_C_rays.data['y']=p1_C_rays.data[name+'y'].slice(0);
        p1_M_rays.data['x']=p1_M_rays.data[name+'x'].slice(0);
        p1_M_rays.data['y']=p1_M_rays.data[name+'y'].slice(0);
        p3_C_rays.data['x']=p3_C_rays.data[name+'x'].slice(0);
        p3_C_rays.data['y']=p3_C_rays.data[name+'y'].slice(0);
        p3_M_rays.data['x']=p3_M_rays.data[name+'x'].slice(0);
        p3_M_rays.data['y']=p3_M_rays.data[name+'y'].slice(0);
        p3inf_C_rays.data['x']=p3inf_C_rays.data[name+'x'].slice(0);
        p3inf_C_rays.data['y']=p3inf_C_rays.data[name+'y'].slice(0);
        p3inf_M_rays.data['x']=p3inf_M_rays.data[name+'x'].slice(0);
        p3inf_M_rays.data['y']=p3inf_M_rays.data[name+'y'].slice(0);
        p4_C_rays.data['x']=p4_C_rays.data[name+'x'].slice(0);
        p4_C_rays.data['y']=p4_C_rays.data[name+'y'].slice(0);
        p4_M_rays.data['x']=p4_M_rays.data[name+'x'].slice(0);
        p4_M_rays.data['y']=p4_M_rays.data[name+'y'].slice(0);
        source_eye_profiles.change.emit();
        p1_C_rays.change.emit();
        p1_M_rays.change.emit();
        p3_C_rays.change.emit();
        p3_M_rays.change.emit();
        p3inf_C_rays.change.emit();
        p3inf_M_rays.change.emit();
        p4_C_rays.change.emit();
        p4_M_rays.change.emit();
    """
)
rot_slider.js_on_change('value', slider_callback)
source_slider.js_on_change('value', slider_callback)

#%%
#output_file(filename="main.html", title="Static HTML file")

# plot_row = row(
#     column(p1_cross.plot, p4_cross.plot),
#     trace_plot.plot
# )
slider_row = row(rot_slider, source_slider, sizing_mode='scale_width')
layout = column(
    layout([[p1_cross.plot, p3inf_cross.plot], 
            [p4_cross.plot, p3_cross.plot]], sizing_mode='scale_width'), 
    slider_row, sizing_mode='scale_width')
show(layout)

#%%
# export_svg(p3inf_cross.plot, filename = "p3inf.svg")
# export_svg(p1_cross.plot, filename = "p1.svg")
# export_svg(p3_cross.plot, filename = "p3.svg")
# export_svg(p4_cross.plot, filename = "p4.svg")
#<iframe seamless src="/plot.html" width="1200" height="800"></iframe>