import json
from collections import defaultdict

import ndjson
import plotly.express as px
from dash import Dash, Input, Output, dcc, html


def visualize(x=["a", "b", "c"], y=[[1, 3, 2], [2, 3, 4]], title="sample figure", height=325):

    fig = px.line(
        x=x, y=y,
        title=title, height=height
    )

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


def read_data():
    # load from file-like objects
    with open('data/prefecture.ndjson') as f:
        data = ndjson.load(f)

    # cnt = []
    date2cnt = defaultdict(int)
    for d in data:
        date2cnt[d['date']] += d['count']
    return date2cnt.keys(), date2cnt.values()


if __name__ == '__main__':
    x, y = read_data()
    visualize(x, y, "Covid-19 Analysis")
