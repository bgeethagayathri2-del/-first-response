import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import requests

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="First Response", page_icon="🚨", layout="centered")

# ---------- EMERGENCY GUIDANCE DATA ----------
GUIDANCE = {
    "Medical Emergency": [
        "Call for help immediately (ambulance / local emergency number).",
        "Check if the person is breathing and conscious.",
        "Do not move the person unless they are in immediate danger.",
        "If trained, begin CPR only if the person is unresponsive and not breathing.",
        "Keep the person warm and calm until help arrives.",
    ],
    "Fire": [
        "Alert everyone nearby and evacuate immediately.",
        "Do not use elevators — use stairs only.",
        "Stay low to the ground to avoid smoke inhalation.",
        "Call the fire department as soon as you are safe.",
        "Do not re-enter the building for any reason.",
    ],
    "Accident": [
        "Ensure the area is safe before approaching.",
        "Call emergency services and share the exact location.",
        "Do not move injured people unless there is immediate danger (fire, traffic).",
        "Apply pressure to any severe bleeding with a clean cloth.",
        "Stay with the person and keep them calm until help arrives.",
    ],
    "Safety Threat": [
        "Move to a safe, populated, or secure location immediately.",
        "Call local emergency services or campus/building security.",
        "Avoid confrontation; prioritize getting to safety.",
        "Alert people nearby if it is safe to do so.",
        "Share your live location with a trusted contact.",
    ],
}

# ---------- FALLBACK SAMPLE LOCATIONS (used if live location/lookup fails) ----------
FALLBACK_HELP = [
    {"name": "City General Hospital", "lat": 12.9716, "lon": 77.5946, "type": "Hospital"},
    {"name": "Central Police Station", "lat": 12.9750, "lon": 77.6000, "type": "Police"},
    {"name": "Fire Station 4", "lat": 12.9700, "lon": 77.5900, "type": "Fire"},
]

ICON_MAP = {"Hospital": "plus", "Police": "shield", "Fire": "fire"}


def nearby_fallback(lat, lon):
    """Generate sample-labeled pins near the given location, used when the live lookup fails."""
    return [
        {"name": "Nearby Hospital (sample)", "lat": lat + 0.01, "lon": lon + 0.008, "type": "Hospital"},
        {"name": "Nearby Police Station (sample)", "lat": lat - 0.009, "lon": lon + 0.006, "type": "Police"},
        {"name": "Nearby Fire Station (sample)", "lat": lat + 0.006, "lon": lon - 0.01, "type": "Fire"},
    ]


def get_nearby_places(lat, lon, radius_m=4000):
    """Query OpenStreetMap's Overpass API for nearby hospitals, police, and fire stations."""
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="police"](around:{radius_m},{lat},{lon});
      node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
    );
    out center 10;
    """
    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        places = []
        type_lookup = {"hospital": "Hospital", "police": "Police", "fire_station": "Fire"}
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            amenity = tags.get("amenity")
            name = tags.get("name", type_lookup.get(amenity, "Unknown"))
            if "lat" in el and "lon" in el:
                places.append({
                    "name": name,
                    "lat": el["lat"],
                    "lon": el["lon"],
                    "type": type_lookup.get(amenity, "Other"),
                })
        return places
    except Exception:
        return []


# ---------- HEADER ----------
st.title("🚨 First Response")
st.caption("Fast guidance and help in the critical first minutes of an emergency.")

st.divider()

# ---------- STEP 1: EMERGENCY TYPE SELECTOR ----------
st.subheader("1. What's happening?")
emergency_type = st.radio(
    "Select the situation:",
    list(GUIDANCE.keys()),
    horizontal=True,
)

# ---------- STEP 2: GUIDANCE ----------
st.subheader("2. What to do right now")
for i, step in enumerate(GUIDANCE[emergency_type], start=1):
    st.markdown(f"**{i}.** {step}")

st.divider()

# ---------- STEP 3: LIVE LOCATION + NEARBY HELP ----------
st.subheader("3. Nearby help")
st.write("Tap the button below and allow location access in your browser to find real nearby help.")

location = streamlit_geolocation()

user_lat, user_lon = None, None
if location and location.get("latitude") is not None:
    user_lat = location["latitude"]
    user_lon = location["longitude"]
    st.success(f"Location found: {user_lat:.4f}, {user_lon:.4f}")

if user_lat and user_lon:
    with st.spinner("Looking up nearby hospitals, police, and fire stations..."):
        places = get_nearby_places(user_lat, user_lon)
    if not places:
        places = nearby_fallback(user_lat, user_lon)
    center_lat, center_lon = user_lat, user_lon
else:
    st.info("No location yet — showing sample locations. Tap the button above to use your real location.")
    places = FALLBACK_HELP
    center_lat = sum(p["lat"] for p in places) / len(places)
    center_lon = sum(p["lon"] for p in places) / len(places)

m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

if user_lat and user_lon:
    folium.Marker(
        location=[user_lat, user_lon],
        popup="You are here",
        tooltip="Your location",
        icon=folium.Icon(color="blue", icon="user"),
    ).add_to(m)

for place in places[:15]:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=f"{place['name']} ({place['type']})",
        tooltip=place["name"],
        icon=folium.Icon(color="red", icon=ICON_MAP.get(place["type"], "info-sign")),
    ).add_to(m)

st_folium(m, width=700, height=400)

st.divider()

# ---------- STEP 4: ALERT ----------
st.subheader("4. Send an alert")

contact_number = st.text_input(
    "Emergency contact's phone number (with country code, no + or spaces, e.g. 919876543210):"
)

if st.button("🚨 Generate Alert Message"):
    if contact_number.strip() == "":
        st.error("Please enter a phone number first.")
    else:
        loc_for_alert = (user_lat, user_lon) if user_lat and user_lon else (center_lat, center_lon)
        message = (
            f"EMERGENCY ALERT: {emergency_type} in progress. "
            f"I need help. My location: "
            f"https://www.google.com/maps?q={loc_for_alert[0]},{loc_for_alert[1]}"
        )
        whatsapp_link = f"https://wa.me/{contact_number.strip()}?text={message.replace(' ', '%20')}"
        st.success("Alert message ready. Click below to send via WhatsApp:")
        st.markdown(f"[📲 Send WhatsApp Alert]({whatsapp_link})")
        st.code(message, language=None)

st.divider()
st.caption("Built for Hack Devengers 1.0 — First Response prototype.")
