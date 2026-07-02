from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
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