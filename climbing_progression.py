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
from bokeh.models import Circle, ColumnDataSource, Line, LinearAxis, Range1d
from bokeh.plotting import figure, output_notebook, show
from bokeh.core.properties import value

# Declare output output output file
output_file("climbing-difficulty-progression.html")

# Load Dataset
data_frame = pd.read_csv('mnt_proj_route_data.csv')

# determine hardest logged route per year in each category
years = list(range(1900,2020))
hardest_roped = []
hardest_boulder = []
hardest_sport = []
hardest_trad = []

ii = 0
for yr in years:
    # sport climb
    try: temp_hardest = max(data_frame[(data_frame['FAyear']==yr)&(data_frame['Style']=='Sport')]['numeric_grade'].values.tolist())
    except ValueError: temp_hardest = 0
    if len(hardest_sport)>0:
        if temp_hardest > hardest_sport[-1]:  
            hardest_sport.append(temp_hardest)
        else: hardest_sport.append(hardest_sport[-1])
    else: hardest_sport = [temp_hardest]

    # trad climb
    try: temp_hardest = max(data_frame[(data_frame['FAyear']==yr)&(data_frame['Style']=='Trad')]['numeric_grade'].values.tolist())
    except ValueError: temp_hardest = 0
    if len(hardest_trad)>0:
        if temp_hardest > hardest_trad[-1]:  
            hardest_trad.append(temp_hardest)
        else: hardest_trad.append(hardest_trad[-1])
    else: hardest_trad = [temp_hardest]

    # bouldering climb
    try: temp_hardest = max(data_frame[(data_frame['FAyear']==yr)&(data_frame['Style']=='Boulder')]['numeric_grade'].values.tolist())
    except ValueError: temp_hardest = 0
    if len(hardest_boulder)>0:
        if temp_hardest > hardest_boulder[-1]:  
            hardest_boulder.append(temp_hardest)
        else: hardest_boulder.append(hardest_boulder[-1])
    else: hardest_boulder = [temp_hardest]

    # hardest roped
    temp_hardest = max(hardest_sport[ii],hardest_trad[ii])
    if len(hardest_roped)>0:
        hardest_roped.append(temp_hardest)
    else: hardest_roped = [temp_hardest]

    ii+= 1
   

data_source = ColumnDataSource(
    data=dict(
        x=years,
        hardest_sport=hardest_sport,
        hardest_trad=hardest_trad,
        hardest_boulder=hardest_boulder,
    )
)

# Custom tooltip to display images on hover
TOOLTIPS = """
<div>
    <div float: left; width: 230px;>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 100px;">Most difficult FA reported during @x</span>
        </div>
    </div>
</div>
"""

p = figure(plot_width=1200, plot_height=700, x_range=(min(years), max(years)), tooltips=TOOLTIPS, title="Progression of Most Difficult Climbs in Each Discipline",)
column1 = "hardest_sport"
column2 = "hardest_trad"
column3 = "hardest_boulder"
# FIRST AXIS
p.line("x", column1,  color=Inferno256[170], source=data_source)
p.circle("x", column1, legend='Hardest Sport climb to-date',fill_color=Inferno256[170], size=8,source=data_source)

p.line("x", column2,  color=Inferno256[85], source=data_source)
p.circle("x", column2, legend='Hardest Trad climb to-date',fill_color=Inferno256[85], size=8, source=data_source)

p.y_range = Range1d(0, 19)
# SECOND AXIS
column3_range = column3 + "_range"
p.extra_y_ranges = {
    column3_range: Range1d( 0, 19)
}
p.legend.location = "top_left"

p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Difficulty Grade'
p.title.text_font_size = '20pt'
p.line("x", column3,  y_range_name=column3_range, color=Inferno256[0],source=data_source)
p.circle("x", column3, legend='Hardest Boulder problem to-date', fill_color=Inferno256[0], size=8, source=data_source)
#####################################

show(p)
