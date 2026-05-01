import folium
from streamlit_folium import st_folium

ACTIVE_STATUSES = ("Pending", "Accepted", "Assigned")
MAX_DELIVERY_DISTANCE = 10.0
LOW_EXPIRY_HOURS = 1.0

def calculate_distance(point_a, point_b):
    if not point_a or not point_b:
        return None

    x1, y1 = point_a
    x2, y2 = point_b
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def distance_label(distance):
    if distance is None:
        return "Unknown", "gray"
    if distance <= 5:
        return "Near", "green"
    if distance <= MAX_DELIVERY_DISTANCE:
        return "Moderate", "orange"
    return "Far", "red"

def delivery_feasibility(order):
    distance = order.get("distance")
    if distance is None:
        return "NGO location missing"
    if distance > MAX_DELIVERY_DISTANCE:
        return "Too far"
    if order["expiry"] <= LOW_EXPIRY_HOURS:
        return "Likely to expire"
    if order["status"] == "Expired":
        return "Expired"
    if order["status"] == "Cancelled":
        return "Cancelled"
    return "Feasible"

def sync_order_logistics(order, ngo_location=None):
    order.setdefault("donor_location", order.get("location"))
    order.setdefault("ngo_location", None)
    order.setdefault("distance", None)
    order.setdefault("delivery_status", "Not Assigned")
    order.setdefault("cancellation_reason", None)
    order.setdefault("distributed", False)

    if ngo_location is not None:
        order["ngo_location"] = ngo_location

    if order.get("donor_location") and order.get("ngo_location"):
        order["distance"] = calculate_distance(order["donor_location"], order["ngo_location"])

def update_expired_orders(orders):
    changed = False
    for order in orders:
        sync_order_logistics(order)
        if order["status"] in ACTIVE_STATUSES and order["expiry"] <= 0:
            order["status"] = "Expired"
            order["delivery_status"] = "Cancelled"
            order["cancellation_reason"] = "Expired"
            changed = True
    return changed

def order_summary(order):
    sync_order_logistics(order)
    distance = order.get("distance")
    feasibility = delivery_feasibility(order)
    return {
        "ID": order["id"],
        "Donor": order["donor_name"],
        "Food Qty": order["food_qty"],
        "Expiry Hours": order["expiry"],
        "Donor Location": order["donor_location"],
        "NGO Location": order["ngo_location"] or "Not assigned",
        "Distance": round(distance, 2) if distance is not None else "Unknown",
        "Feasibility": feasibility,
        "Status": order["status"],
        "Delivery Status": order["delivery_status"],
        "Assigned NGO": order["assigned_ngo"] or "Unassigned",
        "Cancel Reason": order["cancellation_reason"] or "",
        "Distributed": "Yes" if order["distributed"] else "No",
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
        "Cancelled": "red",
    }

    for order in orders:
        sync_order_logistics(order)
        x, y = order["donor_location"]
        folium.Marker(
            [x, y],
            popup=f"Food: {order['food_qty']} | Status: {order['status']} | Distance: {order['distance']}",
            icon=folium.Icon(color=colors.get(order["status"], "green"))
        ).add_to(m)

    st_folium(m, width=700)
