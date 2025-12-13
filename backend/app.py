import pandas as pd
import joblib
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import numpy as np
import io


model = joblib.load('final_model.pkl')
app = FastAPI()


class InputData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int  
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

@app.get("/")
def read_root():
    return {"message": "Customer Churn Prediction API"}

@app.post("/predict")
def predict_churn(data: InputData):
    if model is None:
        return {"error": "Model could not be loaded."}
    
    data_dict = data.model_dump()
    df = pd.DataFrame([data_dict])
    
    try:
        prediction = model.predict(df)
        probability = model.predict_proba(df)[:, 1] 
        result = "WILL CHURN" if prediction[0] == 1 else "WILL STAY"
        return {
            "prediction": result,
            "probability": float(probability[0])
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/predict-batch")
async def predict_batch(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    try:
        
        predictions = model.predict(df)
        probabilities = model.predict_proba(df)[:, 1]
        
     
        df['Churn_Prediction'] = ["Yes" if p == 1 else "No" for p in predictions]
        df['Churn_Probability'] = probabilities
        
     
        risky_customers = df[df['Churn_Prediction'] == 'Yes']
        
     
        stream = io.StringIO()
        risky_customers.to_csv(stream, index=False)
        
    
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=at_risk_customers_report.csv"
        return response

    except Exception as e:
        return {"error": str(e), "message": "CSV format or column names may be incorrect."}