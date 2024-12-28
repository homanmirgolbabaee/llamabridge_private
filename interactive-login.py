import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests
from datetime import datetime
import pandas as pd

# Initialize session state
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None
if 'selection_history' not in st.session_state:
    st.session_state.selection_history = []
if 'geojson_data' not in st.session_state:
    st.session_state.geojson_data = None

# Data for Italian regions with coordinates
REGION_DATA = {
    'Piemonte': {'capital': 'Turin', 'type': 'Region', 'coords': [45.0732745, 7.680687]},
    "Valle d'Aosta": {'capital': 'Aosta', 'type': 'Region', 'coords': [45.7400243, 7.426186]},
    'Lombardia': {'capital': 'Milan', 'type': 'Region', 'coords': [45.4654219, 9.186516]},
    'Trentino-Alto Adige': {'capital': 'Trento', 'type': 'Region', 'coords': [46.0748238, 11.121801]},
    'Veneto': {'capital': 'Venice', 'type': 'Region', 'coords': [45.4371908, 12.327145]},
    'Friuli-Venezia Giulia': {'capital': 'Trieste', 'type': 'Region', 'coords': [45.6495264, 13.776818]},
    'Liguria': {'capital': 'Genoa', 'type': 'Region', 'coords': [44.4056499, 8.946256]},
    'Emilia-Romagna': {'capital': 'Bologna', 'type': 'Region', 'coords': [44.494887, 11.342616]},
    'Toscana': {'capital': 'Florence', 'type': 'Region', 'coords': [43.7695604, 11.255814]},
    'Umbria': {'capital': 'Perugia', 'type': 'Region', 'coords': [43.1107168, 12.389798]},
    'Marche': {'capital': 'Ancona', 'type': 'Region', 'coords': [43.6158299, 13.518915]},
    'Lazio': {'capital': 'Rome', 'type': 'Region', 'coords': [41.9027835, 12.496366]},
    'Abruzzo': {'capital': "L'Aquila", 'type': 'Region', 'coords': [42.3498479, 13.399509]},
    'Molise': {'capital': 'Campobasso', 'type': 'Region', 'coords': [41.5630056, 14.662716]},
    'Campania': {'capital': 'Naples', 'type': 'Region', 'coords': [40.8517983, 14.268124]},
    'Puglia': {'capital': 'Bari', 'type': 'Region', 'coords': [41.1171432, 16.871872]},
    'Basilicata': {'capital': 'Potenza', 'type': 'Region', 'coords': [40.6404067, 15.805148]},
    'Calabria': {'capital': 'Catanzaro', 'type': 'Region', 'coords': [38.9097919, 16.595802]},
    'Sicilia': {'capital': 'Palermo', 'type': 'Region', 'coords': [38.1156879, 13.362381]},
    'Sardegna': {'capital': 'Cagliari', 'type': 'Region', 'coords': [39.2238411, 9.121892]}
}

def create_map():
    # Create a folium map centered on Italy
    m = folium.Map(
        location=[42.8333, 12.8333],
        zoom_start=6,
        tiles='CartoDB positron'
    )

    # Add markers for each region
    for region, data in REGION_DATA.items():
        # Create marker
        folium.Marker(
            data['coords'],
            popup=f"<b>{region}</b><br>Capital: {data['capital']}",
            tooltip=region,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

        # Add circle around marker
        folium.Circle(
            data['coords'],
            radius=30000,  # 30km radius
            color='red',
            fill=True,
            popup=region
        ).add_to(m)

    return m

def main():
    st.title("🗺️ Italy Region Explorer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Map")
        
        # Create and display the map
        m = create_map()
        map_data = st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_clicked"]
        )
        
        # Handle map clicks
        if map_data["last_clicked"]:
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lng = map_data["last_clicked"]["lng"]
            
            # Find closest region to clicked point
            min_distance = float('inf')
            closest_region = None
            
            for region, data in REGION_DATA.items():
                region_lat, region_lng = data['coords']
                distance = ((region_lat - clicked_lat) ** 2 + (region_lng - clicked_lng) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_region = region
            
            if closest_region and min_distance < 0.5:  # Threshold for click proximity
                st.session_state.selected_region = closest_region
                # Update history
                st.session_state.selection_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'region': closest_region,
                    'capital': REGION_DATA[closest_region]['capital'],
                    'type': REGION_DATA[closest_region]['type']
                })
                st.rerun()
    
    with col2:
        st.header("📊 Region Information")
        
        if st.session_state.selected_region:
            region_info = REGION_DATA[st.session_state.selected_region]
            
            st.subheader("🎯 Selected Region")
            st.markdown(f"""
            - **Region:** {st.session_state.selected_region}
            - **Capital:** {region_info['capital']}
            - **Type:** {region_info['type']}
            """)
            
            if st.session_state.selection_history:
                st.subheader("📜 Selection History")
                df = pd.DataFrame(st.session_state.selection_history)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistics
                st.subheader("📈 Statistics")
                unique_regions = len(set(entry['region'] for entry in st.session_state.selection_history))
                total_regions = len(REGION_DATA)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Regions Visited", f"{unique_regions}/{total_regions}")
                with col2:
                    st.metric("Completion", f"{(unique_regions/total_regions):.1%}")
                
                st.progress(unique_regions/total_regions)
                
                # Download option
                if st.download_button(
                    "📥 Download History",
                    df.to_csv(index=False).encode('utf-8'),
                    "region_selection_history.csv",
                    "text/csv",
                    key='download-csv'
                ):
                    st.success("✅ History downloaded successfully!")
        
        # Clear history button
        if st.session_state.selection_history:
            if st.button("🗑️ Clear History"):
                st.session_state.selection_history = []
                st.session_state.selected_region = None
                st.rerun()

    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")

if __name__ == "__main__":
    main()