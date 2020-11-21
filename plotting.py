import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_distributions(data_obj, is_target=False, is_binary=False, target_name='regr-tgt'):
    if is_binary: data_obj = data_obj * 1
    features = data_obj.columns
    titles = data_obj.columns
    colors = px.colors.qualitative.Vivid
    _rows = 2
    _cols = len(data_obj.columns)
    _vertical_spacing = 0.01
    sp = make_subplots(rows=_rows, cols=_cols, subplot_titles=titles, row_heights=[.25, .75], vertical_spacing=_vertical_spacing, horizontal_spacing = 0.05, shared_xaxes=True)
    line_height = sp.layout['yaxis']['domain'][0] - _vertical_spacing
    lines = [data_obj[i].mean() for i in data_obj]
    for idx, feature in enumerate(features):
        counts, bins = np.histogram(data_obj[feature], bins=50)
        dm = divmod(idx, _cols)
        r = dm[0]+1 # row num
        c = dm[1]+1 # col num
        sp.add_trace(go.Box(x=data_obj[feature], name='', marker=dict(color=colors[2])), row=1, col=c)
        sp.add_trace(go.Bar(x=bins, y=counts, marker={'color': counts, 'colorscale': 'viridis'}), row=2, col=c)
        sp.add_shape(type='line',
                     line=dict(color=colors[-2],
                               width=3, dash='dot'),
                     xref=f"x{c}", yref='paper', y0=0,
                     y1=line_height, x0=lines[idx], x1=lines[idx])
        if is_target:
            last_price = data_obj[features].iloc[-1][target_name]
            sp.add_shape(type='line',
                         line=dict(color=colors[-4],
                                   width=3, dash='dot'),
                         xref=f"x{c}", yref='paper', y0=0,
                         y1=line_height, x0=last_price, x1=last_price)
    sp.update_layout(height=600, showlegend=False)
    sp.update_xaxes(showgrid=False)
    sp.show()