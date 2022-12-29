from dash import Dash, html, dcc

def create_expression_input(app: Dash) -> html.Div:
    return html.Div([
        dcc.Input(type='text', className='expression-input', value='x^2+y^2', id='user-expression'),
        html.Button('Recalculate', className='recalculate-zmatrix-button', id='zmatrix-btn'),
    ], className='expression-input-container')