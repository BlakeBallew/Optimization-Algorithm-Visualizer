from dash import Dash, html, dcc
import dash_daq as daq

def create_main_application(app: Dash) -> html.Div:
    return html.Div([
        html.Div([
            html.H3('Algorithm Configurations', className='algorithm-settings-title'),
            html.Div('Algorithm', className='algorithm-toggles-label'),
            html.Div([
                dcc.Dropdown([
                    'Gradient Descent',
                    'BFGS',
                ], value='Gradient Descent', clearable=False, maxHeight=100)
            ], className='algorithm-dropdown-container'),

            html.Div([
                html.Div([
                    html.Div('Starting point', className='toggles-label'),
                    html.Div([
                        html.Div('x:'),
                        dcc.Input(type='number', className='coordinate-input', value=3)
                    ], className='coordinate-input-container'),
                    html.Div([
                        html.Div('y:'),
                        dcc.Input(type='number', className='coordinate-input', value=2)
                    ], className='coordinate-input-container')
                ], className='starting-point-input-container'),
                html.Div([
                    html.Div('Show 3D', className='toggles-label'),
                    daq.BooleanSwitch(on=False)
                ])                
            ], className='coordinate-3d-container')
        ], className='algorithm-toggles-container'),
        
        html.Div([
            dcc.Graph(className='contour-plot', id='contour-plot')
        ], className='contour-plot-container')
    ], className='plot-and-toggles-container')