# Flask API that serves the SuperKart sales forecasting model
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialise the Flask app
superkart_api = Flask("SuperKart Sales Predictor")

# Load the serialized pipeline (preprocessing + tuned Random Forest) once, at startup
model = joblib.load("superkart_model.joblib")

# The 10 features the model expects, in training order
FEATURES = ["Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
            "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
            "Store_Age_Years", "Product_Type_Category"]

# Health check: confirms the API is running
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecasting API!"

# Online inference: one product-store record sent as JSON
@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json()

    # Reject requests with missing features instead of failing inside the model
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the order the model was trained on
    input_df = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = model.predict(input_df)[0]

    return jsonify({"Predicted_Sales": round(float(prediction), 2)})

# Batch inference: a CSV file uploaded under the key "file"
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send a CSV under the key 'file'."}), 400

    input_df = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(input_df[FEATURES])

    # Return {row index: predicted sales}
    return jsonify({int(i): round(float(p), 2) for i, p in zip(input_df.index, predictions)})

# Run locally with: python app.py (in Docker, gunicorn is used instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860)
