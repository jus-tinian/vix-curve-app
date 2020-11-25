import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from plotting import plot_distributions


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


def get_vix_data():

    url = 'http://www.cboe.com/delayedquote/futures-quotes'
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    vx = soup.find_all('table')[6]  # locates the table for VX contracts
    vx = [i.text.strip() for i in vx.find_all('td')]
    quotes = pd.DataFrame({
        "Symbol": vx[::9],
        "Expiration": vx[1::9],
        "Last": vx[2::9],
        "Change": vx[3::9],
        "High": vx[4::9],
        "Low": vx[5::9],
        "Settlement": vx[6::9],
        "Volume": [i.replace(',', '') for i in vx[7::9]],
        "Open Int": [i.replace(',', '') for i in vx[8::9]]
    })
    # dropping weeklies
    quotes = quotes.loc[quotes['Symbol'].str.len() == 5, :]

    quotes['Expiration'] = pd.to_datetime(quotes['Expiration'])
    quotes[['Volume', 'Open Int']] = quotes[['Volume', 'Open Int']].astype('int')
    quotes[['Last', 'Change', 'High', 'Low', 'Settlement']] = quotes[['Last', 'Change', 'High', 'Low', 'Settlement']].astype('float')

    if quotes['Last'].iloc[-1] == 0:
        quotes = quotes.iloc[:-1, :]

    return quotes


def get_vix_products():

    url = 'http://www.cboe.com/products/vix-index-volatility/volatility-indexes'
    req = requests.get(url)
    soup = BeautifulSoup(req.text)
    quotes = soup.find_all('table')[1].text.split()
    vix_index_start = quotes.index('VIX')
    quotes = quotes[vix_index_start:]
    quotes = pd.DataFrame([
                  {
                      'VIX': quotes[:3][1],
                      'VXN': quotes[3:6][1],
                      'VXO': quotes[6:9][1],
                      'VXD': quotes[9:12][1],
                      'RVX': quotes[12:15][1],
                      'VIX9D': quotes[15:18][1],
                      'VIX3M': quotes[18:21][1],
                      'VIX6M': quotes[21:24][1],
                      'VIX1Y': quotes[24:27][1]
                   }
     ])

    return quotes.iloc[0]


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
        height=500,
        margin=dict(l=25, r=10, b=25, t=50)
    )

    return fig


NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [dbc.Col(dbc.NavbarBrand("S&P 500 Volatility Index"))],
                align="center",
                no_gutters=True,
            )
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

VIX_CURVE = dcc.Graph(
    id="vix_curve",
    figure=create_figure(),
    config={
        'responsive': True,  # dynamically resize Graph with browser window
        'displayModeBar': True,  # always show the Graph tools
        'displaylogo': False  # remove the plotly logo
    }
)

VIX_SPOT_HIST = dcc.Graph(
    id="vix_hist",
    figure=plot_distributions(yf.Ticker('^VIX').history(period="Max")[['Close']]),
    config={
        'responsive': True,  # dynamically resize Graph with browser window
        'displayModeBar': True,  # always show the Graph tools
        'displaylogo': False  # remove the plotly logo
    }
)

vix_products = get_vix_products()
VIX_CARDS = dbc.Row(

    [

        dbc.Col(
            [
                dbc.Card([
                    html.H4('VIX Spot'),
                    html.H6(vix_products['VIX'], id='spot')
                ], id='vix-spot', className='mini_container')
            ]),

        dbc.Col(
            [
                dbc.Card([
                    html.H4('VIX9D'),
                    html.H6(vix_products['VIX9D'], id='9d')
                ], id='vix-9d', className='mini_container')
            ]),

        dbc.Col(
            [
                dbc.Card([
                    html.H4('VIX3M'),
                    html.H6(vix_products['VIX3M'], id='3m')
                ], id='vix-3m', className='mini_container')
            ]),

        dbc.Col(
            [
                dbc.Card([
                    html.H4('VIX6M'),
                    html.H6(vix_products['VIX6M'], id='6m')
                ], id='vix-6m', className='mini_container')
            ]),

        dbc.Col(
            [
                dbc.Card([
                    html.H4('VIX1Y'),
                    html.H6(vix_products['VIX1Y'], id='1y')
                ], id='vix-1y', className='mini_container')
            ])

    ], id='metrics_card')

BODY = dbc.Container(
    [

        VIX_CARDS,

        dbc.Row([
            dbc.Col(VIX_CURVE, className='pretty_container')
        ], className='main_chart'),

        dbc.Row([
            dbc.Col(VIX_SPOT_HIST, className='pretty_container')
        ], className='main_chart'),

    ])


# serve on refresh
def serve_layout():

    layout = html.Div(
        [
            NAVBAR,
            html.Br(),
            BODY
        ]
    )

    return layout


app.layout = serve_layout


if __name__ == "__main__":
    app.run_server(debug=True)