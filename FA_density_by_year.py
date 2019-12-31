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
output_file("FA-yearly-density.html")

# Load Dataset
data_frame = pd.read_csv('mnt_proj_route_data.csv')

# total the number of FAs logged per year
Years = list(range(1901,2019))
numFAs = []
for yr in Years:
    numFAs.append(len(data_frame[data_frame['FAyear']==yr]))

# convert Years to strings for labels
Years = [str(y) for y in Years]
    
source2 = ColumnDataSource(data=dict(Years=Years, numFAs=numFAs))

# Custom tooltip to display images on hover
TOOLTIPS = """
<div>
    <div float: left; width: 230px;>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 100px;">@numFAs First Ascents reported during @Years</span>
        </div>
    </div>
</div>
"""

p = figure(x_range=Years, plot_height=700,plot_width=1200, toolbar_location=None, tooltips=TOOLTIPS, title="Number of reported First Ascents by year on Mountain Project")
p.vbar(x='Years', top='numFAs', width=1, source=source2,
       line_color='white',fill_color = factor_cmap('Years', palette=Inferno256[0:len(Years)], factors=Years))

p.xaxis.major_label_orientation = math.pi/2
p.xgrid.grid_line_color = None
p.y_range.start = 0
p.title.text_font_size = '20pt'
p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Number of FAs reported on Mountain Project'

show(p)
