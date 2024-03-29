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


def download_file_if_needed(url, filename):
    """Downloads the file if it doesn't exist or has an unexpected size."""
    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        download_file(url, filename)
    elif os.path.getsize(filename) != requests.head(url).headers.get(
            'Content-Length'):
        download_file(url, filename)
    else:
        print("File already exists and has the expected size.")


def download_file(url, filename):
    """Downloads the file from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-2xx status codes

        with open(filename, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


# file_tc = os.path.join(os.path.dirname(__file__),
#                        'data/ibtracs.since1980.list.v04r00.csv')
file_tc = os.path.join(os.getcwd(),
                       'data/ibtracs.since1980.list.v04r00.csv')

url = 'https://www.ncei.noaa.gov/data/'\
    'international-best-track-archive-for-climate-stewardship-ibtracs'\
    '/v04r00/access/csv/ibtracs.since1980.list.v04r00.csv'


download_file_if_needed(url, file_tc)

#%%%

columns_to_import = ['SID', 'SEASON', 'NUMBER', 'BASIN', 'SUBBASIN',
                     'NAME', 'ISO_TIME', 'NATURE', 'LAT', 'LON', 'USA_WIND',
                     'USA_PRES', 'USA_ATCF_ID', 'USA_SSHS']

tropical_cyclones = pd.read_csv(
    file_tc, skiprows=[1], usecols=columns_to_import)
tropical_cyclones['ISO_TIME'] = pd.to_datetime(tropical_cyclones['ISO_TIME'])
tropical_cyclones['BASIN'] = tropical_cyclones['USA_ATCF_ID'].apply(
    lambda x: x[:2])
tropical_cyclones['TC_ID'] = tropical_cyclones['USA_ATCF_ID'].apply(
    lambda x: x[2:4])
tropical_cyclones['USA_WIND'] = tropical_cyclones['USA_WIND'].apply(
    lambda x: float(x) if x.strip() else float('NaN'))

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

centrer_prop = {'AL': {'center': {"lat": 23, "lon": -52},  'zoom': 2.5},
                'EP': {'center': {"lat": 18, "lon": -115},  'zoom': 3},
                'WP': {'center': {"lat": 25, "lon": 127},  'zoom': 3},
                'IO': {'center': {"lat": 5, "lon": 80},  'zoom': 3},
                'SI': {'center': {"lat": -18, "lon": 80},  'zoom': 3},
                'SP': {'center': {"lat": -23, "lon": 165},  'zoom': 3},
                'SH': {'center': {"lat": -10, "lon": 130},  'zoom': 4},
                'CP': {'center': {"lat": 0, "lon": 180},  'zoom': 2},
                'AS': {'center': {"lat": 20, "lon": 60},  'zoom': 4},
                'BB': {'center': {"lat": 20, "lon": 85},  'zoom': 4},
                }

basin_list_valid = list(tropical_cyclones.BASIN.unique())


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
app.title = 'jdmantillaq'

load_figure_template("darkly")
slider_style = {"font-size": "18px"}
text_style = {"font-size": "20px"}


tab1_content = dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col([
                html.P("Select a Basin:"),
                dcc.Dropdown(id="dropdown_basin_tab1",
                             options=[{'value': i, 'label': j} for i, j
                                      in basin_list.items()],
                             className="dbc", value="AL"),
                html.P("Select a Season (year):"),
                dcc.Dropdown(id="dropdown_season_tab1", options=season_list,
                             className="dbc", value=season_list[-2]),
                html.P("Select a date range:"),
                dcc.DatePickerRange(id="date_picker_tab1", className='dbc',
                                    display_format='DD/MM/YYYY',
                                    start_date_placeholder_text='DD/MM/YYYY'),
                html.P("Select a disturbance:"),
                dcc.Dropdown(id="dropdown_tc_tab1",
                             multi=True, className="dbc")


            ], width=3),
            dbc.Col([html.H4(id="title_fig1", style={'text-align': 'center'}),
                     dcc.Graph(id="graph_tab1")], width=9)])
         ]
    )
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col([
                html.P("Select a Basin:"),
                dcc.Dropdown(id="dropdown_basin_tab2",
                             options=[{'value': i, 'label': j} for i, j
                                      in basin_list.items()],
                             className="dbc", value="AL"),

                html.P("Select a time range:"),
                dcc.RangeSlider(id='slider_season_tab2',
                                className="dbc",
                                min=season_list[0],
                                max=season_list[-1],
                                step=1,
                                marks={i: {"label": f'{i}',
                                           "style": slider_style} for i in
                                       range(season_list[0],
                                             season_list[-1] + 1, 5)},
                                value=[season_list[0], season_list[-1]],
                                tooltip={"placement": "bottom",
                                         "always_visible": False},
                                ),
                dcc.Graph(id="graph_bar_tab2",
                           hoverData={"points": [
                                    {'customdata': ['ALLEN', 1980,
                                                    'Category 5', 165]}]})

            ], width=4),
            dbc.Col([
                html.H4(id="title_fig2", style={'text-align': 'center'}),
                dcc.Graph(id="graph_map_tab2",
                         )
            ], width=8)]

        )]
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
                        dbc.Tab(tab2_content, label="Max Wind Speed",
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
    [Output("graph_bar_tab2", 'figure')],
    [Input("dropdown_basin_tab2", "value"),
     Input('slider_season_tab2', 'value')])
def fig_bar_tab2(basin, season):
    if basin is None:
        raise PreventUpdate
    if season is None:
        raise PreventUpdate
    

    df = tropical_cyclones.query(
        '@season[0] <= SEASON <= @season[1] and BASIN == @basin')
    df = df.groupby(['SEASON', 'TC_ID', 'NAME']).max(['USA_WIND'])
    df = df.reset_index()
    df = df.sort_values(by='USA_WIND', ascending=False).head(10)
    df['CAT'] = df['USA_SSHS'].apply(lambda x: category_dict.get(x))

    hover_data = ['NAME', 'SEASON', 'CAT', 'USA_WIND']

    hover_template = \
        "<span style='font-size: 16px;'><b>Name:</b> %{customdata[0]}</span><br>" + \
        "<span style='font-size: 16px;'><b>Season:</b> %{customdata[1]}</span><br>" + \
        "<span style='font-size: 16px;'><b>Type:</b> %{customdata[2]}</span><br>" + \
        "<span style='font-size: 16px;'><b>Max Wind Speed:</b> %{customdata[3]} knots</span><br>"
        
    custom_ticks = np.arange(-5, 6)
    custom_tick_labels = [category_dict.get(x) for x in custom_ticks]
    
    time_range = f'{season[0]}-{season[1]}' if season[0]!=season[1] else f'{season[0]}'
    title = "Top 10 Cyclones by Maximum Wind Speed<br>"  +\
        f"{basin_list[basin]} ({time_range})"
    
    figure = px.bar(df,
                    x="NAME",
                    y="USA_WIND",
                    color='USA_SSHS',
                    hover_data=hover_data,
                    custom_data=hover_data,
                    color_continuous_scale=custom_color_scale,
                    range_color=(-5, 5),
                    title=title,
                    )
    # Update layout with custom y-axis label
    figure.update_layout(yaxis_title='Max Wind Speed [knots]')
    

    # Update the layout with custom colorbar title
    figure.update_layout(coloraxis_colorbar=dict(title="",
                                                 tickvals=custom_ticks,
                                                 ticktext=custom_tick_labels,
                                                 tickfont=dict(size=14)))
    figure.update_traces(hovertemplate=hover_template)

    return [figure]

@app.callback(
    [Output("title_fig2", 'children'),
     Output("graph_map_tab2", 'figure')],
    [Input("dropdown_basin_tab2", "value"),
     Input("graph_bar_tab2", "hoverData")]
)
def fig_map_tab2(basin, hoverData):
    name = hoverData["points"][0]["customdata"][0]
    season = hoverData["points"][0]["customdata"][1]
    cat =  hoverData["points"][0]["customdata"][2]
    title = f'{name}: {season}'
    
    df = tropical_cyclones.query(
            'BASIN == @basin and SEASON == @season and NAME in @name')
    df['COLOR_TC'] = df['USA_SSHS'].apply(
        lambda x: tc_colors.get(x, color_other))

    df['SIZE'] = df['USA_SSHS'].apply(lambda x: size_marker_TC.get(x, 6))
    df['CAT'] = df['USA_SSHS'].apply(lambda x: category_dict.get(x))
    hover_data = ['NAME', 'LAT',  'LON', 'CAT',
                  'USA_WIND', 'USA_PRES', 'ISO_TIME']
    
    custom_ticks = np.arange(-5, 6)
    custom_tick_labels = [category_dict.get(x) for x in custom_ticks]
    
    
    for i, dist_i in enumerate(df.TC_ID.unique()):
        df_i = df[df.TC_ID == dist_i]
        if i == 0:
            figure = px.scatter_mapbox(df_i, lat="LAT", lon="LON",
                                       mapbox_style="carto-positron",
                                       hover_data=hover_data,
                                       height=800,
                                       color='USA_SSHS',
                                       color_continuous_scale=custom_color_scale,
                                       range_color=(-5, 5),
                                       size='SIZE', size_max=7.5,
                                       zoom=3,
                                       )

        else:
            figure.add_trace(px.scatter_mapbox(
                df_i, lat="LAT", lon="LON",
                hover_data=hover_data,
                color='USA_SSHS',
                color_continuous_scale=custom_color_scale,
                range_color=(-5, 5), size='SIZE', size_max=7.5,
                zoom=3,
            ).data[0])
    
    figure.update_layout(coloraxis_colorbar=dict(title="",
                                                 tickvals=custom_ticks,
                                                 ticktext=custom_tick_labels,
                                                 tickfont=dict(size=16)))

    figure.update_traces(mode="markers+lines")
    figure.update_traces(marker=dict(opacity=1))
    return title, figure



# -----------------------------------------------------------------------------
# Tab1
# -----------------------------------------------------------------------------
@app.callback(
    [Output("date_picker_tab1", 'min_date_allowed'),
     Output("date_picker_tab1", 'max_date_allowed'),
     Output("date_picker_tab1", 'initial_visible_month'),
     Output("date_picker_tab1", 'start_date'),
     Output("date_picker_tab1", 'end_date'),
     Output("dropdown_tc_tab1", "options"),
     Output("dropdown_tc_tab1", "value")],
    [Input("dropdown_basin_tab1", "value"),
     Input("dropdown_season_tab1", "value")])
def set_dates_options(basin, season):
    if basin is None:
        raise PreventUpdate
    if season is None:
        raise PreventUpdate

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
    [Output("dropdown_tc_tab1", "options", allow_duplicate=True),
     Output("dropdown_tc_tab1", "value", allow_duplicate=True)],
    [Input("dropdown_basin_tab1", "value"),
     Input("dropdown_season_tab1", "value"),
     Input("date_picker_tab1", "start_date"),
     Input("date_picker_tab1", "end_date")], prevent_initial_call=True)
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
    [Input("dropdown_basin_tab1", "value"),
     Input("dropdown_season_tab1", "value"),
     Input("dropdown_tc_tab1", "value"),
     Input("date_picker_tab1", "start_date"),
     Input("date_picker_tab1", "end_date")],
)
def fig_map(basin, season, disturbance, start_date, end_date):
    if not all([basin, season, disturbance, start_date, end_date]):
        raise PreventUpdate

    df = tropical_cyclones.query(
        'BASIN == @basin and SEASON == @season and TC_ID in @disturbance')

    df = df.loc[df["ISO_TIME"].between(start_date, end_date)]

    df['COLOR_TC'] = df['USA_SSHS'].apply(
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
        
    custom_ticks = np.arange(-5, 6)
    custom_tick_labels = [category_dict.get(x) for x in custom_ticks]

    for i, dist_i in enumerate(disturbance):
        df_i = df[df.TC_ID == dist_i]
        if i == 0:
            figure = px.scatter_mapbox(df_i, lat="LAT", lon="LON",
                                       mapbox_style="carto-positron",
                                       hover_data=hover_data,
                                       height=800,
                                       color='USA_SSHS',
                                       color_continuous_scale=custom_color_scale,
                                       range_color=(-5, 5),
                                       size='SIZE', size_max=7.5,
                                       **centrer_prop[basin]
                                       )

        else:
            figure.add_trace(px.scatter_mapbox(
                df_i, lat="LAT", lon="LON",
                hover_data=hover_data,
                color='USA_SSHS',
                color_continuous_scale=custom_color_scale,
                range_color=(-5, 5), size='SIZE', size_max=7.5,
                **centrer_prop[basin]
            ).data[0])

    # Update the layout with custom colorbar title
    # figure.update_layout(coloraxis_colorbar=dict(title="Category"))
    figure.update_layout(coloraxis_colorbar=dict(title="",
                                                 tickvals=custom_ticks,
                                                 ticktext=custom_tick_labels,
                                                 tickfont=dict(size=16)))

    figure.update_traces(mode="markers+lines")
    figure.update_traces(marker=dict(opacity=1))

    figure.update_traces(hovertemplate=hover_template)

    return title, figure


if __name__ == "__main__":
    app.run_server(port=8335, host='0.0.0.0')

#%%