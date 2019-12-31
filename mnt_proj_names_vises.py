import time
import random
import datetime as dt
import os
import pickle
import re
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

names_data = pd.read_csv('mnt_proj_names_data.csv')

num_uniques = 200
unique_names = names_data[names_data['Count']==1]['Word'].to_list()
cloud_unique_names = [unique_names[n] for n in list(np.random.permutation(len(unique_names))[0:num_uniques*2])]

text = ""
count = 0
i = 0
while count < num_uniques:
    if len(cloud_unique_names[i]) > 3 and cloud_unique_names[i].isalpha():
        new = cloud_unique_names[i]+" "
        text += new*np.random.randint(3)
        count += 1
    i += 1
    
# Create the wordcloud object
wordcloud = WordCloud(width=1080, height=960, max_font_size=50, max_words=num_uniques, margin=0, collocations=False, ).generate(text)
 
# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
##plt.savefig('route_word_cloud.eps', format='eps')
plt.savefig('route_word_cloud-unique.png', dpi=300)
plt.show()


num_words = 300
freq = 100
while len(names_data[names_data['Count'] > freq]) < num_words:
    freq -= 1
    
names_data = names_data[names_data['Count'] > freq]
print('Top ',len(names_data),' words')

text = ""
for i in range(len(names_data)):
    new = names_data['Word'].loc[i]+" "
    text += new*names_data['Count'].loc[i]
 
# Create the wordcloud object
wordcloud = WordCloud(width=1080, height=960, margin=0, collocations=False).generate(text)
 
# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
##plt.savefig('route_word_cloud.eps', format='eps')
plt.savefig('route_word_cloud-popular.png', dpi=300)
plt.show()


from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
import math
from bokeh.palettes import Dark2_5
from bokeh.palettes import Inferno256


output_file("route_name_count.html")

# further reduce number for this vis
num_words = 50
freq = 100
while len(names_data[names_data['Count'] > freq]) < num_words:
    freq -= 1
names_data = names_data[names_data['Count'] > freq]

words = names_data['Word'].to_list()
counts = names_data['Count'].to_list()


source = ColumnDataSource(data=dict(words=words, counts=counts))

# Custom tooltip to display images on hover
TOOLTIPS = """
<div>
    <div float: left; width: 230px;>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 100px;">"@words" occurs</span>
        </div>
        <div>
            <span style="float: left; margin: 10px 15px 0px 15px; font-size: 15px; width: 100px;">@counts times</span>
        </div>
    </div>
</div>
"""

p = figure(x_range=words, plot_height=700,plot_width=1200, toolbar_location=None, tooltips=TOOLTIPS, title="Common Route Name Words and Their Occurance Counts")
p.vbar(x='words', top='counts', width=1, source=source,
       line_color='white',fill_color = factor_cmap('words', palette=Inferno256[0:len(words)], factors=words))

p.xaxis.axis_label = 'Common words in route names'
p.yaxis.axis_label = 'Number of occurances'
p.title.text_font_size = '20pt'
##fill_color=factor_cmap('words', palette=Spectral6, factors=words)

p.xaxis.major_label_orientation = math.pi/2
p.xgrid.grid_line_color = None
p.y_range.start = 0
##p.y_range.end = 9
##p.legend.orientation = "horizontal"
##p.legend.location = "top_center"

show(p)
