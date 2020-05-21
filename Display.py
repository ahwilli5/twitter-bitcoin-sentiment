#Connect.py should be runnning while TS5 goes

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
from datetime import date
import pandas as pd

date = date.today()

app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H4('Live Twitter Sentiment'),
        html.Div('live-update', children = []),
        dcc.Interval(id='interval-component', interval=3*1000, n_intervals=0),
        dcc.Graph(id='live-graph'),# animate=True),
        dcc.Input(id='sentiment_term', value='bitcoin', type='text')])
        )

@app.callback(Output('live-update', 'children'),
              [Input('interval-component', 'n_intervals')])

def update_graph_scatter(sentiment_term):
    try:
        conn = sqlite3.connect('twitter_{}.db'.format(date))
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 20", conn ,params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/2)).mean()

        df['date'] = pd.to_datetime(df['unix'],unit='ms')
        df.set_index('date', inplace=True)

        df = df.resample('1min').mean()
        df.dropna(inplace=True)
        X = df.index
        Y = df.sentiment_smoothed

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),
                                                    title='Term: {}'.format(sentiment_term))}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')



if __name__ == '__main__':
    app.run_server(debug=True)