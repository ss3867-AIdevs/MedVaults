# Paillier PHE-based FastAPI Secure Inference Application

## Overview
This application provides a secure inference mechanism using the Paillier homomorphic encryption (PHE) scheme within a FastAPI framework. It allows users to submit encrypted data and receive encrypted predictions from a machine learning model.

## Installation
Ensure you have Python 3.8+ and FastAPI installed:
```bash
pip install fastapi uvicorn pycryptodome
```

## Implementation
This FastAPI application exposes two main endpoints:
1. `/encrypt` - Encrypts data using Paillier encryption.
2. `/predict` - Accepts encrypted data and returns encrypted predictions.

### Main file: `main.py`
```python
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from phe import paillier

app = FastAPI()

# Generate Paillier public and private keys
public_key, private_key = paillier.generate_paillier_keypair()

class EncryptionInput(BaseModel):
    data: list

class PredictionOutput(BaseModel):
    encrypted_prediction: str

@app.post("/encrypt")
async def encrypt(input: EncryptionInput):
    encrypted_data = [public_key.encrypt(x) for x in input.data]
    return {'encrypted_data': [enc.ciphertext() for enc in encrypted_data]}

@app.post("/predict", response_model=PredictionOutput)
async def predict(encrypted_data: EncryptionInput):
    # Decrypt input data for prediction
    decrypted_data = [private_key.decrypt(paillier.EncryptedNumber(int(c))) for c in encrypted_data.data]
    # Example: simple prediction (could be a model inference)
    predictions = [2 * x for x in decrypted_data]  # Replace with your model inference
    # Encrypt predictions before returning
    encrypted_predictions = [public_key.encrypt(pred) for pred in predictions]
    return PredictionOutput(encrypted_prediction=[enc.ciphertext() for enc in encrypted_predictions])

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the Application
To run the application, execute:
```bash
uvicorn main:app --reload
```

## Conclusion
This FastAPI application allows secure predictions using homomorphic encryption, enhancing privacy in sensitive data environments.