from math import pi
import pandas as pd
from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.models.widgets import Select
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
import math
from bokeh.palettes import Dark2_5
from bokeh.palettes import Inferno256
import pandas as pd
import time
import random
import datetime as dt
import os
import pickle
import re
import numpy as np
import pandas as pd


# Declare output output output file
output_file("Mnt-proj-overview-pie.html")

# Load Dataset
data_frame = pd.read_csv('mnt_proj_route_data.csv')

x ={'Bouldering':len(data_frame[data_frame['Style']=='Boulder']),
    'Traditional (Trad)':len(data_frame[data_frame['Style']=='Trad']),
    'Sport':len(data_frame[data_frame['Style']=='Sport']),
    'Aid':len(data_frame[data_frame['Style']=='Aid'])}

data = pd.Series(x).reset_index(name='value').rename(columns={'index':'Style'})
data['angle'] = data['value']/data['value'].sum() * 2*pi

##data['color'] = ['#e41a1c','#377eb8' ,'#4daf4a' ,'#984ea3' ]
data['color'] = [Inferno256[0],Inferno256[85],Inferno256[170],'#238b45']

data['imgs'] =['https://cdn-files.apstatic.com/climb/114202430_large_1522344758.jpg',
 'https://cdn-files.apstatic.com/climb/118064406_large_1574113942.jpg',
 'https://cdn-files.apstatic.com/climb/116505010_large_1549132648.jpg',
 'https://cdn-files.apstatic.com/climb/113293872_large_1499716678.jpg']
 
# Custom tooltip to display images on hover
TOOLTIPS = """
<div>
    <div float: left; width: 230px;>
        <div>
            <img
                src="@imgs" height="400" alt="@imgs"
                style="float: left; margin: 15px 15px 15px 15px;"
                border="2"
            ></img>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 200px;">Style: @Style</span>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 200px;"># routes: @value</span>
        </div>
    </div>
</div>
"""


p = figure(plot_height=700,plot_width=1200, title="Mountain Project Data Overview by Discipline", tooltips=TOOLTIPS, toolbar_location=None,
        tools="hover")
p.title.text_font_size = '20pt'
p.xaxis.visible = False
p.yaxis.visible = False
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='Style', source=data)

show(p)


select = Select(title="Metric:", value="Fear Level", options=["Fear Level","Tech Savviness"],width=300)

