import folium
from streamlit_folium import st_folium

def show_map(orders):
    m = folium.Map(location=[12.97, 77.59], zoom_start=10)

    colors = {
        "Pending": "green",
        "Accepted": "blue",
        "Assigned": "purple",
        "Expired": "gray",
    }

    for order in orders:
        x, y = order["location"]
        folium.Marker(
            [x, y],
            popup=f"Food: {order['food_qty']} | Status: {order['status']}",
            icon=folium.Icon(color=colors.get(order["status"], "green"))
        ).add_to(m)

    st_folium(m, width=700)
