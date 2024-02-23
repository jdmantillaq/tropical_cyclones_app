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


tc_colors = {
    -1: '#3BDBE8',
    0: '#3185D3',
    1: '#F2E205',
    2: '#F28705',
    3: '#D90404',
    4: '#D84DDB',
    5: '#8B0088'}
color_other = 'gray'
#  -5        -4      -3      -2
custom_color_scale = ['black', 'gray', 'gray', 'gray',
                      '#3BDBE8', '#3185D3', '#F2E205', '#F28705',
                      '#D90404', '#D84DDB', '#8B0088']

size_marker_TC = {
    -1: 6,
    0: 6.5,
    1: 7,
    2: 7.5,
    3: 8,
    4: 8.5,
    5: 9,
}

season_list = tropical_cyclones.SEASON.unique()
# %%

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

load_figure_template("darkly")
slider_style = {"font-size": "18px"}
text_style = {"font-size": "20px"}


tab1_content = dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col([
                html.P("Select a Basin:"),
                dcc.Dropdown(id="dropdown_subbasin", options=subbasin_list,
                             className="dbc", value="CS"),
                html.P("Select a Season (year):"),
                dcc.Dropdown(id="dropdown_season", options=season_list,
                             className="dbc", value=season_list[-2]),
                html.P("Select a date range:"),
                dcc.DatePickerRange(id="date_picker", className='dbc'),
                html.P("Select a tropical cyclone:"),
                dcc.Dropdown(id="dropdown_tc", multi=True, className="dbc")


            ], width=3),
            dbc.Col([html.H4(id="title_fig1", style={'text-align': 'center'}),
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
# Tab1
# -----------------------------------------------------------------------------
@app.callback(
    [Output("date_picker", 'min_date_allowed'),
     Output("date_picker", 'max_date_allowed'),
     Output("date_picker", 'initial_visible_month'),
     Output("date_picker", 'start_date'),
     Output("date_picker", 'end_date'),
     Output("dropdown_tc", "options"),
     Output("dropdown_tc", "value")],
    [Input("dropdown_subbasin", "value"),
     Input("dropdown_season", "value")])
def set_country_options(subbasin, season):

    if subbasin is None:
        raise PreventUpdate
    if season is None:
        raise PreventUpdate

    # query = ((tropical_cyclones.SUBBASIN == subbasin) &
    #          (tropical_cyclones.SEASON ==
    #          season))
    # df = tropical_cyclones[query]

    df = tropical_cyclones.query('SUBBASIN == @subbasin and SEASON == @season')

    min_date_allowed = df.ISO_TIME.min()
    max_date_allowed = df.ISO_TIME.max()
    initial_visible_month = df.ISO_TIME.max()
    start_date = df.ISO_TIME.max() - pd.Timedelta('10day')
    end_date = df.ISO_TIME.max()

    tc_list = df.NUMBER.unique()

    return min_date_allowed, max_date_allowed, initial_visible_month, \
        start_date, end_date, tc_list, tc_list


@app.callback(
    [Output("title_fig1", 'children'),
     Output("graph_tab1", 'figure')],
    [Input("dropdown_subbasin", "value"),
     Input("dropdown_season", "value"),
     Input("dropdown_tc", "value"),])
def fig_map(subbasin, season, tc):
    if not all([subbasin, season, tc]):
        raise PreventUpdate

    # Define a list of colors for each trace
    colors = px.colors.qualitative.Plotly

    df = tropical_cyclones.query(
        'SUBBASIN == @subbasin and SEASON == @season and NUMBER in @tc')

    df['color_tc'] = df['USA_SSHS'].apply(
        lambda x: tc_colors.get(x, color_other))

    df['size'] = df['USA_SSHS'].apply(lambda x: size_marker_TC.get(x, 6))

    title = f'Tropical Cyclone Paths for Subbasin: {subbasin}, Season: {season}'
    figure = None
    for i, tc_i in enumerate(tc):
        df_i = df.query(f'NUMBER == {tc_i}')
        if i == 0:
            figure = px.scatter_mapbox(df_i, lat="LAT", lon="LON", zoom=4,
                                       mapbox_style="carto-positron",
                                       hover_data=['NAME', 'USA_WIND', 'USA_PRES',
                                                   'ISO_TIME'],
                                       height=800,
                                       color='USA_SSHS',
                                       color_continuous_scale=custom_color_scale,
                                       range_color=(-5, 5),
                                       size='size', size_max=7.5
                                       )

        else:
            figure.add_trace(px.scatter_mapbox(
                df_i, lat="LAT", lon="LON", zoom=4,
                hover_data=['NAME', 'USA_WIND', 'USA_PRES', 'ISO_TIME'],
                color='USA_SSHS',
                color_continuous_scale=custom_color_scale,
                range_color=(-5, 5), size='size', size_max=7.5,
            ).data[0])
    figure.update_traces(mode="markers+lines")
    return title, figure

# def fig_map(subbasin, season, tc):
#     if not all([subbasin, season, tc]):
#         raise PreventUpdate

#     colors = px.colors.qualitative.Plotly
#     tropical_cyclones_df = tropical_cyclones.query(
#         "SUBBASIN == @subbasin and SEASON == @season and NUMBER in @tc"
#     )

#     title = "Tropical Cyclone Paths for Subbasin: {}, Season: {}".format(subbasin, season)
#     figure = px.line_mapbox(tropical_cyclones_df, lat="LAT", lon="LON", zoom=4,
#                             height=800,)

#     # figure.add_traces(
#     #     px.line_mapbox(df_i, lat="LAT", lon="LON", hover_data=['NAME', 'STORM_SPEED', 'ISO_TIME'], color_discrete_sequence=[colors[i]]).data[0]
#     #     for i, df_i in tropical_cyclones_df.groupby("NUMBER")
#     # )
#     figure.update_traces(mode="markers+lines")

#     return title, figure


if __name__ == "__main__":
    app.run_server(port=8335, host='0.0.0.0')

# %%
basin = 'CS'
season = 2023
query = (tropical_cyclones.SUBBASIN == basin) & (
    tropical_cyclones.SEASON == season)
df = tropical_cyclones[query]
df.head()
df['color_tc'] = df['USA_SSHS'].apply(lambda x: tc_colors.get(x, color_other))


df['size'] = df['USA_SSHS'].apply(lambda x: size_marker_TC.get(x, 6))


px.scatter_mapbox(df, lat="LAT", lon="LON", zoom=4,
                  mapbox_style="carto-positron",
                  hover_data=['NAME', 'USA_WIND',
                              'USA_SSHS', 'USA_PRES',
                              'ISO_TIME'],
                  height=800,
                  color='USA_SSHS',  # Specify the column you want to map colors to
                  color_continuous_scale=custom_color_scale,
                  range_color=(-5, 5),
                  size='size',
                  size_max=4)

# %%
