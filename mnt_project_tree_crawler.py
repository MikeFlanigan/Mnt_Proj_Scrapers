import requests
from bs4 import BeautifulSoup
import bs4
import time
import random
import datetime as dt
import os
import pickle
import re

root_url = "https://www.mountainproject.com/route-guide"

node_url = "https://www.mountainproject.com/area/"
leaf_url = 'https://www.mountainproject.com/route/'

# min and max seconds to pause for before scraping again
# this is to prevent predictable scraping and getting banned
sleep_max = 0.15
sleep_min = 0.01

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


pre_loaded_dict = False        
if os.path.isfile('mnt_proj_graph_dictionary.p'):
    with open('mnt_proj_graph_dictionary.p', 'rb') as fp:
        graph_dict = pickle.load(fp)
        pre_loaded_dict = True
        print('LOADED PRIOR GRAPH DICTIONARY')
else: graph_dict = {}

if os.path.isfile('mnt_proj_crawl_queue.p'):
    with open('mnt_proj_crawl_queue.p', 'rb') as fp:
        crawl_queue = pickle.load(fp)
        print('LOADED PRIOR CRAWL QUEUE')
else: crawl_queue = [] # initializing BFS search queue 

if not pre_loaded_dict:
    print('1 second pause, to prevent rapid pinging websites...')
    time.sleep(1)
    page = requests.get(url = root_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # kind of a fake node, but could make a cool vis
    graph_dict['Mountain Project']= mntNode(False,0)
    graph_dict['Mountain Project'].url = root_url
    
    # gather up the names of every root node ---- this only works for the initial route-guide page
    strong_divs = soup.findAll("strong")
    for div in strong_divs:
        if div.find('a') != None:
            name_tags = div.find_all('a',href=True)
            for item in name_tags:
                if node_url in item['href']:
                    # found a node                
                    area_name = item.text
                    if not area_name in graph_dict.keys():
                        graph_dict[area_name]= mntNode(False,1)
                        graph_dict[area_name].areas_list.append(area_name)
                        graph_dict[area_name].url = item['href']
                        graph_dict['Mountain Project'].children.append(area_name)
                        
                        crawl_queue.append(area_name) # add children to queue
                        print('Added ',area_name) 
                elif leaf_url in item['href']:
                    # found a leaf node
                    print('WOAHHHHHHHHHHHH unexpected')


'''
TODO items
- areas list doens't seem to be working. saving to many items
'''

# begin BFS through site. Making assumption this is a tree and no node has two parents

session_areas_count = 0
session_routes_count = 0

start_time = dt.datetime.now()
iters = 0
error_count = 0
while len(crawl_queue) > 0:
    try:
        print(' ')
        print('elapsed run time: ',(dt.datetime.now()-start_time).seconds,' seconds')

        # load the webpage
        sleep_time = random.random()*(sleep_max-sleep_min)+sleep_min
        time.sleep(sleep_time) # 1 second pause, to prevent rapid pinging websites...

        current_node = crawl_queue.pop(0)
        current_node_url = graph_dict[current_node].url

        print('searching: ',current_node)
        is_a_route = graph_dict[current_node].leaf
        
        page = requests.get(url = current_node_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if is_a_route:
            # gather and log route data
            graph_dict[current_node].title = current_node

            graph_dict[current_node].type = soup.find('td',text = re.compile('Type:')).find_next('td').text.strip()
            graph_dict[current_node].FA = soup.find('td',text = re.compile('FA:')).find_next('td').text.strip()

            shared_by_string = ''
            temp = soup.find('td',text = re.compile('Shared By:')).find_next('td').text.strip()
            for word in temp.split():
                shared_by_string += word
                shared_by_string += ' '
            graph_dict[current_node].shared_by = shared_by_string
            
            grade_string = ''
            grade_info = soup.find('h2',{'class':'inline-block mr-2'}).contents
            index = 0
            for i in grade_info:
                if type(i) == bs4.element.Tag:
                    grade_string += i.text.strip()
                if type(i) == bs4.element.NavigableString:
                    if len(i.strip()) == 0:
                        if index != len(grade_info): grade_string += ', '
                    else:
                        grade_string += i.strip()
                        if index != len(grade_info): grade_string += ', '
                index += 1
                        
            graph_dict[current_node].grade = grade_string

            print('Cataloged route: ',current_node)
            
            session_routes_count += 1
            
        else: # find children, which could be routes or areas
            session_areas_count += 1
            left_nav_items = soup.find_all('div',{'class':'lef-nav-row'})
            for entry in left_nav_items:
                entry_url = entry.find('a',href=True)
                if (node_url in entry_url['href']) or (leaf_url in entry_url['href']):
                    entry_name = entry_url.text
                    if not entry_name in graph_dict.keys():
                        graph_dict[entry_name]= mntNode(leaf_url in entry_url['href'],graph_dict[current_node].depth+1)
                        graph_dict[entry_name].url = entry_url['href']
                        graph_dict[entry_name].parent = current_node
                        graph_dict[current_node].children.append(entry_name)
                        
                        graph_dict[entry_name].areas_list = graph_dict[current_node].areas_list
                        if node_url in entry_url['href']:
                            graph_dict[entry_name].areas_list.append(entry_name)
                            
                        crawl_queue.append(entry_name) # add children to queue
                        print('Added ',entry_name)
                else:
                    print('EROROROROER unexpected, not route or area')

            if len(left_nav_items) == 0: # only have routes under this page
                for entry_url in soup.find_all('a',href=True):
                    if leaf_url in entry_url['href']:
                        entry_name = entry_url.text
                        if (not entry_name in graph_dict.keys()) and (not '\n' in entry_name):
                            graph_dict[entry_name]= mntNode(True,graph_dict[current_node].depth+1)
                            graph_dict[entry_name].url = entry_url['href']
                            graph_dict[entry_name].areas_list = graph_dict[current_node].areas_list
                            graph_dict[entry_name].parent = current_node
                            graph_dict[current_node].children.append(entry_name)
                    
                            crawl_queue.append(entry_name) # add children to queue
                            print('Added ',entry_name)

                    
                        
        print('session areas count: ',session_areas_count,' routes count: ',session_routes_count)
        
        # find children areas of node... # really need to detect if it is an area or route
        # seems to be an <h3>Routes in ....</h3> vs <h3>Areas in ...</h3>
        # whatever children the current node has
        # check they aren't in the graph already, if not
        # append them to queue --- and substantiate and make each one

        if False:
            #if iters > 4000:
            print('early stop due to testing iters limit')
            print(' ')
            print(len(graph_dict.keys()),' routes/areas catalogued so far')
            with open('mnt_proj_graph_dictionary.p', 'wb') as fp: pickle.dump(graph_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)
            with open('mnt_proj_crawl_queue.p', 'wb') as fp: pickle.dump(crawl_queue, fp, protocol=pickle.HIGHEST_PROTOCOL)
            break
        iters += 1

    except KeyboardInterrupt:
        print('stopped due to keyboard interrupt')
        break

    except:
        print('unknown error')
        time.sleep(30) # in case it was internet connection
        error_count += 1
        if error_count > 20:
            print('stopped due to excesive error count')
            break

    

print(' ')
if len(crawl_queue) == 0: print('terminated due to finishing the crawl queue!')
with open('mnt_proj_graph_dictionary.p', 'wb') as fp: pickle.dump(graph_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)
with open('mnt_proj_crawl_queue.p', 'wb') as fp: pickle.dump(crawl_queue, fp, protocol=pickle.HIGHEST_PROTOCOL)
    


