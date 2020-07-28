# -*- coding: utf-8 -*-
import datetime
import pathlib
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from dash.dependencies import Input, Output, State
from plotly import tools

import time
from cacheout import Cache
cache = Cache(maxsize=1, ttl=0, timer=time.time) 

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server

# Currency pairs
currencies = ['AUDUSD','AUDCAD','USDCAD','EURUSD','GBPUSD','USDJPY','USDCHF','NZDUSD'] 
#currencies = ['AUDUSD'] 

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("result").resolve()

currency_pair_data = dict()
for currency_pair in currencies:
    currency_pair_data[currency_pair] = pd.read_csv(DATA_PATH.joinpath("{}.csv".format(currency_pair)), index_col=1, parse_dates=["Date"])

cache.set('currency_pair_data',currency_pair_data) 

    


def first_ask_bid(currency_pair, t):
    currency_pair_data = cache.get('currency_pair_data')
    items = currency_pair_data[currency_pair]
    year = int(str(items.index.tolist()[0])[0:4])
    month = int(str(items.index.tolist()[0])[5:7])
    day = int(str(items.index.tolist()[0])[8:10])
    t = t.replace(year=year, month=month, day=day)
    dates = items.index.to_pydatetime()
    index = min(dates, key=lambda x: abs(x - t))
    df_row = items.loc[index]
    int_index = items.index.get_loc(index)
    int_index = 0
    return [df_row, int_index]  

def update_ask_bid(currency_pair):
    t = datetime.datetime.now()
    currency_pair_data = cache.get('currency_pair_data')
    items = currency_pair_data[currency_pair]
    year = int(str(items.index.tolist()[0])[0:4])
    month = int(str(items.index.tolist()[0])[5:7])
    day = int(str(items.index.tolist()[0])[8:10])
    t = t.replace(year=year, month=month, day=day)
    dates = items.index.to_pydatetime()
    index = min(dates, key=lambda x: abs(x - t))
    df_row = items.loc[index]
    int_index = items.index.get_loc(index)
    return [df_row, int_index]

def last_ask_bid(currency_pair):
	t = datetime.datetime.now()
	currency_pair_data = cache.get('currency_pair_data')
	items = currency_pair_data[currency_pair]
	year = int(str(items.index.tolist()[0])[0:4])
	month = int(str(items.index.tolist()[0])[5:7])
	day = int(str(items.index.tolist()[0])[8:10])
	t = t.replace(year=year, month=month, day=day)
	dates = items.index.to_pydatetime()
	index = min(dates, key=lambda x: abs(x - t))
	df_row = items.loc[index]
	int_index = len(items)
	return [df_row, int_index]

def get_lowest_spread(df,index):
    dates = df.index.to_pydatetime()
    index_ = [min(dates, key=lambda x: abs(x - i)) for i in index]
    print(index_)
    df_row = df.loc[index]
    return df_row['current_lowest_spread']



def get_row(data):
    index = data[1]  
    current_row = data[0]  

    return html.Div(
        children=[
            
            html.Div(
                id=current_row[0] + "summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.Div(
                        id=current_row[0] + "row",
                        className="row",
                        children=[
                            html.P(
                                current_row[0],  
                                id=current_row[0],
                                className="three-col",
                            ),
                            html.P(
                                current_row[1].round(5),  
                                id=current_row[0] + "bid",
                                className="three-col",
                            ),
                            html.P(
                                current_row[2].round(5),  
                                id=current_row[0] + "ask",
                                className="three-col",
                            ),
                            html.P(
                                current_row[3].round(8),  
                                id=current_row[0] + "lowest_spread",
                                className="three-col",
                            ),
                            html.Div(
                                index,
                                id=current_row[0]
                                + "index",  
                                style={"display": "none"},
                            ),
                        ],
                    )
                ],
            ),
            
            html.Div(
                id=current_row[0] + "contents",
                className="row details",
                children=[
                    
                    html.Div(
                        className="button-buy-sell-chart",
                        children=[
                            html.Button(
                                id=current_row[0] + "Buy",
                                children="Buy/Sell",
                                n_clicks=0,
                            )
                        ],
                    ),
                    
                    html.Div(
                        className="button-buy-sell-chart-right",
                        children=[
                            html.Button(
                                id=current_row[0] + "Button_chart",
                                children="Chart",
                                n_clicks=1
                                if current_row[0] in currencies
                                else 0,
                            )
                        ],
                    ),
                ],
            ),
        ]
    )


def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"


def replace_row(currency_pair, index, bid, ask,lowest_spread):
    currency_pair_data = cache.get('currency_pair_data')
    index = index + 1  
    new_row = (
        currency_pair_data[currency_pair].iloc[index]
        
        if index < len(currency_pair_data[currency_pair])
        else last_ask_bid(currency_pair)
    )  
 
    if isinstance(new_row,list):
    	new_row,index = new_row


    return [
        html.P(
            currency_pair, id=currency_pair, className="three-col"  
        ),
        html.P(
            new_row[1].round(5),  
            id=new_row[0] + "bid",
            className="three-col",
            style={"color": get_color(new_row[1], bid)},
        ),
        html.P(
            new_row[2].round(5),  
            className="three-col",
            id=new_row[0] + "ask",
            style={"color": get_color(new_row[2], ask)},
        ),
        html.P(
            new_row[3].round(8),  
            className="three-col",
            id=new_row[0] + "lowest_spread",
            style={"color": get_color(new_row[3], lowest_spread)},
        ),
        html.Div(
            index, id=currency_pair + "index", style={"display": "none"}
        ),  
    ]












def moving_average_trace(df, fig):
    df2 = df.rolling(window=5).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  
    return fig



def e_moving_average_trace(df, fig):
    df2 = df.rolling(window=20).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df.index, y=upper_band, mode="lines", showlegend=False, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df.index, y=rolling_mean, mode="lines", showlegend=False, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df.index, y=lower_band, mode="lines", showlegend=False, name="BB_lower"
    )

    fig.append_trace(trace, 1, 1)  
    fig.append_trace(trace2, 1, 1)  
    fig.append_trace(trace3, 1, 1)  
    return fig



def accumulation_trace(df):
    df["volume"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"]
    )
    trace = go.Scatter(
        x=df.index, y=df["volume"], mode="lines", showlegend=False, name="Accumulation"
    )
    return trace





'''
def cci_trace(df, ndays=5):
	print(df)
	TP = (df["high"] + df["low"] + df["close"]) / 3
	CCI = pd.Series(
		(TP - TP.rolling(window=10, center=False).mean())
		/ (0.015 * TP.rolling(window=10, center=False).std()),
		name="cci",
	)
	trace = go.Scatter(x=df.index, y=CCI, mode="lines", showlegend=False, name="CCI")
	return trace
'''
def lowest_spread_trace(df):
    #print(df)
    lowest_spread = df['current_lowest_spread']
    trace = go.Scatter(x=df.index, y=lowest_spread, mode='lines',showlegend=False, name="lowest_spread")
    return trace


def roc_trace(df, ndays=5):
    N = df["close"].diff(ndays)
    D = df["close"].shift(ndays)
    ROC = pd.Series(N / D, name="roc")
    trace = go.Scatter(x=df.index, y=ROC, mode="lines", showlegend=False, name="ROC")
    return trace



def stoc_trace(df):
    SOk = pd.Series((df["close"] - df["low"]) / (df["high"] - df["low"]), name="SO%k")
    trace = go.Scatter(x=df.index, y=SOk, mode="lines", showlegend=False, name="SO%k")
    return trace



def mom_trace(df, n=5):
    M = pd.Series(df["close"].diff(n), name="Momentum_" + str(n))
    trace = go.Scatter(x=df.index, y=M, mode="lines", showlegend=False, name="MOM")
    return trace



def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig



def line_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], mode="lines", showlegend=False, name="line"
    )
    return trace


def area_trace(df):
    trace = go.Scatter(
        x=df.index, y=df["close"], showlegend=False, fill="toself", name="area"
    )
    return trace


def bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#888888")),
        decreasing=dict(line=dict(color="#888888")),
        showlegend=False,
        name="bar",
    )


def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        showlegend=False,
        name="colored bar",
    )


def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#00ff00")),
        decreasing=dict(line=dict(color="white")),
        showlegend=False,
        name="candlestick",
    )





def get_fig(currency_pair, ask, bid, type_trace, studies, period):
    
    currency_pair_data = cache.get('currency_pair_data')
    data_frame = currency_pair_data[currency_pair]
    year = str(data_frame.index.tolist()[0])[0:4]
    month = str(data_frame.index.tolist()[0])[5:7]
    day = str(data_frame.index.tolist()[0])[8:10] 
    
    
    t = datetime.datetime.now()
    data = data_frame.loc[
        : t.strftime(
            "{}-{}-{} %H:%M:%S".format(year,month,day)
        ) 
    ]
    data_bid = data["Bid"]
    data_current_lowest_spread = data["current_lowest_spread"]
    df = data_bid.resample(period).ohlc()

    df_current_lowest_spread = data_current_lowest_spread.resample(period).min()
    df['current_lowest_spread'] = df_current_lowest_spread.tolist()

    
    subplot_traces = [  
        "accumulation_trace",
        "lowest_spread_trace",
        "roc_trace",
        "stoc_trace",
        "mom_trace",
    ]
    selected_subplots_studies = []
    selected_first_row_studies = []
    row = 1  


    row += 1
    selected_subplots_studies = ['lowest_spread_trace']
    
    if studies:
        for study in studies:
            if study in subplot_traces:
                row += 1  
                selected_subplots_studies.append(study)
            else:
                selected_first_row_studies.append(study)


    

    fig = tools.make_subplots(
        rows=row,
        shared_xaxes=True,
        shared_yaxes=True,
        cols=1,
        print_grid=False,
        vertical_spacing=0.12,
    )

    
    fig.append_trace(eval(type_trace)(df), 1, 1)

    
    for study in selected_first_row_studies:
        print(study)
        fig = eval(study)(df, fig)

    row = 1
    
    for study in selected_subplots_studies:
        row += 1
        fig.append_trace(eval(study)(df), row, 1)

    fig["layout"][
        "uirevision"
    ] = "The User is always right"  
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = "%H:%M"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    return fig



def chart_div(pair):
    return html.Div(
        id=pair + "graph_div",
        className="display-none",
        children=[
            
            html.Div(
                id=pair + "menu",
                className="not_visible",
                children=[
                    
                    html.Div(
                        id=pair + "menu_tab",
                        children=["Studies"],
                        style={"display": "none"},
                    ),
                    html.Span(
                        "Style",
                        id=pair + "style_header",
                        className="span-menu",
                        n_clicks_timestamp=2,
                    ),
                    html.Span(
                        "Studies",
                        id=pair + "studies_header",
                        className="span-menu",
                        n_clicks_timestamp=1,
                    ),
                    
                    html.Div(
                        id=pair + "studies_tab",
                        children=[
                            dcc.Checklist(
                                id=pair + "studies",
                                options=[
                                    {
                                        "label": "Accumulation/D",
                                        "value": "accumulation_trace",
                                    },
                                    {
                                        "label": "Bollinger bands",
                                        "value": "bollinger_trace",
                                    },
                                    {"label": "MA", "value": "moving_average_trace"},
                                    {"label": "EMA", "value": "e_moving_average_trace"},
                                    {"label": "lowest_spread", "value": "lowest_spread_trace"},
                                    {"label": "ROC", "value": "roc_trace"},
                                    {"label": "Pivot points", "value": "pp_trace"},
                                    {
                                        "label": "Stochastic oscillator",
                                        "value": "stoc_trace",
                                    },
                                    {
                                        "label": "Momentum indicator",
                                        "value": "mom_trace",
                                    },
                                ],
                                value=[],
                            )
                        ],
                        style={"display": "none"},
                    ),
                    
                    html.Div(
                        id=pair + "style_tab",
                        children=[
                            dcc.RadioItems(
                                id=pair + "chart_type",
                                options=[
                                    {
                                        "label": "candlestick",
                                        "value": "candlestick_trace",
                                    },
                                    {"label": "line", "value": "line_trace"},
                                    {"label": "mountain", "value": "area_trace"},
                                    {"label": "bar", "value": "bar_trace"},
                                    {
                                        "label": "colored bar",
                                        "value": "colored_bar_trace",
                                    },
                                ],
                                value="colored_bar_trace",
                            )
                        ],
                    ),
                ],
            ),
            
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id=pair + "menu_button",
                        className="inline-block chart-title",
                        children=f"{pair} ☰",
                        n_clicks=0,
                    ),
                    
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id=pair + "dropdown_period",
                                        options=[
                                        	{"label": "1 min", "value": "1Min"},
                                            {"label": "5 min", "value": "5Min"},
                                            {"label": "15 min", "value": "15Min"},
                                            {"label": "30 min", "value": "30Min"},
                                        ],
                                        value="15Min",
                                        clearable=False,
                                    )
                                ],
                            ),
                            html.Span(
                                id=pair + "close",
                                className="chart-close inline-block float-right",
                                children="×",
                                n_clicks=0,
                            ),
                        ],
                    ),
                ],
            ),
            # Graph div
            html.Div(
                dcc.Graph(
                    id=pair + "chart",
                    className="chart-graph",
                    config={"displayModeBar": False, "scrollZoom": True},
                )
            ),
        ],
    )



app.layout = html.Div(
    className="row",
    children=[
        
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        
        dcc.Interval(id="i_bis", interval=1 * 2000, n_intervals=0),
        
        dcc.Interval(id="i_tris", interval=1 * 5000, n_intervals=0),
        dcc.Interval(id="interval2", interval=1 * 8000, n_intervals=0),
        
        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),
        
        html.Div(
            className="three columns div-left-panel",
            children=[
                
                html.Div(
                    className="div-info",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("multilul.png")
                        ),
                        html.H6(className="title-header", children="FOREX TRADER"),
                        html.P(
                            """
                            
                            """
                        ),
                    ],
                ),
               
                html.Div(
                    className="div-currency-toggles",
                    children=[
                        html.P(
                            id="live_clock",
                            className="three-col",
                            children=datetime.datetime.now().strftime("%H:%M:%S"),
                        ),
                        html.P(className="three-col", children="Bid"),
                        html.P(className="three-col", children="Ask"),
                        html.P(className="three-col", children="lowest spread"),
                        html.Div(
                            id="pairs",
                            className="div-bid-ask",
                            children=[
                                get_row(first_ask_bid(pair, datetime.datetime.now()))
                                for pair in currencies
                            ],
                        ),
                    ],
                ),
                
            ],
        ),
        
        html.Div(
            className="nine columns div-right-panel",
            children=[
               
                
                html.Div(
                    id="charts",
                    className="row",
                    children=[chart_div(pair) for pair in currencies],
                ),
                
            ],
        ),
        
        html.Div(id="charts_clicked", style={"display": "none"}),
        html.Div(id="update", style={"display": "none"}),
        

    ],
)







def generate_ask_bid_row_callback(pair):
    def output_callback(n, i, bid, ask,lowest_spread):
        return replace_row(pair, int(i), float(bid), float(ask), float(lowest_spread))

    return output_callback



def generate_chart_button_callback():
    def chart_button_callback(*args):
        pairs = ""
        for i in range(len(currencies)):
            if args[i] > 0:
                pair = currencies[i]
                if pairs:
                    pairs = pairs + "," + pair
                else:
                    pairs = pair
        return pairs

    return chart_button_callback



def generate_figure_callback(pair):
    def chart_fig_callback(n_i, p, t, s, pairs, a, b, old_fig):

        if pairs is None:
            return {"layout": {}, "data": {}}

        pairs = pairs.split(",")
        if pair not in pairs:
            return {"layout": {}, "data": []}

        if old_fig is None or old_fig == {"layout": {}, "data": {}}:
            return get_fig(pair, a, b, t, s, p)

        fig = get_fig(pair, a, b, t, s, p)
        return fig

    return chart_fig_callback



def generate_close_graph_callback():
    def close_callback(n, n2):
        if n == 0:
            if n2 == 1:
                return 1
            return 0
        return 0

    return close_callback



def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu




def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name



def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab



def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab



def generate_show_hide_graph_div_callback(pair):
    def show_graph_div_callback(charts_clicked):
        if pair not in charts_clicked:
            return "display-none"

        charts_clicked = charts_clicked.split(",")  
        len_list = len(charts_clicked)

        classes = "chart-style"
        if len_list % 2 == 0:
            classes = classes + " six columns"
        elif len_list == 3:
            classes = classes + " four columns"
        else:
            classes = classes + " twelve columns"
        return classes

    return show_graph_div_callback



def generate_contents_for_left_panel():
    def show_contents(n_clicks):
        if n_clicks is None:
            return "display-none", "row summary"
        elif n_clicks % 2 == 0:
            return "display-none", "row summary"
        return "row details", "row summary-open"

    return show_contents




for pair in currencies:
    
    app.callback(
        [Output(pair + "contents", "className"), Output(pair + "summary", "className")],
        [Input(pair + "summary", "n_clicks")],
    )(generate_contents_for_left_panel())

    
    app.callback(
        Output(pair + "graph_div", "className"), [Input("charts_clicked", "children")]
    )(generate_show_hide_graph_div_callback(pair))

    
    app.callback(
        Output(pair + "chart", "figure"),
        [
            Input("i_tris", "n_intervals"),
            Input(pair + "dropdown_period", "value"),
            Input(pair + "chart_type", "value"),
            Input(pair + "studies", "value"),
            Input("charts_clicked", "children"),
        ],
        [
            State(pair + "ask", "children"),
            State(pair + "bid", "children"),
            State(pair + "chart", "figure"),
        ],
    )(generate_figure_callback(pair))

    
    app.callback(
        Output(pair + "row", "children"),
        [Input("i_bis", "n_intervals")],
        [
            State(pair + "index", "children"),
            State(pair + "bid", "children"),
            State(pair + "ask", "children"),
            State(pair + "lowest_spread", "children"),
        ],
    )(generate_ask_bid_row_callback(pair))

    
    app.callback(
        Output(pair + "Button_chart", "n_clicks"),
        [Input(pair + "close", "n_clicks")],
        [State(pair + "Button_chart", "n_clicks")],
    )(generate_close_graph_callback())

    
    app.callback(
        Output(pair + "menu", "className"),
        [Input(pair + "menu_button", "n_clicks")],
        [State(pair + "menu", "className")],
    )(generate_open_close_menu_callback())

    
    app.callback(
        [
            Output(pair + "menu_tab", "children"),
            Output(pair + "style_header", "className"),
            Output(pair + "studies_header", "className"),
        ],
        [
            Input(pair + "style_header", "n_clicks_timestamp"),
            Input(pair + "studies_header", "n_clicks_timestamp"),
        ],
    )(generate_active_menu_tab_callback())

    
    app.callback(
        Output(pair + "style_tab", "style"), [Input(pair + "menu_tab", "children")]
    )(generate_style_content_tab_callback())

   
    app.callback(
        Output(pair + "studies_tab", "style"), [Input(pair + "menu_tab", "children")]
    )(generate_studies_content_tab_callback())




app.callback(
    Output("charts_clicked", "children"),
    [Input(pair + "Button_chart", "n_clicks") for pair in currencies],
    [State("charts_clicked", "children")],
)(generate_chart_button_callback())





@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M:%S")



@app.callback(Output("update", "children"), [Input("interval2", "n_intervals")])
def update_D(n):
    for currency_pair in currencies:
        currency_pair_data[currency_pair] = pd.read_csv(DATA_PATH.joinpath("{}.csv".format(currency_pair)), index_col=1, parse_dates=["Date"])
    cache.set('currency_pair_data',currency_pair_data)  
if __name__ == "__main__":
    app.run_server(host='0.0.0.0',debug=True, port=8081,processes=8)
