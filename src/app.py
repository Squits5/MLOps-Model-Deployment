from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# Load the pre-trained model
MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}. Please ensure it exists.")
    # Create a dummy model for demonstration if not found
    class DummyModel:
        def predict(self, features):
            print("Using dummy model for prediction.")
            return [np.mean(f) for f in features]
    model = DummyModel()
    joblib.dump(model, MODEL_PATH) # Save dummy model
except Exception as e:
    print(f"Error loading model: {e}")
    class DummyModel:
        def predict(self, features):
            print("Using dummy model for prediction.")
            return [np.mean(f) for f in features]
    model = DummyModel()
    joblib.dump(model, MODEL_PATH) # Save dummy model

@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json(force=True)
    if "features" not in data:
        return jsonify({"error": "Missing 'features' in request body"}), 400
    
    try:
        features = np.array(data["features"])
        prediction = model.predict(features).tolist()
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

if __name__ == "__main__":
    # For local testing, create a dummy model if it doesn't exist
    if not os.path.exists(MODEL_PATH):
        class SimpleRegressor:
            def predict(self, X):
                return np.sum(X, axis=1) # Simple sum for demonstration
        joblib.dump(SimpleRegressor(), MODEL_PATH)
        print(f"Created a dummy model at {MODEL_PATH} for local testing.")

    app.run(debug=True, host="0.0.0.0", port=5000)
