import json
import random
import time
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from time import perf_counter
from tkinter import ALL

import ndjson
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

prefecture_master = pd.read_csv('data/prefecture_master.csv').loc[:, ('prefecture_id', 'prefectureJP')].rename(
    columns={'prefecture_id': 'value', 'prefectureJP': 'label'}).T.to_dict().values()

ALL_JAPAN_ID = 48
START_DATE = "2020-01-01"


def run():

    df = load_data()
    df = df[df['prefecture_id'] == ALL_JAPAN_ID]

    fig = make_fig(df, "")

    app = Dash(__name__)
    app.layout = html.Div([
        html.H4('Covid-19 Analysis'),
        dcc.Dropdown(
            options=list(prefecture_master),
            value=ALL_JAPAN_ID,
            id='demo-dropdown'),
        html.Div(id='dd-output-container'),
        dcc.Graph(id="graph", figure=fig),
        dcc.Clipboard(target_id="structure"),
        html.Pre(
            id='structure',
            style={
                'border': 'thin lightgrey solid',
                'overflowY': 'scroll',
                'height': '275px'
            }
        ),
    ])

    @app.callback(
        Output('graph', 'figure'),
        Input('demo-dropdown', 'value')
    )
    def update_graph(value):
        if value is None:
            return
        print(f"update_graph {value}")
        df = load_data()
        df = df[df['prefecture_id'] == int(value)]
        fig = make_fig(df, f"Vaccination & Death")
        fig.update_layout(transition_duration=0)
        return fig

    @app.callback(
        Output("structure", "children"),
        Input("graph", "figure"))
    def display_structure(fig_json):
        return json.dumps(fig_json, indent=2)

    app.run_server(debug=True)


def read_vaccination():
    df = pd.read_json('data/prefecture.ndjson', lines=True)
    df.astype({'prefecture': 'int32'}, copy=False)
    df = df.loc[:, ('date', 'count', 'prefecture')]
    df = df.groupby(['date', 'prefecture']).sum().reset_index()
    daily_all_df = df.groupby(['date']).sum()
    daily_all_df['prefecture'] = ALL_JAPAN_ID
    daily_all_df.reset_index(inplace=True)
    df = pd.concat([df, daily_all_df], ignore_index=True)
    return df.rename(columns={'count': 'vaccination', 'prefecture': 'prefecture_id'})


def read_death():
    df = pd.read_csv('data/exdeath-japan-observed.csv')
    df['week_ending_date'] = pd.to_datetime(
        df['week_ending_date'], format="%d%b%Y")  # 17feb2013
    df = df[(df['week_ending_date'] > START_DATE)]
    return df.loc[:, ('week_ending_date', 'Observed', 'prefecture_id')].rename(columns={'week_ending_date': 'date', 'Observed': 'death'})


def get_prefecture_id(prefecture_name):
    '''Get prefecture id from data/exdeath-japan-observed.csv.
    ToDo: use the prefecture list for master data.
    '''
    df = pd.read_csv('data/exdeath-japan-observed.csv')
    return df[df['prefecture_EN'] == prefecture_name].head(1)['prefecture_id'].iloc[0]


@lru_cache
def load_data():
    print("loading data")
    t = time.time()
    df_death = read_death()
    print(f"df_death {df_death.shape}")
    df_vaccination = read_vaccination()
    print(f"df_vaccination {df_vaccination.shape}")
    df = pd.concat([df_death, df_vaccination])
    print(
        f"finished loading. time: {(time.time() - t):.2f}, "
        f"df_vaccination: {df_vaccination.shape}, "
        f"df_death: {df_death.shape}, "
        f"df: {df.shape}"
    )
    return df


def make_fig(df, title):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['death'],
            name='death'),
        secondary_y=False)

    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['vaccination'],
            name="vaccination"),
        secondary_y=True)
    fig.update_layout(
        title_text=title)
    return fig


if __name__ == '__main__':
    run()
