import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_distributions(data_obj, last):

    features = data_obj.columns
    start = data_obj.index[0].date()
    end = data_obj.index[-1].date()
    colors = px.colors.qualitative.Vivid
    _rows = 2
    _cols = len(data_obj.columns)
    _vertical_spacing = 0.01
    sp = make_subplots(
        rows=_rows,
        cols=_cols,
        row_heights=[.25, .75],
        vertical_spacing=_vertical_spacing,
        horizontal_spacing=0.05,
        shared_xaxes=True)
    line_height = sp.layout['yaxis']['domain'][0] - _vertical_spacing
    lines = [data_obj[i].mean() for i in data_obj]
    for idx, feature in enumerate(features):
        counts, bins = np.histogram(data_obj[feature], bins=50)
        dm = divmod(idx, _cols)
        r = dm[0]+1  # row num
        c = dm[1]+1  # col num
        sp.add_trace(go.Box(x=data_obj[feature], name='', marker=dict(color=colors[2]), showlegend=False), row=1, col=c)
        sp.add_trace(go.Bar(x=bins, y=counts, marker={'color': counts, 'colorscale': 'viridis'}, showlegend=False), row=2, col=c)
        last_price = float(last)
        sp.add_shape(type='line',
                     line=dict(color=colors[-4],
                               width=3, dash='dot'),
                     xref=f"x{c}", yref='paper', y0=0,
                     y1=line_height, x0=last_price, x1=last_price)
    sp.update_xaxes(showgrid=False)

    sp.add_annotation(x=last_price*1.25,
                      y=counts.max() * .75,
                      xref='x1', yref='y2',
                      text=f'Last Spot-VIX: {last}',
                      showarrow=False, font=dict(size=12))

    sp.update_layout(
        title={
            'text': f'Spot-VIX, From {start} To {end}',
            'y': .96,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(size=10),
        legend=dict(
            title='', yanchor="top", y=1.3, xanchor="left", x=0, orientation="h"
        ),
        xaxis_rangeslider_visible=False,
        height=400,
        margin=dict(l=25, r=10, b=25, t=50)
    )

    return sp