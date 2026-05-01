import folium
from streamlit_folium import st_folium

def show_map(donations, requests):
    m = folium.Map(location=[12.97, 77.59], zoom_start=10)

    for d in donations:
        folium.Marker(
            [d[4], d[5]],
            popup=f"Food: {d[2]}",
            icon=folium.Icon(color="green")
        ).add_to(m)

    for r in requests:
        folium.Marker(
            [r[4], r[5]],
            popup=f"Need: {r[2]}",
            icon=folium.Icon(color="red")
        ).add_to(m)

    st_folium(m, width=700)