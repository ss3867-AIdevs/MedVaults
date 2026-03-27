# PHE-based FastAPI Secure Inference Application

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import json
import pickle
from phe import paillier

app = FastAPI()

# Global model and keypair
model = None
public_key = None
private_key = None

# Startup event to load dataset and train the model
@app.on_event('startup')
def load_model():
    global model, public_key, private_key
    # Load Wisconsin Breast Cancer dataset
    url = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/breast-cancer-wisconsin.data'
    df = pd.read_csv(url, header=None)
    X = df.iloc[:, 2:30].values
    y = df.iloc[:, 1].values

    # Train Logistic Regression model
    model = LogisticRegression()
    model.fit(X, y)

    # Generate Paillier keypair for encryption
    public_key, private_key = paillier.new_keypair()

# Request model input data class
class PredictionRequest(BaseModel):
    features: list

# POST /predict endpoint
@app.post('/predict')
def predict(request: PredictionRequest):
    global model, public_key
    if not model:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    # Encrypt features using Paillier public key
    encrypted_features = [public_key.encrypt(feature) for feature in request.features]

    # Perform homomorphic computation (dot product + bias)
    dot_product = sum(encrypted_features[i] * model.coef_[0][i] for i in range(len(encrypted_features)))
    bias = public_key.encrypt(model.intercept_[0])
    encrypted_prediction = dot_product + bias  # Encrypted result

    return {'prediction': str(encrypted_prediction)}

# Test client simulation function
if __name__ == '__main__':
    # Client-side simulation: generate keypair, encrypt features, send request, and decrypt response
    feature_sample = [5.0, 1.7, 1.3, 0.2]  # Sample patient features
    encrypted_sample = [public_key.encrypt(x) for x in feature_sample]
    response = {'prediction': str(encrypted_sample)}  # Simulate server response
    # Simulated decryption of response
    decrypted_prediction = private_key.decrypt(response['prediction'])
    print(f'Decrypted prediction: {decrypted_prediction}')

# Note on Paillier properties: 
# 1. Additive Homomorphism: Given n1 and n2 encrypted by Paillier, n1 + n2 is also
#    an encryption of (x1 + x2) where x1 and x2 are the plaintexts.
# 2. Encryption does not reveal the original data, allowing secure computation on it.
# 3. The dot product calculates in the encrypted domain, ensuring privacy throughout computation.
