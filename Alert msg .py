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