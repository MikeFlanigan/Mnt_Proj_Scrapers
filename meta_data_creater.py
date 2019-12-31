import time
import random
import datetime as dt
import os
import pickle
import re
import numpy as np
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import bs4

# set up a class for storing tree structure data from mountain project
class mntNode:
    def __init__(self, leaf, depth):
        # tree structure data
        if leaf: self.leaf = True # true if this is a climb, false otherwise
        else: self.leaf = False
        self.url = ''
        self.parent = ''
        self.depth = depth # depth of layer in tree
        if not self.leaf:
            self.children = []        

        # climbing data
        self.areas_list = [] # list of areas in order of big umbrella to small
        
        if self.leaf:
            # the below is not up to date
            self.title = "" # same as entry name
            self.type = "" # raw from the "Type:" mntproj field for now
            # after gathering might add more parsed types to this dict
            self.grade = "" # probably won't enumerate this
            self.FA = "" # raw from the "FA:" mntproj field for now
            self.FA_yr = 0 # parsed date if available
            self.FA_month = 0 # parsed date if available
            self.FAers = [] # list of climbers who got the FA if available
            self.shared_by = "" # mountain project submission info, could be cool to have


data_frame = pd.read_csv('Mountain_project_scrape_data.csv',index_col = 0)


##meta_df_columns = ['route_name','typeraw','graderaw','FAraw','sharedbyraw','leaf','Depth','Parent','Children','url']
##meta_data_frame = pd.DataFrame(columns=df_columns)

route_data = data_frame.loc[data_frame['leaf']].copy()

##route_data.reindex(index = range(len(route_data)))

# add some extra information tags to route_data
route_data['Trad'] = False
route_data['Sport'] = False
route_data['Aid'] = False
route_data['Boulder'] = False
route_data['Style'] = np.nan

route_data['FAyear'] = np.nan
route_data['numeric_grade'] = np.nan
route_data['img_url'] = np.nan

name_freq_dict = {}

st = dt.datetime.now()
try:
    for r in range(len(route_data)):
        crazy_index_shit = route_data.iloc[r].name
        if r % 100 == 0:
            print(r,' of ',len(route_data),' secs elapsed: ',(dt.datetime.now()-st).seconds)

        if type(route_data.iloc[r]['Title']) == str:
            words = route_data.iloc[r]['Title'].strip('""').split()
            for word in words:
                if word.lower() in name_freq_dict:
                    name_freq_dict[word.lower()] += 1
                else:
                    name_freq_dict[word.lower()] = 1


        ###
        found_FAyear = False
        FAraw = route_data.iloc[r]['FAraw']
        if type(FAraw) == str:
            for value in FAraw.split():
                if re.search('\d+', value):
                    if len(value) == 4:
                        try:
                            FAyear = int(value)
                            if FAyear > 1900 and FAyear < 2020:
                                found_FAyear = True
                                route_data.loc[crazy_index_shit,'FAyear'] = FAyear
                        except ValueError:
                            pass
                    pass
                
        if found_FAyear:
            Typeraw = route_data.iloc[r]['typeraw']
            if type(Typeraw) == str:
        ##        print(Typeraw.split())
                for t in Typeraw.split():
                    # the use of elif isn't really accurate, but makes later parsing easier
                    if 'Boulder' in t:
                        route_data.loc[crazy_index_shit,'Boulder'] = True
                        route_data.loc[crazy_index_shit,'Style'] = 'Boulder'
                    elif 'Trad' in t:
                        route_data.loc[crazy_index_shit,'Trad'] = True
                        route_data.loc[crazy_index_shit,'Style'] = 'Trad'
                    elif 'Sport' in t:
                        route_data.loc[crazy_index_shit,'Sport'] = True
                        route_data.loc[crazy_index_shit,'Style'] = 'Sport'
                    elif 'Aid' in t:
                        route_data.loc[crazy_index_shit,'Aid'] = True
                        route_data.loc[crazy_index_shit,'Style'] = 'Aid'
                    pass
                    

            got_grade = False   
            graderaw = route_data.iloc[r]['graderaw']
            if type(graderaw) == str:
                try:
                    YDS = graderaw.split(',')[0]
                    if route_data.iloc[r]['Boulder']:
                        numeric = int(re.sub(r"\D", "", YDS.split('V')[1]))
                        if numeric >= 0 and numeric < 18:
    ##                        print(numeric)
                            route_data.loc[crazy_index_shit,'numeric_grade'] = numeric
                    elif route_data.iloc[r]['Trad'] or route_data.iloc[r]['Sport']:
                        numeric = int(re.sub(r"\D", "", YDS.split('.')[1]))
                        if numeric >= 0 and numeric < 18:
    ##                        print(numeric)
                            route_data.loc[crazy_index_shit,'numeric_grade'] = numeric
                    got_grade = True
                except: pass

            # check if numeric worked
            if got_grade:
                try:
                    # find the url...
                    time.sleep(0.001) 
                    page = requests.get(url = route_data.loc[crazy_index_shit,'url'])
                    soup = BeautifulSoup(page.content, 'html.parser')
                    for el in soup.find(text=re.compile('url')).split(' '):
                        if '.jpg' in el:
                            s_ind = el.find('http')
                            stp_ind = el.find('.jpg')+4
                            url_temp = el[s_ind:stp_ind]

                    # wicked basic check
                    if len(url_temp) > 10: 
                        route_data.loc[crazy_index_shit,'img_url'] = url_temp
                except:
                    print('failed to retreive thumbnail url for some reason')
##        if r > 1000:
##            print('early stopping, debugging')
##            break
except:
    print('Terminated for some exception')
    
meta_df_name_freq = pd.DataFrame(list(name_freq_dict.items()),columns=['Word','Count'])
sorted_meta_df_name_freq = meta_df_name_freq.sort_values(by=['Count'],ascending=False)

# drop single character words
sorted_meta_df_name_freq = sorted_meta_df_name_freq.loc[sorted_meta_df_name_freq['Word'].str.len() != 1]
# drop two letter words...
sorted_meta_df_name_freq = sorted_meta_df_name_freq.loc[sorted_meta_df_name_freq['Word'].str.len() != 2]

ignore = ['the','of','a','and','in','on','no','de','it','for','el','to','i','&','or','le','-','sds','v1',
          'v2','v3','en','oh','que','red','blue']
for val in ignore:
    sorted_meta_df_name_freq = sorted_meta_df_name_freq[~sorted_meta_df_name_freq.Word.str.contains(val)]

##sorted_meta_df_name_freq.to_csv('mnt_proj_names_data.csv',index=False)
##print('Top N words')
##print(sorted_meta_df_name_freq.iloc[0:25])

# drop incomplete route data entries
route_data = route_data[route_data['numeric_grade'].notnull()]
route_data.to_csv('mnt_proj_route_data.csv',index=False)

