from pymongo import MongoClient
import pandas as pd
import datetime
from datetime import datetime, timedelta
import dash
from dash import dcc
from dash import html
import plotly.express as px

URI="mongodb+srv://userdb:userdb1@atlascluster.akwsryc.mongodb.net/"
client = MongoClient(URI)
print("Connection Successful")
db= client.vip
room_col = db["sensor"]
outdoor_col = db["Room-456"]
room_data=room_col.find({},{'date':1,'CO2':1})
outdoor_data=outdoor_col.find({},{'date':1,'CO2':1})

df_room=pd.DataFrame(room_data)
df_room.rename(columns={'date':'datetime'},inplace = True)
df_room['time'] = df_room['datetime'].dt.strftime('%H:%M:%S')
df_room['date'] = df_room['datetime'].dt.date

df_outdoor=pd.DataFrame(outdoor_data)
df_outdoor.rename(columns={'date':'datetime'},inplace = True)
df_outdoor['time'] = df_outdoor['datetime'].dt.strftime('%H:%M:%S')
df_outdoor['date'] = df_outdoor['datetime'].dt.date

df_outdoor.sort_values(by=['datetime'])


app = dash.Dash(__name__)



app.layout = html.Div([
    html.Div(
        id='Most_recent_date',
        style={'margin-top': '20px'}  
    ),
    html.Div(
        id='top_CO2_value_room',
        style={'margin-top': '20px'} 
    ),
    html.Div(
        id='top_CO2_value_outdoor',
        style={'margin-top': '20px'} 
    ),
    dcc.Graph(
        id='co2-time-series',
        config={'displayModeBar': True}
    ),
    dcc.Graph(
        id='co2-time-series-1',
        config={'displayModeBar': True}
    ),
    dcc.Interval(
        id='interval-component',
        interval=10000,
        n_intervals=0
    ),
    dcc.Dropdown(id='dropdown',options=[
            {'label': 'All Time', 'value': 'AT'},
            {'label': 'Latest Hour', 'value': 'hour'},
            {'label': 'Latest Day', 'value': 'day'}
        ],
        value='AT',  
        style={'width': '50%'}),
])

@app.callback(
    [dash.dependencies.Output('co2-time-series', 'figure'),
     dash.dependencies.Output('Most_recent_date', 'children'),
     dash.dependencies.Output('top_CO2_value_room', 'children'),
     dash.dependencies.Output('co2-time-series-1', 'figure'),
     dash.dependencies.Output('top_CO2_value_outdoor', 'children')],
    dash.dependencies.Input('dropdown', 'value')
)
def update_graph(time):
    # Your graph updating logic here
    if time=='AT':
        fig = px.line(df_room, x='datetime', y='CO2', labels={'y': 'CO2'})
        #fig.add_trace(px.line(df_outdoor, x='datetime', y='CO2').data[0])
        fig_1 = px.line(df_outdoor, x='datetime', y='CO2', labels={'y': 'CO2'})
    if time=='hour':
        df_room_hour = df_room[df_room['datetime'] > df_room['datetime'].max() - pd.Timedelta(hours=1)]
        df_out_hour = df_outdoor[df_outdoor['datetime'] > df_outdoor['datetime'].max() - pd.Timedelta(hours=1)]
        fig = px.line(df_room_hour, x='time', y='CO2', labels={'y': 'CO2'})
        fig_1 = px.line(df_out_hour, x='time', y='CO2', labels={'y': 'CO2'})
    if time=='day':
        df_room_day = df_room[df_room['datetime'] > df_room['datetime'].max() - pd.Timedelta(days=1)]
        df_out_day = df_outdoor[df_outdoor['datetime'] > df_outdoor['datetime'].max() - pd.Timedelta(days=1)]
        fig = px.line(df_room_day, x='time', y='CO2', labels={'y': 'CO2'})
        fig_1 = px.line(df_out_day, x='time', y='CO2', labels={'y': 'CO2'})
    return fig, f"The most recent CO2 readings at {df_room['time'].iloc[-1]} on {df_room['date'].iloc[-1]}",f"Room-456 : {df_room['CO2'].iloc[-1]}",fig_1,f"Outdoors : {df_outdoor['CO2'].iloc[-1]}"

if __name__ == '__main__':
    app.run_server(debug=True)
