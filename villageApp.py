#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PROGRAM: villageApp.py
#-----------------------------------------------------------------------
# Version 0.1
# 29 April, 2020
# patternizer AT gmail DOT com
# https://patternizer.github.io
#-----------------------------------------------------------------------

import csv
import sys
import os
from io import BytesIO
import http.client
import requests
import json
import webbrowser
from urllib.request import urlopen
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rc
plt.rcParams["font.family"] = "ariel"
from PIL import Image
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from plotly.subplots import make_subplots
import gunicorn
from flask import Flask
from random import randint
        
# --------------------------------------------------------------
# API KEYS
# --------------------------------------------------------------
#apikey_mo = <'your key'>
#apikey_ow = <'your key'>
keys = pd.read_csv('keys.txt', sep=',', delimiter=None)
apikey_mo = str(keys.key[0])
apikey_ow = str(keys.key[1])

# --------------------------------------------------------------

# --------------------------------------------------------------
# OpenWeatherMap (e.g. https://openweathermap.org/city/2648404)
# --------------------------------------------------------------
# https://api.openweathermap.org/data/2.5/onecall?appid={APIkey}

# Get (latitude, longitude) from IP address

response = requests.get('https://ipinfo.io/')
data = response.json()
(latitude, longitude) = data['loc'].split(',')
latitude = latitude.strip()
longitude = longitude.strip()

# Get weather with OpenWeather API

apiservice = 'https://api.openweathermap.org/data/2.5/onecall?'
url = apiservice + 'lat=' + latitude + '&' + 'lon=' + longitude + '&appid=' + apikey_ow
response = requests.get(url)
data = response.json() 

timezone = data['timezone']
daily = pd.DataFrame(data['daily'])
hourly = pd.DataFrame(data['hourly'])
timenow = pd.Timestamp.now().round('1s')
sunrise = pd.to_datetime(daily.sunrise[0] , unit='s')
sunset = pd.to_datetime(daily.sunset[0] , unit='s')
time = pd.to_datetime(hourly.dt.values, unit='s')
temp = round((hourly.temp - 273.15), 2).values
temp_feel = round((hourly.feels_like - 273.15), 2).values
dew_point = round((hourly.dew_point - 273.15), 2).values
temp_max = daily.temp[0]['max'] - 273.15
temp_min = daily.temp[0]['min'] - 273.15
wind_speed = hourly.wind_speed.values
wind_deg = hourly.wind_deg.values
pressure = hourly.pressure.values
humidity = hourly.humidity.values
clouds = hourly.clouds.values
rain = hourly.rain.values
mask = [rain[i] is not np.nan for i in range(len(rain))]
weather = hourly.weather.values
weathertemp = []
raintemp = []
for i in range(len(mask)):
    weathertemp.append(weather[i][0]['description'])
    if mask[i] is True:
        raintemp.append(rain[i]['1h'])
    else:
        raintemp.append(0.0)
rain = raintemp                 
weather = weathertemp      

print(rain)           

# ---------------------------------------------------------------------
# UKMO
# ---------------------------------------------------------------------
# http://datapoint.metoffice.gov.uk/public/data/{resource}?key={APIkey}

# Global 3-hourly, daily and hourly spot measurement data
client_id = '535de286-c5fb-478e-90be-d2278a7bcd61'
client_secret = 'oY8fY3gF2yM1xN3vQ0wX8fV5wV4lI2aV6wQ5hI1fW3bF0jC3tF'

conn = http.client.HTTPSConnection("api-metoffice.apiconnect.ibmcloud.com")
headers = {
    'x-ibm-client-id': client_id,
    'x-ibm-client-secret': client_secret,
    'accept': "application/json"
    }
   
apiservice = '/metoffice/production/v0/forecasts/point/'
product_name = 'hourly'   
#product_name = 'daily'   
excludeParameterMetadata = 'false'
includeLocationName = 'false'

url = apiservice + product_name + '?excludeParameterMetadata=' + excludeParameterMetadata + '&includeLocationName=' + includeLocationName + '&latitude=' + latitude + '&longitude=' + longitude

conn.request("GET", url, headers=headers)
res = conn.getresponse()
string = res.read().decode('utf-8')
json_obj = json.loads(string)
#df = json_normalize(json_obj)
#df = pd.DataFrame.from_dict(string, orient="index")
#df.parameters[0][0]['uvIndex']

with open("ukmo.txt", "w") as text_file:
    print(string, file=text_file)

# Get weather with UKMO API

apiservice = 'http://datapoint.metoffice.gov.uk/public/data/'

product_type = 'image/wxfcs/'
product_name = 'surfacepressure/'
product_format = 'xml/'
#product_type = 'layer/wxfcs/'
#product_name = 'all/'
#product_format = 'json/'

url = apiservice + product_type + product_name + product_format + 'capabilities?key=' + apikey_mo
response = requests.get(url)

if product_format == 'json/':

    # JSON

    data = response.json()

    print(data.keys())
    Rainfall = data['Layers']['Layer'][0]
    Cloud = data['Layers']['Layer'][1]
    CloudAndRain = data['Layers']['Layer'][2]
    Temperature = data['Layers']['Layer'][3]
    Pressure = data['Layers']['Layer'][4]

# XML
    
data = BytesIO(response.content)
    
try:    
    import xml.etree.cElementTree as ET    
except ImportError:    
    import xml.etree.ElementTree as ET    

tree = ET.parse(data)           
# tree.write('ukmo.xml', xml_declaration=True, encoding='utf-8')
root = tree.getroot()

for child in root.iter('*'):
    print(child.tag)
    
for elem in root:
   for subelem in elem:
      print(subelem.text)
      
#BWSurfacePressureChartList
#BWSurfacePressureChart
#DataDate
#ValidFrom
#ValidTo
#ProductURI
#DataDateTime
#ForecastPeriod
     
timestep=str(12) 
map = apiservice + product_type + product_name + 'gif?timestep=' + timestep + '&amp;key=' + apikey_mo
#webbrowser.open(map)

# ----------------
# URL table to CSV
# ----------------
import requests
from bs4 import BeautifulSoup
URL = "https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_by_continent_(data_file)"
result = requests.get(URL)
if result.status_code == 200:
    soup = BeautifulSoup(result.content, "html.parser")
table = soup.find('table',{'class':'wikitable sortable'})
new_table = []
for row in table.find_all('tr')[1:]:
    column_marker = 0
    columns = row.find_all('td')
    new_table.append([column.get_text() for column in columns])    
df = pd.DataFrame(new_table, columns=['ContinentCode','Alpha2','Alpha3','PhoneCode','Name'])
df['Name'] = df['Name'].str.replace('\n','')
# -----------------

#result = requests.get(map)
#if result.status_code == 200:
#    soup = BeautifulSoup(result.content, "html.parser")

#from urllib.request import Request, urlopen
#from urllib.error import URLError, HTTPError

#req = Request(map, headers={'User-Agent': 'XYZ/3.0'})
#web_byte = urlopen(req, timeout=10).read()
#webpage = web_byte.decode('utf-8')
    

#fig, ax  = plt.subplots()
#plt.plot(im)
#rgb_im = im.convert('RGB')
#r, g, b = rgb_im.getpixel((1, 1))
#print(r, g, b)
#plt.savefig('SurfacePressure.gif')


# ========================================================================
# App Deployment
# ========================================================================

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']
app = dash.Dash(__name__, server=server, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

# ========================================================================
# App Design
# ========================================================================
                 
# colors = {
#    'background': '#111111',
#    'text': '#7FDBFF'
#}          
#app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

app.layout = html.Div(children=[

    html.H1(children='VillageApp (Climate)',
    style={'padding' : '10px', 'width': '100%', 'display': 'inline-block'},
    ),

# ------------
    html.Div([     
    
    dcc.Dropdown(
        id = "input",
        options=[
            {'label': 'Gloucester', 'value': 'Gloucester'}
        ],
        value = 'Gloucester',
        style = {'padding' : '10px', 'width': '140px', 'fontSize' : '20px', 'display': 'inline-block'} ),

    ],
    style={'columnCount': 2}),
# ------------


# ------------
    html.Div([     

#    html.P([
#    html.H3(children='''Geolocation'''),    
#    html.Label('Time: ' + str(timenow)),    
#    html.Label('Weather: ' + str(weather[0])),        
#    html.Label('Sunrise: ' + str(sunrise)),
#    html.Label('Sunset: ' + str(sunset)),
#    html.Label('Latitude: ' + latitude + '°N'),
#    html.Label('Longitude: ' + longitude + '°W')],
#    style={'padding' : '10px', 'width': '50%', 'display': 'inline-block'}),

    html.P([
    html.H3(children='Geolocation')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="geolocation-graph", style = {'width': '90%'}),

    html.P([
    html.H3(children='Map')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="map-graph", style = {'width': '90%'}),
        
    ],
    style={'columnCount': 2}),
# ------------
       
# ------------    
    html.Div([          
    
    html.P([
    html.H3(children='48-hr Temperature [°C]')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="temperature-graph", style = {'width': '90%'}),

    html.P([
    html.H3(children='48-hr Pressure [hPa]')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="pressure-graph", style = {'width': '90%'}),

    
    html.P([
    html.H3(children='48-hr Weather')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="cloud-graph", style = {'width': '90%'}),

    html.P([
    html.H3(children='48-hr Wind [m/s,°]')],
    style = {'padding' : '10px', 'display': 'inline-block'}),
    dcc.Graph(id="wind-graph", style = {'width': '90%'}),

    ],
    style={'rowCount': 2, 'columnCount': 2}),
# ------------

# ------------
    html.Div([         
 
    html.P([
    html.H3(children='River Guages'),
    # UKEA: Hatherly Brook Guage    
    # UKEA: Gloucestershire flood warnings
    html.Iframe(src='https://gaugemap.blob.core.windows.net/gaugemapwidgets/1134-1233-3-300x446.html', style={'width':'300px', 'height':'446px'}),
    html.Iframe(src='https://gaugemap.blob.core.windows.net/gaugemapwidgets/33-36-3-300x446.html', style={'width':'300px', 'height':'446px'}),
    ],
    style={'padding' : '10px', 'width': '100%', 'display': 'inline-block'}
    ),

    html.P([
    html.H3(children='Flood Warnings'),
    html.Iframe(src='https://environment.data.gov.uk/flood-widgets/widgets/widget-Gloucestershire-horizontal.html', style={'width':'600px', 'height':'150px'}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Label(['Data source (48-hr hourly spot data): ', html.A('Open Weather Map', href='https://openweathermap.org/')]),    
    html.Label(['Data source (48-hr forecast maps): ', html.A('UK Met-Office Datapoint', href='http://datapoint.metoffice.gov.uk')]),    
    html.Label(['Data source (real-time satellite maps): ', html.A('Michael Taylor', href='https://patternizer.org/weather-station/')]),     
    html.Label(['Data source (river guages levels): ', html.A('GuageMap', href='https://www.gaugemap.co.uk')]),
    html.Label(['Data source (river flood warnings): ', html.A('UK Environmental Agency', href='https://flood-warning-information.service.gov.uk/warnings')]),
    html.Br(),
    html.Label(['Created by ', html.A('Michael Taylor', href='https://patternizer.github.io'),' using Plotly Dash']),
    ],
    style={'padding' : '10px', 'width': '100%', 'display': 'inline-block'}
    ),
    
    ],
    style={'columnCount': 2}),
# ------------
     
    ],
    style={'columnCount': 1})
    
##################################################################################################
# Callbacks
##################################################################################################

@app.callback(
    Output(component_id='geolocation-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):
    data = [
    go.Table(
            header=dict(values=['Parameter', 'Value'],
                line_color='darkslategray',
                fill_color='lightgrey',
                align='left'),
            cells=dict(values=[['Time now', 'Sunrise', 'Sunset', 'Latitude', 'Longitude'], # 1st column
                [str(timenow), str(sunrise), str(sunset), latitude, longitude]], # 2nd column
                line_color='darkslategray',
                fill_color='white',
                align='left')
            ),
    ]
    layout = go.Layout()
    return {'data': data, 'layout':layout} 

@app.callback(
    Output(component_id='map-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):
    cities = pd.read_json('city.list.json')
#    Index(['id', 'name', 'state', 'country', 'coord'], dtype='object')
    cities['lat'] = [ cities.coord[idx]['lat'] for idx in range(len(cities)) ]
    cities['lon'] = [ cities.coord[idx]['lon'] for idx in range(len(cities)) ]
    gb = cities[cities.country == 'GB']
    #idx = gb[gb.name == 'Gloucester'].index[0]
    #lat = gb.coord[idx]['lat']
    #lon = gb.coord[idx]['lon']
    df = gb[gb.name=='Gloucester']

    fig = px.scatter_mapbox(df, lat='lat', lon='lon', hover_name='name', hover_data=["country", 'name'],
                        color_discrete_sequence=["orange"], zoom=1)
    fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])
    fig.update_layout(margin={"r":10,"l":40,"b":60,"t":20})

    return fig

@app.callback(
    Output(component_id='temperature-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):
    data = [
        go.Scatter(x=time, y=temp, mode='lines+markers', name='2m-Temperature'),
        go.Scatter(x=time, y=temp_feel, mode='lines+markers', name = '2m-Temperature (feel)'),
        go.Scatter(x=time, y=dew_point, mode='lines+markers', name = 'Dew Point')
#       go.Shape(dict(type="line", x0=timenow, y0=np.min([temp.ravel(),temp_feel.ravel(),dew_point.ravel()]), x1=timenow, y1=np.max([temp.ravel(),temp_feel.ravel(),dew_point.ravel()]),line=dict(color="grey", width=1))
    ]
    layout = go.Layout(    
#        title = {'text' : 'Temperature in ' + value + ' (' + latitude + '°N,' + longitude + '°W) at ' + str(timenow), 'y': 0.85},
#        title = {'text' : 'Temperature in ' + value, 'y': 0.85},
#        xaxis_title = '', 
#        yaxis_title = '$\\text{Temperature } ^\\circ \\text{C}$',
        xaxis_showticklabels=False,
        legend_orientation="h", legend=dict(x=.02, y=0, bgcolor='rgba(205, 223, 212, .4)', bordercolor="Black"),
        margin=dict(r=10, l=40, b=60, t=20),                  
    )
    return {'data': data, 'layout':layout} 

@app.callback(
    Output(component_id='pressure-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):
    data = [
    go.Scatter(x=time, y=pressure, mode='lines+markers', name = 'Pressure')
    ]
    layout = go.Layout(    
        xaxis_showticklabels=False,
        legend_orientation="h", legend=dict(x=.02, y=0, bgcolor='rgba(205, 223, 212, .4)', bordercolor="Black"),
        margin=dict(r=10, l=40, b=60, t=20),                  
    )
    return {'data': data, 'layout':layout} 

@app.callback(
    Output(component_id='cloud-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):
    data = [
        go.Scatter(x=time, y=humidity, mode='lines+markers', name='Humidity', yaxis='y1'),
        go.Scatter(x=time, y=clouds, mode='lines+markers', name = 'Cloudiness', yaxis='y1'),
        go.Scatter(x=time, y=rain, mode='lines+markers', name = 'Precipitation', yaxis='y2')
    ]
    layout = go.Layout(    
        xaxis_showticklabels=False,
        yaxis1=dict(title='Cloudiness & Relative Humidity [%]'),
        yaxis2=dict(title='Precipitation [mm]',
        overlaying='y',
        side='right'),
        legend_orientation="h", legend=dict(x=.02, y=0, bgcolor='rgba(205, 223, 212, .4)', bordercolor="Black"),
        margin=dict(r=40, l=40, b=60, t=20),                  
    )
    return {'data': data, 'layout':layout}             
    
@app.callback(
    Output(component_id='wind-graph', component_property='figure'),
    [Input(component_id='input', component_property='value')]
    )
def update_graph(value):           
    data = [
        go.Scatterpolar(r=wind_speed, theta=wind_deg, mode='lines'),
    ]
    layout = go.Layout(    
        legend_orientation="h", legend=dict(x=.02, y=0.08, bgcolor='rgba(205, 223, 212, .4)', bordercolor="Black"),
        margin=dict(r=10, l=40, b=60, t=20),                  
    )
    return {'data': data, 'layout':layout}

##################################################################################################
# Run the dash app
##################################################################################################

if __name__ == "__main__":
 
    app.run_server(debug=True, use_reloader=False) 

# --------------------------------------------------------------
print('*** END')



