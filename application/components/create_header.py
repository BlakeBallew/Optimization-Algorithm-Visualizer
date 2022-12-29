from dash import Dash, html

def create_header(app: Dash) -> html.Div:
    return html.Div([
        html.Div([
            html.H3('Contour Plot & Optimization Algorithm Visualizer', className='title')
        ]),
        html.Div([
            html.H3('Usage Guide', className='header-nav-link'),
            html.H3(html.A('Report a Bug'), className='header-nav-link'),
            html.H3(html.A('Author', href='https://github.com/BlakeBallew', target='_blank'), className='header-nav-link')
        ], className='nav-links-container')
    ], className='header-container')