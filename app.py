import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


def get_vix_data():

    url = 'http://www.cboe.com/delayedquote/futures-quotes'
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    vx = soup.find_all('table')[6]
    vx = [i.text.strip() for i in vx.find_all('td')]
    quotes = pd.DataFrame({
        "Symbol": vx[::9],
        "Expiration": vx[1::9],
        "Last": vx[2::9],
        "Change": vx[3::9],
        "High": vx[4::9],
        "Low": vx[5::9],
        "Settlement": vx[6::9],
        "Volume": vx[7::9],
        "Open Int": vx[8::9]
    })
    # dropping weeklies
    quotes = quotes.loc[quotes['Symbol'].str.len() == 5, :]

    if quotes['Last'].iloc[-1] == 0:
        quotes = quotes.iloc[:-1, :]

    return quotes


def create_figure():

    vix_data = get_vix_data()

    # make fig
    fig = go.Figure()

    # term structure
    fig.add_trace(
        go.Scatter(x=vix_data['Expiration'], y=vix_data['Last'], showlegend=False)
    )

    # set legend to top, update margin, hide range slider
    fig.update_layout(
        title={
            'text': 'VIX Futures Term Structure | Data Collected from CBOE',
            'y': .96,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(size=10),
        legend=dict(
            title='', yanchor="top", y=1.3, xanchor="left", x=0, orientation="h"
        ),
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=25, r=10, b=25, t=50)
    )

    return fig


NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [dbc.Col(dbc.NavbarBrand("Wango Contango"))],
                align="center",
                no_gutters=True,
            )
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

CHART = dcc.Graph(
    id="main_chart",
    figure=create_figure(),
    config={
        'responsive': True,  # dynamically resizes Graph with browser winder
        'displayModeBar': True,  # always show the Graph tools
        'displaylogo': False # remove the plotly logo
    }
)

BODY = dbc.Container(dbc.Col(CHART, className='pretty_container'), className='main_chart')

# the main app.yaml layout
app.layout = html.Div(
    [
        NAVBAR,
        html.Br(),
        BODY
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)