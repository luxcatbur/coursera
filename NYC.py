import sys
!{sys.executable} -m pip install geocoder
!{sys.executable} -m pip install geopy
!{sys.executable} -m pip install wget

import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')



from collections import defaultdict

venues = defaultdict(list)
categories = {}
coordinates = []

with open('data/NYC.txt') as nyc_data:
    for venue in nyc_data.readlines():
        data = venue.split('\t')
        
        # get the coordinates for the shop
        coordinates.insert(len(coordinates), [data[4], data[5]])
        
        # store the shop id and the user ids
        if data[1] not in venues:
            venues[data[1]].append(data[0])
        elif data[0] not in venues[data[1]]:
            venues[data[1]].append(data[0])
            
        # store the type of the shop and its id
        if data[1] not in categories:
            categories[data[1]] = data[3]
                
        
# example for 5 places and their visitors according to check-ins
for i in range(5):
    print(list(venues)[i], ": ", len(venues.get(list(venues)[i])), "  --> ", venues.get(list(venues)[i]))
    print()



column_names = ['VenueID', 'CategoryName', 'Visitor Count', 'Latitude', 'Longitude'] 

# instantiate the dataframe
venue_data = pd.DataFrame(columns=column_names)

venue_data

for idx in range(0, 2000):
    venue_id = list(venues)[idx]
    coords = list(coordinates)[idx]
    visitorCount = len(venues.get(venue_id))
    venue_type = categories.get(venue_id)


    venue_data = venue_data.append({ 'CategoryName': venue_type,
                                     'VenueID': venue_id,
                                     'Visitor Count': visitorCount,
                                     'Latitude': coords[0],
                                     'Longitude': coords[1]}, ignore_index=True)



print('The dataframe has {} venues with total of {} visitors.'.format(
        len(venue_data['VenueID'].unique()),
        sum(venue_data['Visitor Count'])
    )
)


import math as Math
def pointInCircle(lat0, lon0, r, lat, lon):  
    C = 40075.04                                               # Earth circumference
    A = 360*r/C                                                # semi-minor in north-south direction 
    B = A/Math.cos(Math.radians(float(lat0)));                 # semi-major in east-west direction
    return Math.pow((float(lat)-float(lat0))/A, 2) + Math.pow((float(lon)-float(lon0))/B, 2) < 1;

for idx in range(0, 2000):
    venue_id = list(venues)[idx]
    visitorCount = len(venues.get(venue_id))
    venue_type = categories.get(venue_id)
    
    if venue_type not in visitForCategories:
        visitForCategories[venue_type] = visitorCount
    else: 
        visitForCategories[venue_type] = visitForCategories[venue_type]+visitorCount
        
# visitForCategories
sorted_dict = sorted(visitForCategories.items(), key=lambda x: x[1], reverse=True)
for v in sorted_dict:
    if v[0] in someCategories:
        maxVisited = v[0]
        break
        
# category names with their visit number
sorted_dict = sorted(visitForCategories.items(), key=lambda x: x[1], reverse=True)
print(sorted_dict)

print()

# Max visited category
print("'" + maxVisited + "'", "is the most visited commercial category according to given data.")

mostVisitedCommercialPlace = {}
visited = []

r = 4              # kilometers
n = 2000           # venues

# maxVisited ='Food & Drink Shop'

for idx in range(0, n):
    coords = list(coordinates)[idx]
    if tuple(coords) in visited:
        continue
    visited.append(tuple(coords))

    storeCount = {}
    for tempVal in range(0, n):
        venue_id = list(venues)[idx]
        temp_coord = list(coordinates)[tempVal]
        venue_type = categories.get(venue_id)
    
        if pointInCircle(coords[0], coords[1], r, temp_coord[0], temp_coord[1]) and tuple(temp_coord) not in visited:
            
            visited.append(tuple(temp_coord))
            if venue_type not in storeCount:
                storeCount[venue_type] = 1
            else:
                storeCount[venue_type] = storeCount.get(venue_type)+1

        if maxVisited not in storeCount:
            mostVisitedCommercialPlace[tuple(coords)] = 0
        else: 
            mostVisitedCommercialPlace[tuple(coords)] = storeCount.get(maxVisited)
            
noneShops = []
sorted_dict = sorted(mostVisitedCommercialPlace.items(), key=lambda x: x[1], reverse=True)
print("Coordinates with number of " + maxVisited + " shops within", r, "kilometers according to", n, "venues.")
print()
for c in sorted_dict:
    print(c[0], ":", c[1])
    if c[1] < 2:
        noneShops.append(tuple(c[0]))
        
        
mostShopCoord = list(sorted_dict)[0][0]
del sorted_dict[0]
print("Coordinate that has the given specific shop the most: ", mostShopCoord)
from math import cos, asin, sqrt
nearNeighborhoods = []

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(data, v):
    return min(data, key=lambda p: distance(float(v[0]),float(v[1]),float(p[0][0]),float(p[0][1])) if p[0] not in nearNeighborhoods else 9999)

nearNeighborhoods
neighborhoods = {}
findNumOfPlaces = 2

centerNeighborhoodData = requests.get('https://api.foursquare.com/v2/venues/search?&client_id=JGGBRN5XODTLZGJOMCSWIQMRH1JLGJKPSFR10XNB2R5U25GR&client_secret=KWRAMLK2HOJBQ2XLICLKXRU3M4HOCC1U2VG4Y4OPP5JF03QX&v=20180605&ll={},{}&limit=1'.format(
    float(mostShopCoord[0]), float(mostShopCoord[1]))).json()

centerNeighborhood = centerNeighborhoodData['response']['venues'][0]['location']['formattedAddress']

while len(neighborhoods) != findNumOfPlaces:
    nearNeighborhoods.append(closest(list(sorted_dict), mostShopCoord)[0])
    lat = nearNeighborhoods[-1][0]
    lng = nearNeighborhoods[-1][1]
    url = 'https://api.foursquare.com/v2/venues/search?&client_id=JGGBRN5XODTLZGJOMCSWIQMRH1JLGJKPSFR10XNB2R5U25GR&client_secret=KWRAMLK2HOJBQ2XLICLKXRU3M4HOCC1U2VG4Y4OPP5JF03QX&v=20180605&ll={},{}&limit=1'.format(
    lat, lng)
    
    results = requests.get(url).json()
    
    try:
        neighborhoods[results['response']['venues'][0]['location']['neighborhood']] = tuple([lat,lng])
    except:
        continue

# print out the selected neighborhoods which are okay to get in. ( having no more than 1 shop within given range )
for ne in neighborhoods:
    print(ne)
import folium

mapit = folium.Map( location=[40.7128, -74.0060], zoom_start=11 )
latlon = []
neighboorhoodNames = []

for name, coords in neighborhoods.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
    latlon.append(tuple([float(coords[0]), float(coords[1])]))
    neighboorhoodNames.append(name)


# shop's coordinates with the most number of the given shop
folium.CircleMarker(
        [mostShopCoord[0], mostShopCoord[1]],
        radius=5,
        color='#ff0000',
        fill=True,
        fill_color='#ff0000',
        popup=folium.Popup('{}, NY'.format(centerNeighborhood), parse_html=True),
        parse_html=False,
        fill_opacity=0.7).add_to(mapit)


# label the potential neighborhoods
for c, n in zip(latlon, neighboorhoodNames):
    label = '{}, NY'.format(n)
    label = folium.Popup(label, parse_html=True)

    folium.Marker( location=[ c[0], c[1] ], fill_color='#43d9de', radius=8, popup=label, parse_html=False ).add_to( mapit )

mapit
