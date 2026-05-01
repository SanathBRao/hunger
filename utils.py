import folium
from streamlit_folium import st_folium

ACTIVE_STATUSES = ("Pending", "Accepted", "Assigned")

def update_expired_orders(orders):
    changed = False
    for order in orders:
        if order["status"] in ACTIVE_STATUSES and order["expiry"] <= 0:
            order["status"] = "Expired"
            changed = True
    return changed

def order_summary(order):
    return {
        "ID": order["id"],
        "Donor": order["donor_name"],
        "Food Qty": order["food_qty"],
        "Expiry Hours": order["expiry"],
        "Location": order["location"],
        "Status": order["status"],
        "Assigned NGO": order["assigned_ngo"] or "Unassigned",
        "Created At": order["created_at"],
    }

def show_map(orders):
    m = folium.Map(location=[12.97, 77.59], zoom_start=10)

    colors = {
        "Pending": "green",
        "Accepted": "blue",
        "Assigned": "purple",
        "Completed": "orange",
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
