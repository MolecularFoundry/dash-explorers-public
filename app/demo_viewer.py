import glob
import dash
from dash import Dash, html, dcc, callback, Output, Input, State, Patch, register_page
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
import json
import h5py
from flask import current_app, session
import sys

from general_functions import *
from .dataset_cache import dataset_cache
from index_string import index_string

from common_explorer import protect_dashviews, generate_basic_components, add_common_callbacks

# explorer specific packages
import igor2 as igor
from PIL import Image


# ============ other functions you need!
# def decode_recurse(x):
#     if isinstance(x, dict):
#         for k in list(x.keys()):
#             x[k] = decode_recurse(x[k])
#     elif isinstance(x, bytes):
#         try:
#             x = x.decode('latin-1')
#         except:
#             x = x
#     elif isinstance(x, list):
#         x = [decode_recurse(i) for i in x]
#     elif isinstance(x, np.ndarray):
#         x = np.array([decode_recurse(i) for i in x])
#     else:
#         x = x
#     return(x)



def add_dash(server, env):
    # ============================== DEFINE DASH ENDPOINT AND PAGE TITLE ==================
    dash_endpoint = ""
    dash_app_title = ""
    
    dashapp = dash.Dash(__name__, 
                        server = server, 
                        use_pages = False, 
                        url_base_pathname = f"/datasets/{dash_endpoint}/", 
                        external_stylesheets=[dbc.themes.BOOTSTRAP], 
                        suppress_callback_exceptions = True)

        
    dashapp.index_string = index_string

    basic_layout = generate_basic_components(dash_app_title, reload_interval = 600, one_or_more = "one", kw_suggestion = "picam_readout")

    #  ================================= DEFINE APP COMPONENTS =========================
    '''
    examples:
    html.Div(id = 'text-component', 'write some text you want to display')
    html.H3(id = 'my-header', 'This will be a level 3 (medium size) header')
    dcc.Graph(id = 'my-figure', figure = "")
    '''
    additional_app_components = [
                                    # html.H3(id = "plot-title"),
                                    # html.Div(id = "z-choices-placeholder"),
                                    # html.Div(id = "color-map-choice-placeholder"),
                                    # dcc.Graph(id='fig1', figure = "")
                                 ]



    
    #  ================================= // ================== // =========================
    
    dashapp.layout = dbc.Container(
                                   basic_layout + additional_app_components, 
                                   fluid=True, 
                                   style={"margin": "0 auto", "max-width": "80%"}
                                  )

   # protect_dashviews(dashapp)
    add_common_callbacks(dashapp, env) 
   
    #  ================================= DEFINE APP CALLBACKS =========================
    '''
        example callback: 
        # auth-var and kw-checklist come from the basic layout components that are imported from common_explorer
        # you will need those two Inputs for any callback function that is loading in a dataset
        # auth-var is a flag indicating whether the user is authorized to view the selected dataset
        # kw-checklist is the value of the selected dataset(s) to view.  
        
        @dashapp.callback(
            Output(component_id='my-header', component_property='children'),
            Output(component_id='fig1', component_property='figure'),
            Input("auth-var", "value"), 
            Input("kw-checklist", "value"))
        def gen_fig1(auth, dsvalue):
            if auth is None:
                # if user not authorized, don't update the graph
                raise PreventUpdate
            else:
                # get the data
                dsid = dsvalue.strip('"').strip("'")
                dataset_cache(dsid, config=current_app.config, always_sync=False)
                dsname = glob.glob(f"./assets/{dsid}/*.h5")[-1]
                
                # read in the data
                with h5py.File(dsname, 'r') as f:
                    M = f['measurement/hyperspec_picam_mcl']
                    h_array = np.array(M['h_array'])
                    v_array = np.array(M['v_array'])
                    spec_map = np.array(M['spec_map'])[0]
                    wls = np.array(M['wls'])
                
                # make the plot
                spec_line = go.Figure(data = [go.Scatter(x=wls, 
                                                         y=spec_map[0,0,:],
                                                         mode = "markers+lines", 
                                                         marker=dict(size=2))
                                                         ]
                                    )
                return("Plot Title", spec_line)
    '''

    # @dashapp.callback(
    #     Output(component_id='z-choices-placeholder', component_property='children'),
    #     Input("auth-var", "value"), 
    #     Input("kw-checklist", "value"))
    # def gen_dropdown(auth, dsvalue):
    #     if auth is None:
    #         # if user not authorized, don't update the graph
    #         raise PreventUpdate
    #     else:
    #         # get the data
    #         dsid = dsvalue.strip('"').strip("'")
    #         dataset_cache(dsid, config=current_app.config, always_sync=False)
    #         dsname = glob.glob(f"./assets/{dsid}/*.ibw")[-1]
            
    #         # read in the data
    #         im = igor.binarywave.load(dsname)
    #         im = decode_recurse(im)
    #         ax_options = im['wave']['labels'][2][1:]
    #         print(ax_options)
    #         return(dcc.Dropdown(options = ax_options, value = ax_options[0], id = 'z-choice'), 
    #                dcc.Dropdown(options = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    #                   'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu','GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'], value = "Greys", id = 'colormap-choice'))

    
    # @dashapp.callback(
    #     Output(component_id='plot-title', component_property='children'),
    #     Output(component_id='fig1', component_property='figure'),
    #     Input("auth-var", "value"),
    #     Input("kw-checklist", "value"),
    #     Input("z-choice", "value"), 
    #     Input("colormap-choice", "value"))
    # def gen_fig1(auth, dsvalue, zchoice, colormap_choice):
    #     if auth is None:
    #         # if user not authorized, don't update the graph
    #         raise PreventUpdate
    #     else:
    #         # get the data
    #         dsid = dsvalue.strip('"').strip("'")
    #         dataset_cache(dsid, config=current_app.config, always_sync=False)
    #         dsname = glob.glob(f"./assets/{dsid}/*.ibw")[-1]
            
    #         # read in the data
    #         im = igor.binarywave.load(dsname)
    #         im = decode_recurse(im)
            
    #         w = np.array(im['wave']['wData'])

    #         # make the plot
    #         zindex = [i+1 for i,x in enumerate(im['wave']['labels'][2]) if x == zchoice][-1]

    #         fig = px.imshow(w[:,:,zindex], color_continuous_scale = colormap_choice)
            
    #         return(zchoice, fig)


    #  ================================= // ================== // =========================
    
    return(server)
