import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import dash_leaflet as dl

app = Dash(__name__)
server = app.server
app.title = "Maize Yield Dashboard"

DATA_FILE = os.getenv("DATA_URL", "merged_yield_data_sample.csv")
df = pd.read_csv(DATA_FILE, parse_dates=["PlantingDate"])
df.columns = df.columns.str.strip()
if "yield" in df.columns and "Yield" not in df.columns:
    df.rename(columns={"yield": "Yield"}, inplace=True)
df["SeasonYear"] = df["SeasonYear"].astype(int)
df["RainType"]    = df["RainType"].astype(str).fillna("Unknown")
df["Variety"]     = df["Variety"].astype(str).fillna("Unknown")

years      = sorted(int(y) for y in df["SeasonYear"].unique())
rain_types = sorted(df["RainType"].unique())
varieties  = sorted(df["Variety"].unique())
marks      = {y: str(y) for y in years}

app.layout = html.Div([
    html.H1("Maize Yield Dashboard"),
    html.Div([
        dcc.Dropdown(id="year-dropdown",
                     options=[{"label": y, "value": y} for y in years],
                     value=years, multi=True),
        dcc.Dropdown(id="rain-dropdown",
                     options=[{"label": r, "value": r} for r in rain_types],
                     value=rain_types, multi=True),
        dcc.Dropdown(id="variety-dropdown",
                     options=[{"label": v, "value": v} for v in varieties],
                     value=varieties, multi=True),
    ], style={"display":"flex","gap":"1rem","margin-bottom":"20px"}),
    dcc.Slider(id="year-slider",
               min=min(years), max=max(years), value=min(years),
               marks=marks, step=None),
    dl.Map(id="map", center=[-0.5,34.8], zoom=8,
           children=[dl.TileLayer(), dl.LayerGroup(id="markers")],
           style={"width":"100%","height":"600px","margin-top":"20px"})
])

@app.callback(
    Output("markers", "children"),
    Input("year-dropdown", "value"),
    Input("rain-dropdown", "value"),
    Input("variety-dropdown", "value"),
    Input("year-slider", "value")
)
def update_markers(selected_years, selected_rain, selected_varieties, slider_year):
    dff = df[
        df["SeasonYear"].isin(selected_years) &
        df["RainType"].isin(selected_rain) &
        df["Variety"].isin(selected_varieties) &
        (df["SeasonYear"] == slider_year)
    ]
    markers = []
    for _, row in dff.iterrows():
        popup = (
            f"Yield: {row['Yield']} MT/ha<br>"
            f"Planting Date: {row['PlantingDate'].date()}"
        )
        markers.append(
            dl.Marker(position=[row.Latitude, row.Longitude], children=[
                dl.Popup(html.Div(dcc.Markdown(popup))),
                dl.Tooltip(f"{row['Yield']} MT/ha")
            ])
        )
    return markers

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
