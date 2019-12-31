import pandas as pd
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from bokeh.models import Legend
from bokeh.models.widgets import RadioGroup
from bokeh.models.widgets import Panel, Tabs
from bokeh.palettes import Inferno256
import numpy as np

# Declare output output output file
output_file("scatter.html")

# Load Dataset
data_frame = pd.read_csv('mnt_proj_route_data.csv')
new_frame = data_frame[data_frame['img_url'].notnull()]
new_frame = new_frame.reindex(list(range(len(new_frame))))
# add some uniform scatter to data for better visualization
for r in range(len(data_frame)):
    if r % 100 == 0: print(r,' of ',len(data_frame))
    data_frame.loc[r,'FAyear'] += np.random.random() - 0.5
    if data_frame.loc[r,'numeric_grade'] > 1:
        data_frame.loc[r,'numeric_grade'] += np.random.random() - 0.5

# Grab sub frames for color mapping
Style = data_frame['Style']

# maybe will filter to greater than 1960's or so

# Generate ColumnDataSource for plots
source = ColumnDataSource(data=dict(
##    style=style,
    x=data_frame['FAyear'],
    y=data_frame['numeric_grade'],
    titles=data_frame['Title'],
    Style=data_frame['Style'], # this is temp! 
    imgs=data_frame['img_url'],
))

# Custom tooltip to display images on hover
TOOLTIPS = """
<div>
    <div float: left; width: 230px;>
        <div>
            <img
                src="@imgs" height="200" alt="@imgs"
                style="float: left; margin: 15px 15px 15px 15px;"
                border="2"
            ></img>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 17px; width: 200px; font-weight: bold;">Route name: @titles</span>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 200px;">Style: @Style</span>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 200px;">FA Year: @x</span>
        </div>
    </div>
</div>
"""

# Generate first plot
colors1 = factor_cmap('Style', palette=[Inferno256[0],Inferno256[85],Inferno256[170],'#238b45'], factors=Style.unique())

p = figure(plot_width=1500, plot_height=1000, tooltips=TOOLTIPS,
           title="Route First Ascents by Difficulty and Year", lod_threshold=None)

p.circle('x', 'y', size=6, source=source, fill_color=colors1, line_color=colors1, legend=colors1)


p.xaxis.axis_label = 'Year'
p.yaxis.axis_label = 'Difficulty Grade'


p.min_border_left = 100
p.min_border_right = 100
p.min_border_top = 200
p.min_border_bottom = 200

p.legend.location = "top_left"
p.title.text_font_size = '20pt'

show(p)
