import streamlit as st
import pandas as pd
import folium
import ee
import time

from streamlit_folium import st_folium
from folium.plugins import HeatMap

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# -------------------------------
# Session State Init
# -------------------------------
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "time" not in st.session_state:
    st.session_state.time = None


# -------------------------------
# Initialize GEE
# -------------------------------
try:
    ee.Initialize(project='urbanheatmapping')
except:
    ee.Authenticate()
    ee.Initialize(project='urbanheatmapping')


# -------------------------------
# UI
# -------------------------------
st.set_page_config(layout="wide")
st.title("🌡 Hyperlocal Urban Heat & Vulnerability Mapping and Alerts System")


# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("temperature_data.csv")

data = load_data()


# -------------------------------
# Train Model
# -------------------------------
@st.cache_resource
def train_model(data):

    features = data[[
        "Latitude_x","Longitude_x","NDVI","NDBI","Year","Time"
    ]]

    target = data["Temp_C"]

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    return model, mean_absolute_error(y_test, pred), r2_score(y_test, pred)


model, mae, r2 = train_model(data)

col1, col2 = st.columns(2)
col1.metric("MAE", f"{mae:.2f} °C")
col2.metric("R² Score", f"{r2:.2f}")


# -------------------------------
# Functions
# -------------------------------
def encode_time(slot):
    return 1 if "Morning" in slot else 2 if "Afternoon" in slot else 3


def classify_heat(temp):
    return "High" if temp > 45 else "Medium" if temp > 40 else "Low"


def calculate_vulnerability(temp, ndvi, ndbi):
    return round((0.4*(temp/50) + 0.3*(1-ndvi) + 0.3*ndbi), 2)


def classify_risk(v):
    return "High Risk" if v > 0.7 else "Moderate Risk" if v > 0.4 else "Low Risk"


def get_indices(lat, lon, date):

    point = ee.Geometry.Point([lon, lat])
    start = ee.Date(str(date))
    end = start.advance(15, 'day')

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(point)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    if collection.size().getInfo() == 0:
        return 0, 0

    image = collection.median()

    nir = image.select("B8")
    red = image.select("B4")
    swir = image.select("B11")

    ndvi = nir.subtract(red).divide(nir.add(red))
    ndbi = swir.subtract(nir).divide(swir.add(nir))

    ndvi_val = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=10
    ).get("B8").getInfo()

    ndbi_val = ndbi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=10
    ).get("B11").getInfo()

    return ndvi_val or 0, ndbi_val or 0


# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.header("Enter Location")

lat = st.sidebar.number_input("Latitude", value=float(data["Latitude_x"].mean()))
lon = st.sidebar.number_input("Longitude", value=float(data["Longitude_x"].mean()))

date = st.sidebar.date_input("Select Date")

time_slot = st.sidebar.selectbox(
    "Select Time",
    ["Morning (9-12)", "Afternoon (12-3)", "Evening (3-6)"]
)

predict_button = st.sidebar.button("Predict")


# -------------------------------
# Heatmap
# -------------------------------
st.subheader("Urban Heat Map")

m = folium.Map(
    location=[data["Latitude_x"].mean(), data["Longitude_x"].mean()],
    zoom_start=11,
    tiles="CartoDB Voyager"
)

HeatMap(
    data[["Latitude_x","Longitude_x","Temp_C"]].values.tolist(),
    radius=35,
    blur=25
).add_to(m)

st_folium(m, width=900)


# -------------------------------
# Prediction
# -------------------------------
if predict_button:

    ndvi, ndbi = get_indices(lat, lon, date)

    prediction = model.predict(pd.DataFrame(
        [[lat, lon, ndvi, ndbi, date.year, encode_time(time_slot)]],
        columns=["Latitude_x","Longitude_x","NDVI","NDBI","Year","Time"]
    ))[0]

    vulnerability = calculate_vulnerability(prediction, ndvi, ndbi)

    st.session_state.prediction = (prediction, vulnerability)
    st.session_state.time = time.time()


# -------------------------------
# Output (ONLY 1 MINUTE)
# -------------------------------
if st.session_state.prediction is not None:

    if time.time() - st.session_state.time < 60:

        prediction, vulnerability = st.session_state.prediction
        risk = classify_risk(vulnerability)

        st.success(f"🌡 Temperature: {prediction:.2f} °C")
        st.metric("Vulnerability Score", vulnerability)
        st.write(f"⚠ Risk Level: {risk}")

        if risk == "High Risk":
            st.error("🚨 Severe Heat Alert")
        elif risk == "Moderate Risk":
            st.warning("⚠ Moderate Risk")
        else:
            st.success("✅ Safe Zone")

        # Map
        result_map = folium.Map(location=[lat, lon], zoom_start=14)

        color = "red" if risk=="High Risk" else "orange" if risk=="Moderate Risk" else "green"

        folium.Marker(
            [lat, lon],
            popup=f"{prediction:.2f} °C",
            icon=folium.Icon(color=color)
        ).add_to(result_map)

        st_folium(result_map, width=900)

    else:
        st.warning("⏳ Result expired! Click Predict again.")