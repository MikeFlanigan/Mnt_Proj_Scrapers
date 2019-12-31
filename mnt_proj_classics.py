import sys
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


csv_output_fname = 'classic_climbs.csv'
URL = 'https://www.mountainproject.com/area/classics/105744225/flagstaff'
##URL = 'https://www.mountainproject.com/area/classics/105840796/wild-iris?type=all'
##URL = 'https://www.mountainproject.com/area/classics/105744222/boulder-canyon'
##URL = 'https://www.mountainproject.com/area/classics/105833388/yosemite-valley?type=boulder'

if(len(sys.argv) > 1):
    URL = sys.argv[1]
    print('Searching page URL: ')
else:
    print('No URL entered by user, using default URL: ')
    
print(URL)
time.sleep(0.9)

classicsDF = pd.DataFrame(columns=['Climb', 'Area', 'Stars', 'Grade', 'Type'])


page = requests.get(url = URL)
soup = BeautifulSoup(page.content, 'html.parser')

classics = soup.findAll('div',{'class':'text-truncate'}) # contains all the names...



ii = 0
for climb in classics:
    classicsDF.loc[ii,'Climb'] = climb.find('strong').get_text()

    if ii == 0: # fill in just the stars and the grade for the first element
        BSelement = climb.findPrevious('div')
        for nn in range(2):
            if nn == 0:
                classicsDF.loc[ii,'Stars'] = len(BSelement.findAll('img'))
                if 'Half' in BSelement.findAll('img')[-1]['src'].split('/')[-1]:
                    classicsDF.loc[ii,'Stars'] -= 0.5
            if nn == 1:
                classicsDF.loc[ii,'Grade'] = BSelement.find('span').get_text().strip()
            BSelement = BSelement.findPrevious('div')

    if ii + 1 < len(classics):
        BSelement = climb.findNext('div')
        for nn in range(5):
            if nn == 0:
                classicsDF.loc[ii,'Type'] = BSelement.get_text().strip()
            elif nn == 3:
                classicsDF.loc[ii,'Area'] = BSelement.get_text().strip()
            elif nn == 4:
                classicsDF.loc[ii+1,'Grade'] = BSelement.find('span').get_text().strip()
                classicsDF.loc[ii+1,'Stars'] = len(BSelement.findAll('img'))
                if 'Half' in BSelement.findAll('img')[-1]['src'].split('/')[-1]:
                    classicsDF.loc[ii+1,'Stars'] -= 0.5
            else:
                pass
            BSelement = BSelement.findNext('div')
    
    ii += 1


# lololololol
for i in range(len(classicsDF)):
    hard_shitz = ['5.14','5.15','V9','V10','V11','V12']
    for g in hard_shitz:
        if g in classicsDF.loc[i,'Grade']:
            if 'V' in classicsDF.loc[i,'Grade']:
                classicsDF.loc[i,'Grade'] = 'v... no way bro ;) ('+classicsDF.loc[i,'Grade']+')'
            else:
                classicsDF.loc[i,'Grade'] = '5... no way bra ;) ('+classicsDF.loc[i,'Grade']+')'
                
classicsDF.to_csv(csv_output_fname,index=False)




