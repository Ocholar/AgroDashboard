AgroDashboard

An interactive agronomic dashboard built with Plotly Dash to explore maize yield data across East Africa. Apply spatial, temporal, and categorical filters, view normalized variety performance, and surface key insights through maps, bar charts, and summary panels.



Demo

Live demo: coming soon 



Features

📍 Interactive Map



Automatically centers and zooms to fit all farmer plots



Jittered coordinates for clarity



Color-coded by YieldPerAcre, sized by AvgSampleYield\_per\_m2



🗺️ Filters



Country (All / Kenya / Tanzania / Rwanda)



Season (Standardized\_Season)



Variety (raw and normalized grouping)



Rain Type (Short rains / Long rains)



🔍 Hover Pop-Out



EstimatedYieldKG



PlotSize\_Acres



YieldPerAcre



Variety



Standardized\_Season



📊 Bar Chart



Average yield by normalized variety



Dynamic height scaling based on number of varieties



Merges variants like DK8031, DK\_8031, DK 8031



📋 Summary Panels



Top 5 varieties by average yield



Country-level average yields



Yield by rain type



⚙️ Data Processing



Cleans and normalizes variety names



Drops records with missing coordinates or yield



Imputes minimal sample yield for plotting

