import streamlit as st
import folium
from streamlit_folium import st_folium

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

# ---------- SAMPLE NEARBY HELP LOCATIONS ----------
# Replace these with real coordinates near your demo city if you want it more accurate.
NEARBY_HELP = [
    {"name": "City General Hospital", "lat": 12.9716, "lon": 77.5946, "type": "Hospital"},
    {"name": "Central Police Station", "lat": 12.9750, "lon": 77.6000, "type": "Police"},
    {"name": "Fire Station 4", "lat": 12.9700, "lon": 77.5900, "type": "Fire"},
]

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

# ---------- STEP 3: MAP OF NEARBY HELP ----------
st.subheader("3. Nearby help")

# Center map on the average of sample locations (swap with real user location later if you add geolocation)
center_lat = sum(p["lat"] for p in NEARBY_HELP) / len(NEARBY_HELP)
center_lon = sum(p["lon"] for p in NEARBY_HELP) / len(NEARBY_HELP)

m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

icon_map = {"Hospital": "plus", "Police": "shield", "Fire": "fire"}
for place in NEARBY_HELP:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=f"{place['name']} ({place['type']})",
        tooltip=place["name"],
        icon=folium.Icon(color="red", icon=icon_map.get(place["type"], "info-sign")),
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
        message = (
            f"EMERGENCY ALERT: {emergency_type} in progress. "
            f"I need help. My approximate location: "
            f"https://www.google.com/maps?q={center_lat},{center_lon}"
        )
        # WhatsApp deep link - no API key or backend needed
        whatsapp_link = f"https://wa.me/{contact_number.strip()}?text={message.replace(' ', '%20')}"
        st.success("Alert message ready. Click below to send via WhatsApp:")
        st.markdown(f"[📲 Send WhatsApp Alert]({whatsapp_link})")
        st.code(message, language=None)

st.divider()
st.caption("Built for Hack Devengers 1.0 — First Response prototype.")
