import json
import random
import time
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from time import perf_counter
from tkinter import ALL
from turtle import width

import ndjson
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

pd.options.plotting.backend = "plotly"


prefecture_master_df = pd.read_csv('data/prefecture_master.csv')
prefecture_master = prefecture_master_df.loc[:, ('prefecture_id', 'prefectureJP')].rename(
    columns={'prefecture_id': 'value', 'prefectureJP': 'label'}).T.to_dict().values()
prefecture_id2name = prefecture_master_df.loc[:,
                                              ('prefecture_id', 'prefecture_EN')].set_index('prefecture_id').to_dict()['prefecture_EN']
ALL_JAPAN_ID = 48
START_DATE = "2017-01-01"
YEARS_FOR_DEATH_RATE = ["2019", "2020", "2021"]


def run():

    df = load_data()
    fig = make_fig(df)

    df_death = read_death_rate()
    fig_death = make_fig_from_death(df_death)

    app = Dash(__name__)
    app.layout = html.Div([
        html.H2('Covid-19 Analysis'),
        html.H3('Vaccination & Death'),
        html.H5('Prefecture'),
        dcc.Dropdown(
            options=list(prefecture_master),
            value=ALL_JAPAN_ID,
            id='prefecture-dropdown'),
        html.H5('Death Type'),
        dcc.Dropdown(
            options=[{"value": 1, "label": "Death"},
                     {"value": 2, "label": "Death Exceeded"}],
            value=2,
            id='death-dropdown'),

        html.Div(id='dd-output-container'),
        dcc.Graph(id="graph", figure=fig),

        html.H3('Death Rate'),
        html.H5('Gender'),
        dcc.Dropdown(
            options=[{"value": "male", "label": "Male"},
                     {"value": "female", "label": "Female"}],
            value="male",
            id='gender-dropdown'),
        html.Div(id='death-rate-per-age'),
        dcc.Graph(id='graph-death-rate-per-age', figure=fig_death),
    ])

    @app.callback(
        Output('graph', 'figure'),
        [Input('prefecture-dropdown', 'value'),
         Input('death-dropdown', 'value')]
    )
    def update_graph(prefecture_id, death_type):
        if prefecture_id is None:
            return
        print(f"update_graph {prefecture_id=}, {death_type=}")
        df = load_data()
        fig = make_fig(df, int(prefecture_id), int(death_type))
        fig.update_layout(transition_duration=0)
        return fig

    @app.callback(
        Output('graph-death-rate-per-age', 'figure'),
        [Input('gender-dropdown', 'value')]
    )
    def update_graph(gender):
        if gender is None:
            return
        df = read_death_rate()
        fig = make_fig_from_death(df, gender)
        fig.update_layout(transition_duration=0)
        return fig

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


def read_estimated_death():
    df = pd.read_csv('data/exdeath-japan-estimates.csv')
    df['week_ending_date'] = pd.to_datetime(
        df['week_ending_date'], format="%d%b%Y")  # 17feb2013
    df = df[(df['week_ending_date'] > START_DATE)]
    return df.rename(columns={'week_ending_date': 'date'})


def read_death_rate():
    all_df = None
    for year in YEARS_FOR_DEATH_RATE:
        year_df = None
        for gender in ["male", "female"]:
            df = pd.read_csv(
                f"data/manual_data/{year}_death_rate_for_age_{gender}.csv", sep="\t")
            df['gender'] = gender
            df.rename(columns={
                      'death_rate': f"{year}"}, inplace=True)

            if year_df is None:
                year_df = df
            else:
                year_df = pd.concat([year_df, df])
        if all_df is None:
            all_df = year_df
        else:
            all_df = pd.merge(all_df, year_df)
    return all_df


@lru_cache
def load_data():
    print("loading data")
    t = time.time()
    df_death = read_estimated_death()
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


def make_fig(df, prefecture_id=ALL_JAPAN_ID, death_type=1):
    prefecture_name = prefecture_id2name[prefecture_id]
    df = df[(df['prefecture_id'] == prefecture_id)
            | (df['prefecture_id'].isnull())]
    df[f"{prefecture_name}_Exceeded"] = df[f"{prefecture_name}_Observed"] - \
        df[f"{prefecture_name}_Estimated"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if death_type == 1:
        death_data = [f"{prefecture_name}_95Lower", f"{prefecture_name}_95Upper",
                      f"{prefecture_name}_Observed", f"{prefecture_name}_Estimated"]
    elif death_type == 2:
        death_data = [f"{prefecture_name}_Exceeded"]
    for y in death_data:
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df[y],
                name=f"death_{y}"),
            secondary_y=False)

    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['vaccination'],
            name="vaccination"),
        secondary_y=True)
    fig.update_layout(
        title_text=f"Vaccination & Death ({prefecture_name})")

    return fig


def make_fig_from_death(df, gender="male"):
    df = df[df['gender'] == gender]
    df = df[(df['age'] > 30) & (df['age'] < 70)]
    fig = px.line(
        df,
        x="age",
        y=YEARS_FOR_DEATH_RATE,
        title='Age & Death Rate',
        labels={"value": "death rate"}
    )
    return fig


if __name__ == '__main__':
    run()
