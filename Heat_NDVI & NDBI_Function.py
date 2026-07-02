
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
