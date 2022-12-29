from dash import Dash, html, dcc

def create_contour_settings(app: Dash) -> html.Div:
    return html.Div([
        html.Div('Contour Plot Settings', className='settings-title'),
        html.Div([
            html.Div([
                html.Div('Colorscale', className='setting-label'),
                html.Div([
                    dcc.Dropdown([
                        'Electric',
                        'Hot',
                        'Viridis',
                        'Cividis',
                        'Red Blue',
                    ], value='Electric', className='dropdown', clearable=False, maxHeight=100, id='colorscale-dropdown')
                ], className='colorscale-dropdown-container'),
                html.Div([
                    html.Div([
                        html.Div('Start'),
                        dcc.Input(type='number', value=0, id='change-start')
                    ], className='start-stop-step-element'),
                    html.Div([
                        html.Div('Stop'),
                        dcc.Input(type='number', value=50, id='change-stop')
                    ], className='start-stop-step-element'),
                    html.Div([
                        html.Div('Step'),
                        dcc.Input(type='number', value=5, id='change-step')
                    ], className='start-stop-step-element')
                ], className='start-stop-step-container')
            ], className='left-side-controls'),
            html.Div([
                html.Div('Accuracy (requires recalculation)', className='setting-label'),
                html.Div([
                    dcc.Slider(
                        min=5, max=50, step=5,
                        id='accuracy-step-slider', className='step-slider', value=20)
                ], className='step-slider-container'),
                html.Div('Auto-Smoothing', className='setting-label', style={'paddingTop': '10px'}),
                html.Div([
                    dcc.Slider(
                        min=0, max=1,
                        id='smoothing-step-slider', className='step-slider', value=0.6)
                ], className='step-slider-container')
            ], className='right-side-controls')
        ], className='app-settings-container'),
    ], className='app-settings')