from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
import pandas as pd
import os

app = FastAPI(title="Penguin ML API", description="API for predicting penguin species")

model_name = "PenguinModel"
model_version = "latest"

try:
    # Load model from MLflow registry
    model_uri = f"models:/{model_name}/{model_version}"
    print(f"Loading model from: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Defining the input data schema
class PenguinData(BaseModel):
    island: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Penguin ML API. Send a POST request to /predict for predictions."}

@app.post("/predict")
def predict(data: PenguinData):
    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded. Train and register the model first.")
    
    # Convert input to dataframe
    df = pd.DataFrame([data.dict()])
    
    # Make prediction
    try:
        prediction = model.predict(df)
        return {"prediction": str(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")
