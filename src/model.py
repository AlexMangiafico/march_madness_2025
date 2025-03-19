from sklearn.ensemble import RandomForestClassifier
import joblib

def save_model_data(model, features, scaler, path: str):
    """Save trained model to a file."""
    model_data = {
        "model": model,
        "features": features,
        "scaler": scaler
    }
    joblib.dump(model_data, path)

def load_model_data(path: str):
    """Load model from file."""
    return joblib.load(path)