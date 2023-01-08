import plotly.graph_objects as go
import json

def add_2d_vector(x_coordinates, y_coordinates, old_fig) -> go.Figure:
    x0, x1 = x_coordinates
    y0, y1 = y_coordinates
    
    s = 0.95
    w = 0.015
    
    coord_vector = [s*(x1-x0), s*(y1-y0)]
    perp = [-y1+y0, x1-x0]
    
    tri_x1, tri_y1 = x1, y1
    tri_x2, tri_y2 = ((x0+coord_vector[0]) + perp[0]*w), ((y0+coord_vector[1]) + perp[1]*w)
    tri_x3, tri_y3 = ((x0+coord_vector[0]) - perp[0]*w), ((y0+coord_vector[1]) - perp[1]*w)
    
    new_fig = go.Figure(data = old_fig['data'],
                        layout = old_fig['layout'])
    
    # print(json.dumps(old_fig['layout'].get('shapes', []), indent=5))
    new_fig.update_layout(
        shapes = old_fig.get('layout', []).get('shapes', []) + [
            dict(type='path', path=f'M {tri_x1} {tri_y1} L {tri_x2} {tri_y2} L {tri_x3} {tri_y3} Z', fillcolor='rgb(255,0,0)', line_color='rgb(255,0,0)', layer='above'),
            dict(type='line', x0=x0, y0=y0, x1=x1-((x1-x0)/90), y1=y1-((y1-y0)/90), line=dict(color="rgb(255,0,0)"), layer='above')
        ] 
    )
    
    return new_fig