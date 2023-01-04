from dash import Dash, html, dcc

def create_contour_settings(app: Dash) -> html.Div:
    return html.Div([
        
        html.H3('Plot Settings:', className='settings-title'),
        
        html.Div([
            html.Div('Colorscale:', className='setting-label'),
                dcc.Dropdown([
                    'Electric',
                    'Hot',
                    'Viridis',
                    'Cividis',
                    'Red Blue',
                ], value='Electric', clearable=False, maxHeight=100, id='colorscale-dropdown'),            
        ], className='colorscale-container'),

        html.Div([
            html.Div('Start:'),
            dcc.Input(type='number', value=0, id='change-start')
        ], className='toggle-start-container'),

        html.Div([
            html.Div('Stop:'),
            dcc.Input(type='number', value=50, id='change-stop')
        ], className='toggle-stop-container'),

        html.Div([
            html.Div('Step:'),
            dcc.Input(type='number', value=5, id='change-step')
        ], className='toggle-step-container'),

        html.Div([
            html.Div('Accuracy:', className='setting-label'),
            dcc.Slider(
                min=5, max=50, step=5, value=20, 
                id='accuracy-step-slider', 
                className='step-slider'
            ),            
        ], className='accuracy-container'),

        html.Div([
            html.Div('Auto-Smoothing:', className='setting-label', style={'paddingTop': '10px'}),
            dcc.Slider(
                min=0, max=1, value=0.6,
                id='smoothing-step-slider', 
                className='step-slider'
            ),            
        ], className='smoothing-container'),        

    ], className='settings-container')
