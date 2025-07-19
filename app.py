import os
import requests
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np

# ────────────────────────────────────────────────────────
# Download dataset from Dropbox if missing on dyno
DATA_FILE = "merged_yield_data.csv"
DROPBOX_URL = (
    "https://www.dropbox.com/scl/fi/"
    "i4nbcm1664irwbmjinqgi/merged_yield_data.csv?dl=1"
)

if not os.path.isfile(DATA_FILE):
    print(f"Downloading {DATA_FILE} from Dropbox…")
    resp = requests.get(DROPBOX_URL, stream=True)
    resp.raise_for_status()
    with open(DATA_FILE, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

# Load data
df = pd.read_csv(DATA_FILE)

# Normalize Season and RainType
season_col = "Standardized_Season"
df[season_col] = df[season_col].fillna("Unknown Season")
df["RainType"] = (
    df["RainType"]
    .str.strip()
    .str.lower()
    .replace({"short rains": "Short rains", "long rains": "Long rains"})
)

# Normalize Variety & display labels
df["Variety_normalized"] = (
    df["Variety"]
    .str.lower()
    .str.replace(r"[\s_]+", "", regex=True)
)
rep_names = df.groupby("Variety_normalized")["Variety"].first().to_dict()
df["Variety_display"] = df["Variety_normalized"].map(rep_names)

# Jitter coordinates
df["model_lat"] = pd.to_numeric(df["model_lat"], errors="coerce")
df["model_lon"] = pd.to_numeric(df["model_lon"], errors="coerce")
jitter = 0.0002
df["model_lat"] += np.random.uniform(-jitter, jitter, len(df))
df["model_lon"] += np.random.uniform(-jitter, jitter, len(df))

# Impute sample yield size
df["AvgSampleYield_per_m2"] = df["AvgSampleYield_per_m2"].fillna(0.1)

# Dropdown options
country_opts = ["All"] + sorted(df["Country"].dropna().unique())
season_opts = ["All"] + sorted(df[season_col].dropna().unique())
variety_opts = ["All"] + sorted(df["Variety"].dropna().unique())
rain_opts = ["All"] + sorted(df["RainType"].dropna().unique())

# Initialize Dash
app = dash.Dash(__name__)
app.title = "Maize Yield Dashboard"

app.layout = html.Div([
    html.H2("Maize Yield Dashboard", style={"textAlign": "center"}),

    # Filters
    html.Div([
        html.Div([
            html.Label("Country"),
            dcc.Dropdown(id="country-dropdown",
                         options=[{"label": c, "value": c} for c in country_opts],
                         value="All")
        ], style={"width": "24%", "display": "inline-block"}),

        html.Div([
            html.Label("Season"),
            dcc.Dropdown(id="season-dropdown",
                         options=[{"label": s, "value": s} for s in season_opts],
                         value="All")
        ], style={"width": "24%", "display": "inline-block", "marginLeft": "1%"}),

        html.Div([
            html.Label("Variety"),
            dcc.Dropdown(
                id="variety-dropdown",
                options=[{"label": v, "value": v} for v in variety_opts],
                multi=True,
                placeholder="Select varieties...",
                value=["All"],
                style={"width": "100%"}
            )
        ], style={"width": "24%", "display": "inline-block", "marginLeft": "1%"}),

        html.Div([
            html.Label("Rain Type"),
            dcc.Dropdown(id="rain-dropdown",
                         options=[{"label": r, "value": r} for r in rain_opts],
                         value="All")
        ], style={"width": "24%", "display": "inline-block", "marginLeft": "1%"})
    ], style={"marginBottom": "20px"}),

    # Map
    dcc.Graph(id="yield-map", style={"height": "650px"}),

    # Bar chart
    html.Div(id="bar-chart-container", style={"marginTop": "40px"}),

    # Summaries
    html.Div([
        html.Div(id="top-varieties", style={"width": "32%", "display": "inline-block", "verticalAlign": "top"}),
        html.Div(id="country-yields", style={"width": "32%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"}),
        html.Div(id="rain-yields", style={"width": "32%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"})
    ], style={"marginTop": "40px"})
])

@app.callback(
    [
        Output("yield-map", "figure"),
        Output("bar-chart-container", "children"),
        Output("top-varieties", "children"),
        Output("country-yields", "children"),
        Output("rain-yields", "children")
    ],
    [
        Input("country-dropdown", "value"),
        Input("season-dropdown", "value"),
        Input("variety-dropdown", "value"),
        Input("rain-dropdown", "value")
    ]
)
def update_dashboard(sel_country, sel_season, sel_varieties, sel_rain):
    dff = df.copy()
    if sel_country != "All":
        dff = dff[dff["Country"] == sel_country]
    if sel_season != "All":
        dff = dff[dff[season_col] == sel_season]
    if sel_varieties and "All" not in sel_varieties:  # Filter only if specific varieties selected
        dff = dff[dff["Variety"].isin(sel_varieties)]
    if sel_rain != "All":
        dff = dff[dff["RainType"] == sel_rain]

    # Drop invalid coordinates & yields
    dff = dff.dropna(subset=["model_lat", "model_lon", "YieldPerAcre"])

    # Map bounds & center
    lat_min, lat_max = dff["model_lat"].min(), dff["model_lat"].max()
    lon_min, lon_max = dff["model_lon"].min(), dff["model_lon"].max()
    center = {"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2}
    span = max(lat_max - lat_min, lon_max - lon_min)
    if span > 10:
        zoom = 4
    elif span > 5:
        zoom = 5
    elif span > 1:
        zoom = 6
    else:
        zoom = 8

    # Map figure with trimmed hover
    map_fig = px.scatter_mapbox(
        dff,
        lat="model_lat", lon="model_lon",
        color="YieldPerAcre", size="AvgSampleYield_per_m2",
        hover_data={
            "EstimatedYieldKG": True,
            "PlotSize_acres": True,
            "YieldPerAcre": True,
            "Variety": True,
            "Standardized_Season": True,
            "model_lat": False,
            "model_lon": False
        },
        center=center, zoom=zoom,
        mapbox_style="open-street-map",
        color_continuous_scale="Viridis",
        range_color=[600, 6000],
        title="Yield Distribution"
    )
    map_fig.update_traces(marker=dict(opacity=0.8, sizemin=4))
    map_fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

    # Bar chart data
    bar_df = dff.groupby("Variety_normalized").agg({
        "YieldPerAcre": "mean",
        "AvgSampleYield_per_m2": "mean"
    }).reset_index()
    bar_df["DisplayName"] = bar_df["Variety_normalized"].map(rep_names)
    bar_df = bar_df[bar_df["YieldPerAcre"].notna()]

    # Dynamic height
    height = max(600, len(bar_df) * 25)
    bar_fig = px.bar(
        bar_df,
        x="YieldPerAcre", y="DisplayName",
        color="AvgSampleYield_per_m2",
        orientation="h",
        labels={"YieldPerAcre": "Yield (kg/acre)", "DisplayName": "Maize Variety"},
        title="Average Yield by Normalized Variety"
    )
    bar_fig.update_layout(yaxis=dict(dtick=1))
    bar_chart = dcc.Graph(figure=bar_fig, style={"height": f"{height}px", "width": "100%"})

    # Summaries
    top5 = bar_df.sort_values("YieldPerAcre", ascending=False).head(5)
    top_varieties = html.Div([
        html.H4("Top 5 Varieties by Yield"),
        html.Ul([html.Li(f"{r['DisplayName']}: {r['YieldPerAcre']:.1f} kg/acre") for _, r in top5.iterrows()])
    ])

    country_avg = dff.groupby("Country")["YieldPerAcre"].mean().reset_index()
    country_avg = country_avg[country_avg["YieldPerAcre"].notna()]
    country_yields = html.Div([
        html.H4("Country-Level Average Yield"),
        html.Ul([html.Li(f"{r['Country']}: {r['YieldPerAcre']:.1f} kg/acre") for _, r in country_avg.iterrows()])
    ])

    rain_avg = dff.groupby("RainType")["YieldPerAcre"].mean().reset_index()
    rain_avg = rain_avg[rain_avg["YieldPerAcre"].notna()]
    rain_yields = html.Div([
        html.H4("Yield by Rain Type"),
        html.Ul([html.Li(f"{r['RainType']}: {r['YieldPerAcre']:.1f} kg/acre") for _, r in rain_avg.iterrows()])
    ])

    return map_fig, bar_chart, top_varieties, country_yields, rain_yields

if __name__ == "__main__":
    app.run(debug=True)
