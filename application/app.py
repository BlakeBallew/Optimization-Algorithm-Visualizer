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
from functions.add_2d_vector import add_2d_vector
from functions.add_3d_vector import add_3d_vector
from functions.string_eval import NumericStringParser
from functions.armijo import armijo_search
from functions.update_BFGS import update_BFGS

"""
dcc store scheme:
{
    '2d_plot': dict,
    '2d_plot': dict,
}
need to update x and y coord in same callback
"""



app = Dash(
    __name__,
    suppress_callback_exceptions=True,
)

app.layout = html.Div([
    create_header(app),
    html.Div([
        html.Div([
            dcc.Input(type='text', className='expression-input', value='x^2+y^2', id='user-expression'),
            html.Button('Calculate', id='recalc-btn', className='calculate-btn')            
        ], className='expression-input-flex')
    ],className='expression-input-container'),
    html.Div(id='error-display'),
    html.Section([
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
                    dcc.Markdown('N/A', className='latex-markdown', id='descent-direction', mathjax=True)
                    # dcc.Markdown('$$\\begin{bmatrix} ' + str(1+6) + ' \\\ ' + str(2) + ' \\end{bmatrix}$$', mathjax=True, className='latex-markdown')
                ], className='descent-direction-container'),
                html.Div([
                    html.H5('Step size:'),
                    dcc.Markdown('N/A', className='latex-markdown', id='step-size')
                ], className='step-size-container'),
                html.Div([
                    html.H5('Gradient norm:'),
                    dcc.Markdown('N/A', className='latex-markdown', id='gradient-norm')
                    # dcc.Markdown('$$\\begin{bmatrix} ' + str(1+6) + ' \\\ ' + str(2) + ' \\end{bmatrix}$$', mathjax=True)
                ], className='gradient-norm-container'),
                html.Div([
                    html.H5('Show 3D:', className='show-3d-text'),
                    daq.BooleanSwitch(on=False, className='toggle-3d', id='toggle-3d'),
                ], className='show-3d-toggle'),
                html.Div([
                    html.Button('Take step', id='step-btn'),
                    html.Button('Reset', id='reset-btn'),
                ], className='step-reset-container')
                    
            ], className='toggles-container'),
            html.Div([
                dbc.Spinner([
                    dcc.Graph(className='contour-plot', id='contour-plot')
                ], color='whitesmoke', size='md', delay_show=100)
            ], className='contour-plot-container'),
        ], className='plot-toggles-container'),
        create_contour_settings(app)

    ], className='main-app-container'),

    create_footer(app),

    dcc.Store(id='app-store', storage_type='memory', data = {
        '2d_plot': None,
        '3d_plot': None,
        'hessian_matrix_approx': json.dumps(np.identity(2).tolist())
    })
], className='app-container', id='app')




# Serverside callbacks

@app.callback(
    output = {
        'app-store': Output(component_id='app-store', component_property='data'),
        'current_figure': Output(component_id='contour-plot', component_property='figure'),
        'x-coordinate': Output(component_id='x-coordinate', component_property='value'),
        'y-coordinate': Output(component_id='y-coordinate', component_property='value'),
        'error': Output(component_id='error-display', component_property='children'),
        'descent_direction': Output(component_id='descent-direction', component_property='children'),
        'step_size': Output(component_id='step-size', component_property='children'),
        'gradient_norm': Output(component_id='gradient-norm', component_property='children'),
    },
    
    inputs = {
        'recalc_btn': Input(component_id='recalc-btn', component_property='n_clicks'), 
        'reset_btn': Input(component_id='reset-btn', component_property='n_clicks'), 
        'step_btn': Input(component_id='step-btn', component_property='n_clicks'),
        'toggle_3d': Input(component_id='toggle-3d', component_property='on'),
        'apply_changes_btn': Input(component_id='apply-changes-btn', component_property='n_clicks'),
    },
    
    state = {
        'expression': State(component_id='user-expression', component_property='value'),
        'store': State(component_id='app-store', component_property='data'),
        'x_coord': State(component_id='x-coordinate', component_property='value'),
        'y_coord': State(component_id='y-coordinate', component_property='value'), 
        'current_plot': State(component_id='contour-plot', component_property='figure'),
        'colorscale': State(component_id='colorscale-dropdown', component_property='value'), 
        'start': State(component_id='change-start', component_property='value'), 
        'stop': State(component_id='change-stop', component_property='value'), 
        'step': State(component_id='change-step', component_property='value'), 
        'smoothness': State(component_id='smoothing-step-slider', component_property='value'), 
        'accuracy': State(component_id='accuracy-step-slider', component_property='value'),
        'selected_algorithm': State(component_id='algo-dropdown', component_property='value'),     
    }
)
def update_store(recalc_btn, 
                 reset_btn,
                 step_btn,
                 toggle_3d,
                 apply_changes_btn,
                 expression, 
                 store, 
                 x_coord, 
                 y_coord, 
                 current_plot, 
                 colorscale, 
                 start, 
                 stop,
                 step,
                 smoothness,
                 accuracy,
                 selected_algorithm):
    component_triggered = ctx.triggered_id
    output = {
        'app-store': no_update, # <- will contain 2d and 3d plots
        'current_figure': no_update,
        'x-coordinate': no_update,
        'y-coordinate': no_update,
        'error': html.I(''),
        'descent_direction': no_update,
        'step_size': no_update,
        'gradient_norm': no_update,
    }

    nsp = NumericStringParser()

    def func(alpha, descent_direction):
        ready_expression = expression.replace('x', str(x_coord+alpha*descent_direction[0])).replace('y', str(y_coord+alpha*descent_direction[1]))
        return nsp.eval(ready_expression)

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

        fig_2d['layout']['xaxis']['range'] = [-3, 5]
        fig_2d['layout']['yaxis']['range'] = [-3, 5]
        
        store.update({
            '2d_plot': fig_2d.to_json(),
            '3d_plot': fig_3d.to_json(),
        })
        
        output.update({
            'app-store': store,
            'current_figure': fig_2d,
        })
        
        
        return output

    if component_triggered == 'toggle-3d':
        if toggle_3d:
            store.update({'2d_plot': json.dumps(current_plot)})
        else:
            store.update({'3d_plot': json.dumps(current_plot)})
    else:
        if not toggle_3d:
            store.update({'2d_plot': json.dumps(current_plot)})
        else:
            store.update({'3d_plot': json.dumps(current_plot)})

    # if current_plot is None and store['2d_plot'] is not None:
    #     output.update({'app': json.loads(store['app_state'])})
    #     return output
    # beale function: '(1.5-x+(x*y))^2+(2.25-x+(x*(y^2)))^2+(2.625-x+(x*(y^3)))^2'
    # rosenbrock function: '(1-x)^2+100*(y-x^2)^2'
        
    if component_triggered == 'recalc-btn':
        # case where user tries to recalculate a 3d plot
        if toggle_3d:
            x_range = json.loads(store['2d_plot'])['layout']['xaxis']['range']
            y_range = json.loads(store['2d_plot'])['layout']['yaxis']['range']
        else: 
            x_range = current_plot['layout']['xaxis']['range']
            y_range = current_plot['layout']['yaxis']['range']
        
        
        try:
            x_inputs, y_inputs, z = compute_zmatrix(expression, x_range, y_range, accuracy)
        except Exception as error:
            output.update({'error': html.I(f'An error occurred! {error}')})
            return output


        new_2d_fig = json.loads(store['2d_plot'])
        new_3d_fig = json.loads(store['3d_plot'])
        
        new_2d_fig['data'][0]['x'], new_2d_fig['data'][0]['y'], new_2d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z
        new_3d_fig['data'][0]['x'], new_3d_fig['data'][0]['y'], new_3d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z
        
        store.update({
            '2d_plot': json.dumps(new_2d_fig),
            '3d_plot': json.dumps(new_3d_fig),
        })
        

        output.update({'app-store': store,
                       'current_figure': new_3d_fig if toggle_3d else new_2d_fig})
        return output        
    
        
    if component_triggered == 'reset-btn':
        new_2d_fig = json.loads(store['2d_plot'])
        new_3d_fig = json.loads(store['3d_plot'])
        
        new_2d_fig['layout']['shapes'] = []
        new_3d_fig['data'] = [new_3d_fig['data'][0]]
        
        store.update({'2d_plot': json.dumps(new_2d_fig),
                      '3d_plot': json.dumps(new_3d_fig)})

        output.update({
            'app-store': store,
            'descent_direction': 'N/A',
            'step_size': 'N/A',
            'gradient_norm': 'N/A',
            'current_figure': new_3d_fig if toggle_3d else new_2d_fig,
        })

        return output
    
    
    if component_triggered == 'step-btn':
        delta_y, delta_x = compute_gradient(expression, x_coord, y_coord)
        old_fval = func(0, np.array([0, 0]))

        if selected_algorithm == 'Gradient Descent':
            alpha = armijo_search(np.array([delta_x, delta_y]),
                                  old_fval,
                                  np.array([-delta_x, -delta_y]),
                                  func)
            new_fval = func(alpha, np.array([delta_x, delta_y]))

            new_x, new_y = x_coord+alpha*delta_x, y_coord+alpha*delta_y

            fig_2d_with_vector = add_2d_vector([x_coord, new_x], [y_coord, new_y], json.loads(store['2d_plot'])).to_json()
            fig_3d_with_vector = add_3d_vector([x_coord, new_x], [y_coord, new_y], [old_fval, new_fval], json.loads(store['3d_plot'])).to_json()
            store.update({'2d_plot': fig_2d_with_vector,
                        '3d_plot': fig_3d_with_vector})
            output.update({'descent_direction': '$$\\begin{bmatrix} ' + str(round(delta_x, 5)) + ' \\\ ' + str(round(delta_y, 5)) + ' \\end{bmatrix}$$'})
                        
      
        if selected_algorithm == 'BFGS':
            approx_hessian = np.array(json.loads(store['hessian_matrix_approx']))
            numpy_gradient = np.array([-delta_x, -delta_y])
            pk = -np.dot(approx_hessian, numpy_gradient)
            alpha = armijo_search(pk,
                                  old_fval,
                                  numpy_gradient,
                                  func)
            old_pt = np.array([x_coord, y_coord])
            old_gradient = numpy_gradient
            new_x, new_y = x_coord+alpha*pk[0], y_coord+alpha*pk[1]
            new_pt = np.array([new_x, new_y])
            new_delta_y, new_delta_x = compute_gradient(expression, new_x, new_y)
            new_gradient = np.array([-new_delta_x, -new_delta_y])
            pts_delta = new_pt - old_pt
            gradients_delta = new_gradient - old_gradient
            new_approx_hessian = update_BFGS(approx_hessian, gradients_delta, pts_delta)
            new_fval = func(alpha, np.array([pk[0], pk[1]]))

            fig_2d_with_vector = add_2d_vector([x_coord, new_x], [y_coord, new_y], json.loads(store['2d_plot'])).to_json()
            fig_3d_with_vector = add_3d_vector([x_coord, new_x], [y_coord, new_y], [old_fval, new_fval], json.loads(store['3d_plot'])).to_json()
            store.update({'2d_plot': fig_2d_with_vector,
                          '3d_plot': fig_3d_with_vector,
                          'hessian_matrix_approx': json.dumps(new_approx_hessian.tolist())})
            output.update({'descent_direction': '$$\\begin{bmatrix} ' + str(round(pk[0], 5)) + ' \\\ ' + str(round(pk[1], 5)) + ' \\end{bmatrix}$$'})


        output.update({'app-store': store,
                        'current_figure': json.loads(fig_3d_with_vector) if toggle_3d else json.loads(fig_2d_with_vector),
                        'x-coordinate': round(new_x, 5),
                        'y-coordinate': round(new_y, 5),
                        'step_size': str(round(alpha, 5)),
                        'gradient_norm': str(round(np.linalg.norm(np.array([delta_x, delta_y])), 5))})


        return output


    if component_triggered == 'toggle-3d':
        if toggle_3d:
            output.update({'current_figure': json.loads(store['3d_plot'])})
        else:
            output.update({'current_figure': json.loads(store['2d_plot'])})
        
        
        return output

    if component_triggered == 'apply-changes-btn':
        new_2d_fig = json.loads(store['2d_plot'])
        new_3d_fig = json.loads(store['3d_plot'])

        new_2d_fig['data'][0]['colorscale'] = colorscale
        new_3d_fig['data'][0]['colorscale'] = colorscale

        new_2d_fig['data'][0]['contours']['start'] = start
        new_2d_fig['data'][0]['contours']['end'] = stop
        new_2d_fig['data'][0]['contours']['size'] = step

        new_2d_fig['data'][0]['line']['smoothing'] = smoothness

        # case where user tries to recalculate a 3d plot
        if toggle_3d:
            x_range = json.loads(store['2d_plot'])['layout']['xaxis']['range']
            y_range = json.loads(store['2d_plot'])['layout']['yaxis']['range']
        else: 
            x_range = current_plot['layout']['xaxis']['range']
            y_range = current_plot['layout']['yaxis']['range']
        
        try:
            x_inputs, y_inputs, z = compute_zmatrix(expression, x_range, y_range, accuracy)
        except Exception as error:
            output.update({'error': html.I(f'An error occurred! {error}')})
            return output        

        new_2d_fig['data'][0]['x'], new_2d_fig['data'][0]['y'], new_2d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z
        new_3d_fig['data'][0]['x'], new_3d_fig['data'][0]['y'], new_3d_fig['data'][0]['z'] = list(x_inputs), list(y_inputs), z

        
        store.update({
            '2d_plot': json.dumps(new_2d_fig),
            '3d_plot': json.dumps(new_3d_fig),
        })

        output.update({'app-store': store,
                       'current_figure': new_3d_fig if toggle_3d else new_2d_fig})
        return output


# app

if __name__ == '__main__':
    app.run_server(debug=True)
    
