# %%
"""
Created on 22-Feb-2024
@author: jdmantillaq
"""

import plotly.express as px
import pandas as pd
import numpy as np

from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

# %%

file_tc = '../data/ibtracs.since1980.list.v04r00.csv'
tropical_cyclones = pd.read_csv(file_tc, skiprows=[1])
tropical_cyclones.head()
tropical_cyclones['ISO_TIME'] = pd.to_datetime(tropical_cyclones['ISO_TIME'])


# %%
basin_list = [{'value': 'NA', 'label': 'North Atlantic'},
              {'value': 'EP', 'label': 'Eastern North Pacific'},
              {'value': 'WP', 'label': 'Western North Pacific'},
              {'value': 'NI', 'label': 'North Indian'},
              {'value': 'SI', 'label': 'South Indian'},
              {'value': 'SP', 'label': 'Southern Pacific'},
              {'value': 'SA', 'label': 'South Atlantic'}]

subbasin_list = [{'value': 'CS', 'label': 'Caribbean Sea'},
                 {'value': 'GM', 'label': 'Gulf of Mexico'},
                 {'value': 'CP', 'label': 'Central Pacific'},
                 {'value': 'BB', 'label': 'Bay of Bengal'},
                 {'value': 'AS', 'label': 'Arabian Sea'},
                 {'value': 'WA', 'label': 'Western Australia'},
                 {'value': 'EA', 'label': 'Eastern Australia'}]

season_list = tropical_cyclones.SEASON.unique()
# %%

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

load_figure_template("darkly")
slider_style = {"font-size": "18px"}
text_style = {"font-size": "12px"}


tab1_content = dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col([
                html.P("Select a Basin:"),
                dcc.Dropdown(id="dropdown_subbasin", options=subbasin_list,
                             className="dbc", value="CS"),
                html.P("Select a Season:"),
                dcc.Dropdown(id="dropdown_season", options=season_list,
                             className="dbc", value=season_list[-2]),
                html.P("Select a date range:"),
                dcc.DatePickerRange(id="date_picker", className='dbc')

            ], width=3),
            dbc.Col([html.H2(id="title_fig1", style={'text-align': 'center'}),
                     dcc.Graph(id="graph_tab1")], width=9)])
         ]
    )
)

tab2_content = dbc.Card(
    dbc.CardBody(
    )
)


app.layout = html.Div(
    [html.Div(
        className="header",
        children=[
            html.Div(
                className="div-info",
                children=[
                    html.H2(className="title",
                            children="Tropical Cyclones",
                            style={"padding": "10px"}),
                    html.Hr(),
                    dbc.Tabs([
                        dbc.Tab(tab1_content, label="Global Map",
                                tab_id="tab-1"),
                        dbc.Tab(tab2_content, label="Tab 2",
                                tab_id="tab-2"),],
                             id="tabs",
                             active_tab="tab-1",
                             )
                ],
            ),
        ],
    ),
    ], style=text_style
)


# -----------------------------------------------------------------------------
# Tab2
# -----------------------------------------------------------------------------
@app.callback(
    [Output("date_picker", 'min_date_allowed'),
     Output("date_picker", 'max_date_allowed'),
     Output("date_picker", 'initial_visible_month'),
     Output("date_picker", 'start_date'),
     Output("date_picker", 'end_date')],
    [Input("dropdown_subbasin", "value"),
     Input("dropdown_season", "value")])
def set_country_options(subbasin, season):
    query = ((tropical_cyclones.SUBBASIN == subbasin) &
             (tropical_cyclones.SEASON ==
             season))
    df = tropical_cyclones[query]

    min_date_allowed = df.ISO_TIME.min()
    max_date_allowed = df.ISO_TIME.max()
    initial_visible_month = df.ISO_TIME.max()
    start_date = df.ISO_TIME.max() - pd.Timedelta('10day')
    end_date = df.ISO_TIME.max()
    return min_date_allowed, max_date_allowed, initial_visible_month, \
        start_date, end_date


if __name__ == "__main__":
    app.run_server(port=8335, host='0.0.0.0')

# %%
basin = 'CS'
season = 2023
query = (tropical_cyclones.SUBBASIN == basin) & (
    tropical_cyclones.SEASON == season)
df = tropical_cyclones[query]
df
# %%
