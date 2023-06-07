#%%
import numpy as np
from utility import read_rays
from utility import create_bokeh_rays, create_bokeh_eye_profile_from_file

from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider
from bokeh.models import Range1d, BoxZoomTool, WheelZoomTool

#%%
ray_dict = read_rays("rays.pk")
init_state, source_C_rays, source_M_rays = \
    create_bokeh_rays(ray_dict, infinite_object=30)

EYE_ROTATION = ray_dict["DIM"]["Axis"]["EyeRotation"]
eye_rot_start = EYE_ROTATION.min()
eye_rot_end = EYE_ROTATION.max()
eye_rot_step = np.abs(EYE_ROTATION[1] - EYE_ROTATION[0])
eye_rot_init = EYE_ROTATION[init_state["index"][1]]

#%%
source_eye_profiles = create_bokeh_eye_profile_from_file("eye_profile.pk")

#%%
# create a new plot with default tools, using figure
TOOLS = "pan,wheel_zoom,reset"
p = figure(
    title="Simple line example", 
    tools=TOOLS,
    x_axis_label='x', 
    y_axis_label='y',
    width=1100,
    height=300,
    match_aspect=True,
    sizing_mode='scale_both')
p.toolbar.logo = None
p.add_tools(BoxZoomTool(match_aspect=True))
p.toolbar.active_scroll = p.select_one(WheelZoomTool)
p.x_range = Range1d(-20, 430)
p.y_range = Range1d(-55, 55)

c_line = p.line(
    x='x', y='y', 
    source=source_C_rays,
    line_width=1,
    line_color='blue')
m_line = p.multi_line(
    xs='x', ys='y', 
    source=source_M_rays,
    line_width=1,
    line_color='red')

eye_profiles = p.multi_line(
    'x', 'y', source=source_eye_profiles,
    line_width=1,
    line_color='black')

rot_slider = Slider(title="Eye Rotation [deg]: ", 
                    value=eye_rot_init, 
                    start=eye_rot_start, 
                    end=eye_rot_end, step=eye_rot_step)
rot_callback = CustomJS(args=dict(
    source_eye_profiles=source_eye_profiles, 
    source_C_rays=source_C_rays,
    source_M_rays=source_M_rays), code="""
    source_eye_profiles.data['x']=source_eye_profiles.data['ER'+this.value+'x'].slice(0);
    source_eye_profiles.data['y']=source_eye_profiles.data['ER'+this.value+'y'].slice(0);
    source_C_rays.data['x']=source_C_rays.data['SA0ER'+this.value+'x'].slice(0);
    source_C_rays.data['y']=source_C_rays.data['SA0ER'+this.value+'y'].slice(0);
    source_M_rays.data['x']=source_M_rays.data['SA0ER'+this.value+'x'].slice(0);
    source_M_rays.data['y']=source_M_rays.data['SA0ER'+this.value+'y'].slice(0);
    source_eye_profiles.change.emit();
    source_C_rays.change.emit();
    source_M_rays.change.emit();
""")
rot_slider.js_on_change('value', rot_callback)
#%%
output_file(filename="main.html", title="Static HTML file")
#save(p)
save(column(rot_slider, p))