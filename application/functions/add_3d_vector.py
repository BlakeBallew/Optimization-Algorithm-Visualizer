import plotly.graph_objects as go

def add_3d_vector(x: list[int], y: list[int], z: list[int], old_fig: dict) -> go.Figure:
    x_lines = list()
    y_lines = list()
    z_lines = list()
    
    for p in [(0, 1)]:
        for i in range(2):
            x_lines.append(x[p[i]])
            y_lines.append(y[p[i]])
            z_lines.append(z[p[i]])
    x_lines.append(None)
    y_lines.append(None)
    z_lines.append(None)

    trace = go.Scatter3d(
        x=x_lines,
        y=y_lines,
        z=z_lines,
        mode='lines',
        line = dict(width = 2, color = 'rgb(255, 0,0)')
    )

    new_fig = go.Figure(data = old_fig['data'],
                        layout = old_fig['layout'])
    
    new_fig.add_trace(trace)

    arrow_tip_ratio = 0.1
    arrow_starting_ratio = 0.98

    for p in [(0, 1)]:
        new_fig.add_trace(go.Cone(
            x=[x[p[0]] + arrow_starting_ratio*(x[p[1]] - x[p[0]])],
            y=[y[p[0]] + arrow_starting_ratio*(y[p[1]] - y[p[0]])],
            z=[z[p[0]] + arrow_starting_ratio*(z[p[1]] - z[p[0]])],
            u=[arrow_tip_ratio*(x[p[1]] - x[p[0]])],
            v=[arrow_tip_ratio*(y[p[1]] - y[p[0]])],
            w=[arrow_tip_ratio*(z[p[1]] - z[p[0]])],
            showlegend=False,
            showscale=False,
            colorscale=[[0, 'rgb(255,0,0)'], [1, 'rgb(255,0,0)']]
        ))

    return new_fig
