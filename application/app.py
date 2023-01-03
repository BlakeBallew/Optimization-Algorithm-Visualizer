# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import random
import json

from dash import Dash, html, dcc, ctx
from dash.dash import no_update
import dash_loading_spinners as dls
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from components.create_header import create_header
from components.create_expression_input import create_expression_input
from components.create_main_application import create_main_application
from components.create_contour_settings import create_contour_settings
from components.create_footer import create_footer
from functions.compute_zmatrix import compute_zmatrix
from functions.compute_gradient import compute_gradient

"""
dcc store scheme:
{
    '2d_plot': dict,
    '2d_plot': dict,
    'descent_dir': list[float],
    'step_size': float,
    'gradient_norm': float,
    'app_state': everything,
}
need to update x and y coord in same callback
"""



app = Dash(
    __name__,
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    create_header(app),
    html.Div([
        dcc.Input(type='text', className='expression-input', value='x^2+y^2', id='user-expression'),
        html.Button('Calculate', id='recalc-btn', className='calculate-btn')
    ],className='expression-input-container'),
    html.Section([
        html.Div([
            html.Div([
                html.Div([
                
                    dcc.Dropdown([
                        'Gradient Descent',
                        'BFGS',
                    ], value='Gradient Descent', clearable=False, maxHeight=100, id='algo-dropdown'),
                    html.Div([
                        html.H5('X-Coordinate:'),
                        dcc.Input(type='number', value=2, style={'width': '25%'}, id='x-coordinate'),
                    ], className='x-coord-input'),
                    html.Div([
                        html.H5('Y-Coordinate:'),
                        dcc.Input(type='number', value=3, style={'width': '25%'}, id='y-coordinate'),
                    ], className='y-coord-input'),
                    html.Div([
                        html.H5('Descent direction:'),
                        dcc.Markdown('N/A', className='latex-markdown')
                        # dcc.Markdown('$$\\begin{bmatrix} ' + str(1+6) + ' \\\ ' + str(2) + ' \\end{bmatrix}$$', mathjax=True, className='latex-markdown')
                    ], className='descent-direction-container'),
                    html.Div([
                        html.H5('Step size:'),
                        dcc.Markdown('N/A', className='latex-markdown')
                    ], className='step-size-container'),
                    html.Div([
                        html.H5('Gradient norm:'),
                        dcc.Markdown('N/A', className='latex-markdown')
                        # dcc.Markdown('$$\\begin{bmatrix} ' + str(1+6) + ' \\\ ' + str(2) + ' \\end{bmatrix}$$', mathjax=True)
                    ], className='gradient-norm-container'),
                    html.Div([
                        html.H5('Show 3D:', className='show-3d-text'),
                        daq.BooleanSwitch(on=False, className='toggle-3d', id='toggle-3d'),
                    ], className='show-3d-toggle'),
                    html.Div([
                        html.Button('Take step', id='reset-btn'),
                        html.Button('Reset', id='step-btn'),
                    ], className='step-reset-container')
                    
                ], className='toggles'),
            ], className='toggles-container'),
            html.Div([
                dls.Roller([
                    dcc.Graph(className='contour-plot', id='contour-plot')
                ], color='whitesmoke', debounce=1000, show_initially=False)
            ], className='contour-plot-container'),
        ], className='plot-toggles-container'),
        create_contour_settings(app)

    ], className='main-app-container'),

    create_footer(app),

    dcc.Store(id='app-store', data = {
        '2d_plot': None,
        '3d_plot': None,
        'toggle_3d': False,
        'descent_dir': None,
        'step_size': None,
        'gradient_norm': None,
        'app_state': None,
    })       
], className='app-container', id='app')




"""
Callbacks
"""

@app.callback(
    output = {
        'app-store': Output(component_id='app-store', component_property='data'),
        'x-coordinate': Output(component_id='x-coordinate', component_property='value'),
        'y-coordinate': Output(component_id='y-coordinate', component_property='value'),
        'app': Output(component_id='app', component_property='children'),
    },
    
    inputs = {
        'recalc_btn': Input(component_id='recalc-btn', component_property='n_clicks'), 
        'reset_btn': Input(component_id='reset-btn', component_property='n_clicks'), 
        'step_btn': Input(component_id='step-btn', component_property='n_clicks'),
        'toggle_3d': Input(component_id='toggle-3d', component_property='on'),
        'colorscale': Input(component_id='colorscale-dropdown', component_property='value'), 
        'start': Input(component_id='change-start', component_property='value'), 
        'stop': Input(component_id='change-stop', component_property='value'), 
        'step': Input(component_id='change-step', component_property='value'), 
        'smoothness': Input(component_id='smoothing-step-slider', component_property='value'), 
        'accuracy': Input(component_id='accuracy-step-slider', component_property='value'), 
    },
    
    state = {
        'expression': State(component_id='user-expression', component_property='value'),
        'store': State(component_id='app-store', component_property='data'),
        'x_coord': State(component_id='x-coordinate', component_property='value'),
        'y_coord': State(component_id='y-coordinate', component_property='value'), 
        'app': State(component_id='app', component_property='children'),
        'current_plot': State(component_id='contour-plot', component_property='figure'),
    }
)
def update_store(recalc_btn, 
                 reset_btn,
                 step_btn,
                 toggle_3d,
                 colorscale, 
                 start, 
                 stop, 
                 step, 
                 smoothness, 
                 accuracy, 
                 expression, 
                 store,
                 x_coord,
                 y_coord,
                 app,
                 current_plot):
    component_triggered = ctx.triggered_id
    output = {
        'app-store': no_update,
        'x-coordinate': no_update,
        'y-coordinate': no_update,
        'app': no_update,
    }
    
    if current_plot is None and store['2d_plot'] is None:
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
            'margin': {'t': 30, 'b': 0, 'l': 0, 'r': 0, 'pad': 5}, 
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
                    colorscale='Electric',
                    contours_z = contours_3d,
            ),
            layout = layout_3d,
        )
        
        store.update({
            '2d_plot': fig_2d.to_json(),
            '3d_plot': fig_3d.to_json(),
            'app_state': json.dumps(app),
        })
        
        output.update({
            'app-store': store,
        })
        
        return output
    
    if current_plot is None and store['2d_plot'] is not None:
        output.update({'app': json.loads(store['app_state'])})
        
    if component_triggered == 'recalc-btn':
        x_range = current_plot['layout']['xaxis']['range']
        y_range = current_plot['layout']['yaxis']['range']
        # beale function: '(1.5-x+(x*y))^2+(2.25-x+(x*(y^2)))^2+(2.625-x+(x*(y^3)))^2'
        # rosenbrock function: '(1-x)^2+100*(y-x^2)^2'
        x_inputs, y_inputs, z = compute_zmatrix(expression, x_range, y_range, accuracy)
        
        new_2d_fig = json.loads(store['2d_plot'])
        new_3d_fig = json.loads(store['3d_plot'])
        
        new_2d_fig['data'][0]['x'], new_2d_fig['data'][0]['y'], new_2d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z
        new_3d_fig['data'][0]['x'], new_3d_fig['data'][0]['y'], new_3d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z
        
        store.update({
            '2d_plot': json.dumps(new_2d_fig),
            '3d_plot': json.dumps(new_3d_fig),
        })
        
        # compute_gradient(expression, x_range, y_range, 3, 1, accuracy)

        output.update({'app-store': store})
        
        return output        
        

    
    if component_triggered == 'reset-btn':
        pass
    
    if component_triggered == 'step-btn':
        pass

    if component_triggered == 'toggle-3d':
        store.update({'toggle_3d': toggle_3d})
        output.update({'app-store': store})
        return output

    if component_triggered == 'colorscale-dropdown':
        
        new_3d_fig = json.loads(store['3d_plot'])
        new_2d_fig = json.loads(store['2d_plot'])
        
        new_3d_fig['data'][0]['colorscale'] = colorscale
        new_2d_fig['data'][0]['colorscale'] = colorscale
        
        store.update({
            '2d_plot': json.dumps(new_2d_fig),
            '3d_plot': json.dumps(new_3d_fig),
        })
        
        output.update({'app-store': store})
        
        return output
        
    
    if component_triggered == 'change-start':
        pass

    if component_triggered == 'change-stop':
        pass

    if component_triggered == 'change-step':
        pass
    
    if component_triggered == 'smoothing-step-slider':
        pass
    
    if component_triggered == 'accuracy-step-slider':
        pass


@app.callback(Output(component_id='contour-plot', component_property='figure'),
              Input(component_id='app-store', component_property='data'))
def update_figure(store):
    if store['toggle_3d']:
        return json.loads(store['3d_plot'])
    return json.loads(store['2d_plot'])




"""

@app.callback(Output(component_id='contour-plot', component_property='figure'),
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
            'margin': {'t': 30, 'b': 0, 'l': 0, 'r': 0, 'pad': 5}, 
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

        return fig_2d, plots

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

        return current_plot, plots

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

    return current_plot, plots

"""

"""
Entry point into the application
"""

if __name__ == '__main__':
    app.run_server(debug=True)
    
