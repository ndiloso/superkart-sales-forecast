# Streamlit UI for SuperKart sales forecasting; calls the Flask backend for predictions
import os
import requests
import pandas as pd
import streamlit as st

# Backend URL: inside Docker, this is the backend container's name on the shared network
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("🛒 SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

tab_single, tab_batch = st.tabs(["Single prediction", "Batch prediction"])

# ---------- Online (single) prediction ----------
with tab_single:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product weight", min_value=0.0, max_value=30.0, value=12.66, step=0.1)
        product_mrp = st.number_input("Product MRP", min_value=1.0, max_value=500.0, value=117.08, step=1.0)
        product_allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                                 value=0.027, step=0.001, format="%.3f")
    with col2:
        product_sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = st.selectbox("Product group (ID prefix)", ["FD", "NC", "DR"],
                                       help="FD = Food, NC = Non-Consumable, DR = Drinks")
        product_type_category = st.selectbox("Product category", ["Perishables", "Non Perishables"])

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                 "Departmental Store", "Food Mart"])
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"])
    with col4:
        store_city = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"])
        store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    if st.button("Predict sales", type="primary"):
        # Payload keys must match the feature names the API expects
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted sales: {response.json()['Predicted_Sales']:,.2f}")
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ---------- Batch prediction ----------
with tab_batch:
    st.write("Upload a CSV with the 10 model features to get predictions for every row.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write("Preview:", batch_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"))},
                    timeout=60,
                )
                if response.status_code == 200:
                    preds = response.json()
                    # JSON keys come back as strings ("0", "1", ...)
                    batch_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(batch_df))]
                    st.success(f"Predictions generated for {len(batch_df)} rows.")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions", batch_df.to_csv(index=False),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
