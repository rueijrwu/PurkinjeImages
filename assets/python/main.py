import json
import pyodide
import numpy as np

from js import Bokeh, console, JSON

from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN

# data
x = np.linspace(0, np.pi, num=50)
y = np.sin(x)

# create a new plot with default tools, using figure
p = figure(
    title="Simple line example", 
    x_axis_label='x', 
    y_axis_label='y',
    #match_aspect=True,
    sizing_mode='scale_both')

# add a circle renderer with x and y coordinates, size, color, and alpha
p.line(x, y, legend_label="Temp.", line_width=2)
p_json = json.dumps(json_item(p, "myplot"))

Bokeh.embed.embed_item(JSON.parse(p_json))