AgroDashboard

An interactive agronomic dashboard built with Plotly Dash to explore maize yield data across East Africa. Apply spatial, temporal, and categorical filters, view normalized variety performance, and surface key insights through maps, bar charts, and summary panels.

---

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Plotly Dash](https://img.shields.io/badge/Plotly-Dash-0175C2?logo=plotly)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?logo=pandas)
![GeoJSON](https://img.shields.io/badge/GeoJSON-Spatial%20Data-8E8E8E?logo=geojson)
![Heroku](https://img.shields.io/badge/Heroku-Deployment-430098?logo=heroku)
![Ngrok](https://img.shields.io/badge/Ngrok-Demo%20Link-1F1F1F?logo=ngrok)
![GitHub](https://img.shields.io/badge/GitHub-Version%20Control-181717?logo=github)

---

### 🎞️ Dashboard Demo
[![Live Demo](https://img.shields.io/badge/Live_Demo-ngrok-blue?logo=plotly)](https://f6f663660096.ngrok-free.app/)

![AgroDashboard Demo](dashboard_demo.gif)

---

### 📊 Dashboard Preview
![Dashboard Preview](dashboard_preview1.png)
![Dashboard Preview](dashboard_preview2.png)

---

Features

📍 Interactive Map



Automatically centers and zooms to fit all farmer plots



Jittered coordinates for clarity



Color-coded by YieldPerAcre, sized by AvgSampleYield\_per\_m2

---

🗺️ Filters



Country (All / Kenya / Tanzania / Rwanda)



Season (Standardized\_Season)



Variety (raw and normalized grouping)



Rain Type (Short rains / Long rains)

---

🔍 Hover Pop-Out



EstimatedYieldKG



PlotSize\_Acres



YieldPerAcre



Variety



Standardized\_Season

---

📊 Bar Chart



Average yield by normalized variety



Dynamic height scaling based on number of varieties



Merges variants like DK8031, DK\_8031, DK 8031

---

📋 Summary Panels


Top 5 varieties by average yield


Country-level average yields


Yield by rain type

---

⚙️ Data Processing

Cleans and normalizes variety names

Drops records with missing coordinates or yield

Imputes minimal sample yield for plotting


---

### 🎯 Use Cases

**👩‍🌾 Agronomists & Field Officers**
- Compare yield performance across seasons, varieties, and rainfall conditions
- Identify spatial patterns and outliers using clustering and map overlays
- Plan targeted field interventions based on granular, normalized insights

**📈 Donors & Funders**
- Visualize geographic impact and outcomes across program locations
- Evaluate the effectiveness of agronomic interventions over time
- Support data-backed proposals and grant reporting with visual metrics

**🛠️ Data Analysts & Engineers**
- Leverage structured agronomic data to refine models and dashboards
- Explore clustering techniques and geospatial mapping within Plotly Dash
- Build scalable pipelines from field data to front-end storytelling

**🎓 Researchers & Academics**
- Conduct exploratory analysis on environmental factors vs. yield
- Incorporate spatial filtering and metadata into agronomic studies
- Share insights with a broader audience through interactive visualization

---
