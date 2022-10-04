import json
from collections import defaultdict
from datetime import datetime

import ndjson
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots


def visualize(fig):

    app = Dash(__name__)

    app.layout = html.Div([
        html.H4('Displaying figure structure as JSON'),
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
        Output("structure", "children"),
        Input("graph", "figure"))
    def display_structure(fig_json):
        return json.dumps(fig_json, indent=2)

    app.run_server(debug=True)


def read_vaccination(prefecture_id):
    with open('data/prefecture.ndjson') as f:
        data = ndjson.load(f)

    date2cnt = defaultdict(int)
    for d in data:
        if d["prefecture"] != prefecture_id:
            continue
        date2cnt[d['date']] += d['count']

    return pd.concat([pd.to_datetime(pd.Series(date2cnt.keys(), name="date")), pd.Series(
        date2cnt.values(), name="vaccination")], axis=1)


def read_death(prefecture):
    df = pd.read_csv('data/exdeath-japan-observed.csv')
    df['week_ending_date']
    df['week_ending_date'] = pd.to_datetime(
        df['week_ending_date'], format="%d%b%Y")  # 17feb2013
    df = df[(df['prefecture_EN'] == prefecture) & (df['week_ending_date'] > "2021-03-01")].loc[:,
                                                                                               ('week_ending_date', 'Observed')]
    return df.loc[:, ('week_ending_date', 'Observed')].rename(columns={'week_ending_date': 'date', 'Observed': 'death'})


def get_prefecture_id(prefecture_name):
    '''Get prefecture id from data/exdeath-japan-observed.csv.
    ToDo: use the prefecture list for master data.
    '''
    df = pd.read_csv('data/exdeath-japan-observed.csv')
    return df[df['prefecture_EN'] == prefecture_name].head(1)['prefecture_id'].iloc[0]


if __name__ == '__main__':
    prefecture = "Tokyo"

    # make data
    prefecture_id = get_prefecture_id(prefecture)
    df_death = read_death(prefecture)
    df_vaccination = read_vaccination(f"{prefecture_id:2d}")
    df = pd.concat([df_death, df_vaccination])

    # make fig
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
    fig.update_layout(title_text=f"Vaccination & Death ({prefecture})")

    # visualize
    visualize(fig)
