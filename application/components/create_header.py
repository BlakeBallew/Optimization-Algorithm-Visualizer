from dash import Dash, html

def create_header(app: Dash) -> html.Div:
    return html.Header([
        html.Div([
            html.Div([
                html.H3('Contour Plot & Optimization Algorithm Visualizer', className='title')
            ]),
            html.Div([
                html.H4('Usage Docs', className='header-nav-link'),
                html.H4(html.A('Author', href='https://github.com/BlakeBallew', target='_blank'), className='header-nav-link')
            ], className='nav-links-container')       
        ], className='dummy-container')
    ], className='header-container')