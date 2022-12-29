# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import random
import json

from dash import Dash, html, dcc, ctx
import dash_loading_spinners as dls
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from components.create_header import create_header
from components.create_expression_input import create_expression_input
from components.create_main_application import create_main_application
from components.create_contour_settings import create_contour_settings
from functions.compute_zmatrix import compute_zmatrix
from functions.compute_gradient import compute_gradient

app = Dash(
    __name__,
    suppress_callback_exceptions=True
)

app.layout = html.Div([ 
    create_header(app),
    html.Div([
        create_expression_input(app),
        dls.Ellipsis(html.Div(id='loading-ellipsis', className='ellipsis'), color='white', width=40, debounce=100),
        html.Div([
            create_main_application(app),
            create_contour_settings(app),
        ], className='app-body-container')
    ], className='app-container'),
    dcc.Store(id='plots', data = {})
])

"""
Callbacks
"""

@app.callback(Output(component_id='contour-plot', component_property='figure'),
              Output(component_id='loading-ellipsis', component_property='children'),
              Output(component_id='plots', component_property='data'),
              Input(component_id='zmatrix-btn', component_property='n_clicks'),
              Input(component_id='colorscale-dropdown', component_property='value'),
              Input(component_id='change-start', component_property='value'),
              Input(component_id='change-stop', component_property='value'),
              Input(component_id='change-step', component_property='value'),
              Input(component_id='smoothing-step-slider', component_property='value'),
              State(component_id='contour-plot', component_property='figure'),
              State(component_id='user-expression', component_property='value'),
              State(component_id='accuracy-step-slider', component_property='value'),
              State(component_id='plots', component_property='data'))
def recalculate_contour(btn_click, colorscale, start, stop, step, smoothness, current_plot, expression, accuracy, plots):
    component_triggered = ctx.triggered_id

    if current_plot is None:
        initial_x, initial_y, initial_z = compute_zmatrix('x^2+y^2', [-3, 5], [-3, 5], accuracy)
        contours_2d = {
            'start': start,
            'end': stop,
            'size': step,
        }
        contours_3d = {**contours_2d, **{
            'show': True,
            'usecolormap': True,            
        }}
        colorbar = {
            'nticks': 10,
            'ticks': 'outside',
            'tickwidth': 1,
            'showticklabels': True,
            'tickangle': 0,
            'tickfont_size': 12,
        }
        layout_2d = {
            'margin': {'t': 30, 'b': 30, 'pad': 5}, 
            'plot_bgcolor': '#212329',
            'paper_bgcolor': '#212329',
            'font': {'color': 'white'},
        }

        layout_3d_axis_config = {
            'backgroundcolor': '#212329',
            'gridcolor': 'white',
            'showbackground': True,
            'zerolinecolor': 'white',            
        }

        layout_3d = {**layout_2d, **{
            'scene': {
                'xaxis': layout_3d_axis_config,
                'yaxis': layout_3d_axis_config,
                'zaxis': layout_3d_axis_config,
            },
            'scene_camera_eye': {
                'x': -1.1,
                'y': -1.8,
                'z': 0.9,
            }
        }}

        fig_2d = go.Figure(
            data = go.Contour(
                    x = initial_x,
                    y = initial_y,
                    z = initial_z,
                    line_smoothing=smoothness,
                    colorscale='Electric',
                    contours = contours_2d,
                    colorbar = colorbar,
            ),
            layout = layout_2d
        )

        fig_3d = go.Figure(
            data = go.Surface(
                    x = initial_x,
                    y = initial_y,
                    z = initial_z,
                    # line_smoothing=smoothness,
                    colorscale='Electric',
                    contours_z = contours_3d,
                    # colorbar = colorbar,
            ),
            layout = layout_3d,
        )
      
        plots.update({'2d': fig_2d.to_json(),
                      '3d': fig_3d.to_json()})

        return fig_2d, [], plots

    # print(json.dumps(current_plot['data'][0]['line']['smoothing'], indent=3))

    if component_triggered == 'zmatrix-btn':

        # update is triggered by updating x, y, or z values
        x_range = current_plot['layout']['xaxis']['range']
        y_range = current_plot['layout']['yaxis']['range']

        # beale function: '(1.5-x+(x*y))^2+(2.25-x+(x*(y^2)))^2+(2.625-x+(x*(y^3)))^2'
        # rosenbrock function: '(1-x)^2+100*(y-x^2)^2'
        x_inputs, y_inputs, z = compute_zmatrix(expression, x_range, y_range, accuracy)
        current_plot['data'][0]['x'] = x_inputs
        current_plot['data'][0]['y'] = y_inputs
        current_plot['data'][0]['z'] = z

        compute_gradient(expression, x_range, y_range, 3, 1, accuracy)

        return current_plot, [], plots

    if component_triggered == 'change-start' and start is not None:
        current_plot['data'][0]['contours']['start'] = start

    if component_triggered == 'change-stop' and stop is not None:
        current_plot['data'][0]['contours']['end'] = stop
        
    if component_triggered == 'change-step' and step is not None:
        current_plot['data'][0]['contours']['size'] = step

    if component_triggered == 'colorscale-dropdown' and colorscale:
        current_plot['data'][0]['colorscale'] = colorscale

    if component_triggered == 'smoothing-step-slider':
        current_plot['data'][0]['line']['smoothing'] = smoothness

    return current_plot, [], plots

"""
Entry point into the application
"""

if __name__ == '__main__':
    app.run_server(debug=True)