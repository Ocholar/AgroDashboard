import os
import json

import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Optional clustering
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Initial load for slider bounds
df_init = pd.read_csv('merged_yield_data.csv')
min_year = int(df_init['SeasonYear'].min())
max_year = int(df_init['SeasonYear'].max())
slider_marks = {y: str(y) for y in range(min_year, max_year + 1)}

app = dash.Dash(__name__)
app.title = "Maize Yield Dashboard"

app.layout = html.Div([
    html.H1("Maize Yield Insights", style={'textAlign': 'center'}),

    # Filters row
    html.Div([
        html.Div([
            html.Label("Season Year"),
            dcc.Dropdown(id='year_filter', placeholder='All years')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Rain Type"),
            dcc.Dropdown(id='rain_filter', placeholder='All rain types')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Variety"),
            dcc.Dropdown(id='variety_filter', placeholder='All varieties')
        ], style={'width': '32%', 'display': 'inline-block'}),
    ], style={'marginBottom': '15px'}),

    # Slider
    html.Div([
        html.Label("Season Progress"),
        dcc.Slider(
            id='year_slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks=slider_marks,
            step=1
        )
    ], style={'padding': '0 20px 20px'}),

    # Layer selector
    html.Div([
        html.Label("Map Layer"),
        dcc.RadioItems(
            id='layer_toggle',
            options=[
                {'label': 'Base Map Only', 'value': 'none'},
                {'label': 'GeoJSON Regions', 'value': 'geojson'},
                {'label': 'Rainfall Map', 'value': 'rainfall'},
                {'label': 'Clustering by Variety', 'value': 'cluster'}
            ],
            value='none',
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        )
    ], style={'padding': '0 20px 20px'}),

    # Daily refresh
    dcc.Interval(id='interval_refresh', interval=24*60*60*1000, n_intervals=0),

    # Map + sidebar
    html.Div([
        html.Div([ dcc.Graph(id='map', style={'height': '700px'}) ],
                 style={'width': '74%', 'display': 'inline-block'}),
        html.Div([ html.H4("Summary"), html.Div(id='summary_stats') ],
                 style={'width': '25%', 'display': 'inline-block', 'padding': '20px'})
    ]),

    # Variety chart
    html.H4("Yield by Variety", style={'marginLeft': '20px'}),
    dcc.Graph(id='variety_yield_chart')
])


@app.callback(
    Output('map', 'figure'),
    Output('year_filter', 'options'),
    Output('rain_filter', 'options'),
    Output('variety_filter', 'options'),
    Output('summary_stats', 'children'),
    Output('variety_yield_chart', 'figure'),
    Input('year_filter', 'value'),
    Input('rain_filter', 'value'),
    Input('variety_filter', 'value'),
    Input('year_slider', 'value'),
    Input('layer_toggle', 'value'),
    Input('interval_refresh', 'n_intervals'),
    State('map', 'relayoutData')
)
def update_dashboard(year, rain, variety, slider_year, layer, _, relayout):
    # Reload data
    df = pd.read_csv('merged_yield_data.csv')

    # Dropdown options
    years_opts = [{'label': 'All', 'value': 'All'}] + [
        {'label': str(y), 'value': y}
        for y in sorted(df['SeasonYear'].dropna().unique())
    ]
    rains_opts = [{'label': 'All', 'value': 'All'}] + [
        {'label': r, 'value': r}
        for r in sorted(df['RainType'].dropna().unique())
    ]
    vars_opts = [{'label': 'All', 'value': 'All'}] + [
        {'label': v, 'value': v}
        for v in sorted(df['Variety'].dropna().unique())
    ]

    # Filter logic: dropdown year > slider > rain > variety
    dff = df.copy()
    if year and year != 'All':
        dff = dff[dff['SeasonYear'] == year]
    else:
        dff = dff[dff['SeasonYear'] == slider_year]

    if rain and rain != 'All':
        dff = dff[dff['RainType'] == rain]
    if variety and variety != 'All':
        dff = dff[dff['Variety'] == variety]

    # East Africa bounding box
    dff = dff[
        (dff['model_lat'] > -10) & (dff['model_lat'] < 5) &
        (dff['model_lon'] > 28) & (dff['model_lon'] < 42)
    ]

    # Base scatter_mapbox
    fig = px.scatter_mapbox(
        dff,
        lat='model_lat',
        lon='model_lon',
        color='YieldPerAcre',
        size='PlotSize_acres',
        hover_name='ImgID',
        custom_data=[
            'EstimatedYieldKG', 'YieldPerAcre',
            'Standardized_Season', 'Country', 'PlotSize_acres'
        ],
        zoom=6,
        height=800
    )
    fig.update_traces(hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Yield: %{customdata[0]:.2f} kg<br>"
        "Yield/Acre: %{customdata[1]:.2f} kg<br>"
        "Season: %{customdata[2]}<br>"
        "Country: %{customdata[3]}<br>"
        "Plot Size: %{customdata[4]:.2f} acres"
    ))
    fig.update_layout(mapbox_style="open-street-map")

    # GeoJSON overlay
    if layer == 'geojson':
        path = 'region_boundaries.geojson'
        if os.path.exists(path):
            with open(path) as f:
                geo = json.load(f)
            fig.update_layout(mapbox_layers=[{
                'source': geo, 'type': 'line', 'color': 'black'
            }])
        else:
            fig.add_annotation(
                text="GeoJSON not found",
                x=0.5, y=0.95, xref="paper", yref="paper",
                showarrow=False, font=dict(color="red")
            )

    # Rainfall overlay
    if layer == 'rainfall':
        img = 'rainfall_overlay.png'
        if os.path.exists(img):
            fig.update_layout(mapbox_layers=[{
                'sourcetype': 'image',
                'source': img,
                'coordinates': [[28, -10], [42, -10], [42, 5], [28, 5]],
                'opacity': 0.4
            }])
        else:
            fig.add_annotation(
                text="Rainfall overlay missing",
                x=0.5, y=0.95, xref="paper", yref="paper",
                showarrow=False, font=dict(color="red")
            )

    # Clustering by variety
    if layer == 'cluster':
        if SKLEARN_AVAILABLE and len(dff) >= 3:
            coords = dff[['model_lat', 'model_lon']]
            dff['Cluster'] = KMeans(n_clusters=3, random_state=42).fit_predict(coords)
            fig = px.scatter_mapbox(
                dff, lat='model_lat', lon='model_lon',
                color='Cluster', size='PlotSize_acres',
                hover_name='Variety',
                custom_data=[
                    'EstimatedYieldKG', 'YieldPerAcre',
                    'Standardized_Season', 'Country', 'PlotSize_acres'
                ],
                zoom=6, height=800
            )
            fig.update_layout(mapbox_style="open-street-map")
        else:
            msg = "Install scikit-learn for clustering" if not SKLEARN_AVAILABLE else "Need ≥3 points"
            fig.add_annotation(
                text=msg, x=0.5, y=0.95,
                xref="paper", yref="paper", showarrow=False,
                font=dict(color="red")
            )

    # Retain zoom/pan
    if relayout and 'mapbox.center' in relayout:
        fig.update_layout(
            mapbox_center=relayout['mapbox.center'],
            mapbox_zoom=relayout.get('mapbox.zoom', 6)
        )

    # Summary sidebar
    total = len(dff)
    avg = dff['YieldPerAcre'].mean() if total else 0
    top = "N/A"
    if total and not dff['YieldPerAcre'].dropna().empty:
        top = dff.groupby('Variety')['YieldPerAcre'].mean().idxmax()
    summary = [
        html.P(f"Total Plots: {total}"),
        html.P(f"Avg Yield/Acre: {avg:.2f} kg"),
        html.P(f"Top Variety: {top}")
    ]

    # Variety bar chart
    if total:
        chart = px.bar(
            dff.groupby('Variety', as_index=False)['YieldPerAcre'].mean(),
            x='Variety', y='YieldPerAcre',
            labels={'YieldPerAcre': 'kg/acre'},
            title='Average Yield by Variety'
        )
    else:
        chart = go.Figure()
        chart.add_annotation(
            text="No data for these filters",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=16, color="gray")
        )

    return fig, years_opts, rains_opts, vars_opts, summary, chart


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
