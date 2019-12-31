import time
import random
import datetime as dt
import os
import pickle
import re
import numpy as np
import pandas as pd


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
            self.title = "" # same as entry name
            self.type = "" # raw from the "Type:" mntproj field for now
            # after gathering might add more parsed types to this dict
            self.grade = "" # probably won't enumerate this
            self.FA = "" # raw from the "FA:" mntproj field for now
            self.FA_yr = 0 # parsed date if available
            self.FA_month = 0 # parsed date if available
            self.FAers = [] # list of climbers who got the FA if available
            self.shared_by = "" # mountain project submission info, could be cool to have


dictionary_fname = 'mnt_proj_graph_dictionary-final.p'

with open(dictionary_fname, 'rb') as fp:
    graph_dict = pickle.load(fp)
    pre_loaded_dict = True
    print('LOADED PRIOR GRAPH DICTIONARY')

df_columns = ['Title','typeraw','graderaw','FAraw','sharedbyraw','leaf','Depth','Parent','Children','url']
data_frame = pd.DataFrame(columns=df_columns)

keys = list(graph_dict.keys())
for i in range(len(graph_dict)):
    graph_dict[keys[i]].areas_list = []
    if i%100 == 0: print(i,' of ',len(graph_dict))

    if graph_dict[keys[i]].leaf:
        child = np.nan
        PicType = graph_dict[keys[i]].type
        PicGrade = graph_dict[keys[i]].grade
        PicFA = graph_dict[keys[i]].FA
        PicSharedby = graph_dict[keys[i]].shared_by
    else:
        child = graph_dict[keys[i]].children
        PicType = np.nan
        PicGrade = np.nan
        PicFA = np.nan
        PicSharedby = np.nan
        
    data_frame.loc[i] = [keys[i], PicType, PicGrade, PicFA,
                         PicSharedby, graph_dict[keys[i]].leaf,
                         graph_dict[keys[i]].depth, graph_dict[keys[i]].parent, child,
                         graph_dict[keys[i]].url]



