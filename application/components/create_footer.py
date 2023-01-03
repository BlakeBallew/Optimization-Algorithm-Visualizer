from dash import Dash, html

def create_footer(app: Dash) -> html.Div:
    return html.Footer([
        html.Div([
            html.H6('Created by Blake Ballew'),
            html.Div([
                html.A(html.H6('More Projects'), href='https://github.com/BlakeBallew?tab=repositories', target='_blank'),
                html.A(html.H6('Report a Bug / Contact Me'), href='mailto: bballew2001+opvisualizer@gmail.com'),                
            ], className='footer-rhs-links')
        ], className='centered-text')
    ], className='footer-container')