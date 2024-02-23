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
import os
import requests


# %%

file_tc = '../data/ibtracs.since1980.list.v04r00.csv'
url = 'https://www.ncei.noaa.gov/data/'international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.since1980.list.v04r00.csv'

# Check if the file exists
if not os.path.exists(file_tc):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_tc), exist_ok=True)

    # Download the file
    response = requests.get(url)
    with open(file_tc, 'wb') as f:
        f.write(response.content)
    print("File downloaded successfully.")
else:
    print("File already exists.")


# %%
columns_to_import = ['SID', 'SEASON', 'NUMBER', 'BASIN', 'SUBBASIN',
                     'NAME', 'ISO_TIME', 'NATURE', 'LAT', 'LON', 'USA_WIND',
                     'USA_PRES']

tropical_cyclones = pd.read_csv(
    file_tc, skiprows=[1], usecols=columns_to_import)
tropical_cyclones = pd.read_csv(file_tc, skiprows=[1])
tropical_cyclones['ISO_TIME'] = pd.to_datetime(tropical_cyclones['ISO_TIME'])
tropical_cyclones['BASIN'] = tropical_cyclones['USA_ATCF_ID'].apply(
    lambda x: x[:2])
tropical_cyclones['TC_ID'] = tropical_cyclones['USA_ATCF_ID'].apply(
    lambda x: x[2:4])

# %%


# %%
basin_list = {
    'AL': 'North Atlantic',
    'EP': 'East Pacific',
    'WP': 'West Pacific',
    'IO': 'North Indian',
    'SI': 'South Indian',
    'SP': 'South Pacific',
    'SL': 'South Atlantic',
    'SH': 'Southern Hemisphere',
    'CP': 'Central Pacific',
    'AS': 'Arabian Sea',
    'BB': 'Bay of Bengal'
}


subbasin_list = {'CS': 'Caribbean Sea',
                 'GM': 'Gulf of Mexico',
                 'CP': 'Central Pacific',
                 'BB': 'Bay of Bengal',
                 'AS': 'Arabian Sea',
                 'WA': 'Western Australia',
                 'EA': 'Eastern Australia'}


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

category_dict = {
    -5: "Unknown",
    -4: "Post-tropical",
    -3: "Disturbance",
    -2: "Subtropical",
    -1: "Tropical depression",
    0: "Tropical storm",
    1: "Category 1",
    2: "Category 2",
    3: "Category 3",
    4: "Category 4",
    5: "Category 5"
}

season_list = tropical_cyclones.SEASON.unique()
# %%

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

load_figure_template("darkly")
slider_style = {"font-size": "16px"}
text_style = {"font-size": "20px"}


tab1_content = dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col([
                html.P("Select a Basin:"),
                dcc.Dropdown(id="dropdown_basin",
                             options=[{'value': i, 'label': j} for i, j
                                      in basin_list.items()],
                             className="dbc", value="AL"),
                html.P("Select a Season (year):"),
                dcc.Dropdown(id="dropdown_season", options=season_list,
                             className="dbc", value=season_list[-2]),
                html.P("Select a date range:"),
                dcc.DatePickerRange(id="date_picker", className='dbc',
                                    display_format='DD/MM/YYYY',
                                    start_date_placeholder_text='DD/MM/YYYY'),
                html.P("Select a disturbance:"),
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
    [Input("dropdown_basin", "value"),
     Input("dropdown_season", "value")])
def set_country_options(basin, season):
    if basin is None:
        raise PreventUpdate
    if season is None:
        raise PreventUpdate

    # query = ((tropical_cyclones.SUBBASIN == subbasin) &
    #          (tropical_cyclones.SEASON ==
    #          season))
    # df = tropical_cyclones[query]

    df = tropical_cyclones.query('BASIN == @basin and SEASON == @season')
    min_date_allowed = pd.to_datetime(f'{season}-01-01')
    max_date_allowed = pd.to_datetime(f'{season}-12-31')
    initial_visible_month = df.ISO_TIME.max()
    start_date = df.ISO_TIME.min()
    end_date = df.ISO_TIME.max()

    disturbance_list = df.TC_ID.unique()

    return min_date_allowed, max_date_allowed, initial_visible_month, \
        start_date, end_date, disturbance_list, disturbance_list


@app.callback(
    [Output("dropdown_tc", "options", allow_duplicate=True),
     Output("dropdown_tc", "value", allow_duplicate=True)],
    [Input("dropdown_basin", "value"),
     Input("dropdown_season", "value"),
     Input("date_picker", "start_date"),
     Input("date_picker", "end_date")], prevent_initial_call=True)
def set_disturbance_options(basin, season, start_date, end_date):
    if not all([basin, season, start_date, end_date]):
        raise PreventUpdate
    df = tropical_cyclones.query('BASIN == @basin and SEASON == @season')
    df = df.loc[df["ISO_TIME"].between(start_date, end_date)]
    disturbance_list = df.TC_ID.unique()
    return disturbance_list, disturbance_list


@app.callback(
    [Output("title_fig1", 'children'),
     Output("graph_tab1", 'figure')],
    [Input("dropdown_basin", "value"),
     Input("dropdown_season", "value"),
     Input("dropdown_tc", "value"),
     Input("date_picker", "start_date"),
     Input("date_picker", "end_date")],
)
def fig_map(basin, season, disturbance, start_date, end_date):
    if not all([basin, season, disturbance, start_date, end_date]):
        raise PreventUpdate

    df = tropical_cyclones.query(
        'BASIN == @basin and SEASON == @season and TC_ID in @disturbance')

    df = df.loc[df["ISO_TIME"].between(start_date, end_date)]

    df['color_tc'] = df['USA_SSHS'].apply(
        lambda x: tc_colors.get(x, color_other))

    df['SIZE'] = df['USA_SSHS'].apply(lambda x: size_marker_TC.get(x, 6))
    df['CAT'] = df['USA_SSHS'].apply(lambda x: category_dict.get(x))

    title = f'{season}-{basin_list[basin]} hurricane season'
    figure = None
    hover_data = ['NAME', 'LAT',  'LON', 'CAT',
                  'USA_WIND', 'USA_PRES', 'ISO_TIME']

    hover_template = \
        "<span style='font-size: 16px;'><b>Name:</b> %{customdata[0]}</span><br>" + \
        "<span style='font-size: 16px;'><b>Lat:</b> %{customdata[1]:.2f}, </span>" + \
        "<span style='font-size: 16px;'><b>Lon:</b> %{customdata[2]:.2f}</span><br>" + \
        "<span style='font-size: 16px;'><b>Type:</b> %{customdata[3]}</span><br>" + \
        "<span style='font-size: 16px;'><b>Max Wind Speed:</b> %{customdata[4]} knots</span><br>" + \
        "<span style='font-size: 16px;'><b>Pressure:</b> %{customdata[5]} mb</span><br>" + \
        "<span style='font-size: 16px;'><b>Time:</b> %{customdata[6]}</span><extra></extra>"

    for i, dist_i in enumerate(disturbance):
        df_i = df[df.TC_ID == dist_i]
        if i == 0:
            figure = px.scatter_mapbox(df_i, lat="LAT", lon="LON", zoom=4,
                                       mapbox_style="carto-positron",
                                       hover_data=hover_data,
                                       height=800,
                                       color='USA_SSHS',
                                       color_continuous_scale=custom_color_scale,
                                       range_color=(-5, 5),
                                       size='SIZE', size_max=7.5
                                       )

        else:
            figure.add_trace(px.scatter_mapbox(
                df_i, lat="LAT", lon="LON", zoom=4,
                hover_data=hover_data,
                color='USA_SSHS',
                color_continuous_scale=custom_color_scale,
                range_color=(-5, 5), size='SIZE', size_max=7.5,
            ).data[0])

    # Update the layout with custom colorbar title
    figure.update_layout(coloraxis_colorbar=dict(title="Category"))

    figure.update_traces(mode="markers+lines")
    figure.update_traces(marker=dict(opacity=1))

    figure.update_traces(hovertemplate=hover_template)

    return title, figure


if __name__ == "__main__":
    app.run_server(debug=True, port=8335)

# %%
# basin = 'AL'
# season = 2023
# query = (tropical_cyclones.BASIN == basin) & (
#     tropical_cyclones.SEASON == season)

# # query = (tropical_cyclones.SEASON == season)
# df = tropical_cyclones[query]
# df.head()
# df['color_tc'] = df['USA_SSHS'].apply(lambda x: tc_colors.get(x, color_other))

# df['size'] = df['USA_SSHS'].apply(lambda x: size_marker_TC.get(x, 6))

# tc = df.TC_ID.unique()

# for i, tc_i in enumerate(tc):
#     df_i = df[df.TC_ID == tc]
#     if i == 0:
#         figure = px.scatter_mapbox(df_i, lat="LAT", lon="LON", zoom=4,
#                                     mapbox_style="carto-positron",
#                                     hover_data=hover_data,
#                                     height=800,
#                                     color='USA_SSHS',
#                                     color_continuous_scale=custom_color_scale,
#                                     range_color=(-5, 5),
#                                     size='SIZE', size_max=7.5
#                                     )

#     else:
#         figure.add_trace(px.scatter_mapbox(
#             df_i, lat="LAT", lon="LON", zoom=4,
#             hover_data=hover_data,
#             color='USA_SSHS',
#             color_continuous_scale=custom_color_scale,
#             range_color=(-5, 5), size='SIZE', size_max=7.5,
#         ).data[0])

# # Update the layout with custom colorbar title
# figure.update_layout(coloraxis_colorbar=dict(title="Category"))

# figure.update_traces(mode="markers+lines")
# figure.update_traces(marker=dict(opacity=1))

# #%%
# figure.data.marker.line.width = 4
# figure.data.marker.line.color = "black"
# # %%
# .update_traces(
#      line=dict(dash="dot", width=4),
