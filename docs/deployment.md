# Deployment

## Overview
Deployment is the final stage in the machine learning lifecycle, where trained and validated models are integrated into production environments to deliver business value. This phase transforms a model from an experimental project into an operational system that can generate predictions on new data, often in real-time.

## Key Components

### Hosting Options
- **Cloud Platforms**: AWS SageMaker, Google AI Platform, Azure ML.
- **On-Premises Servers**: Self-managed infrastructure.
- **Edge Devices**: Deployment on IoT devices, mobile phones, embedded systems.
- **Hybrid Solutions**: Combination of cloud and on-premises deployments.

### Input/Output Handling
- **API Development**: RESTful APIs, GraphQL, gRPC.
- **Batch Processing**: Scheduled jobs for large-scale inference.
- **Real-time Inference**: Stream processing for immediate predictions.
- **Request/Response Formatting**: Data serialization, schema validation.
- **Error Handling**: Graceful failure modes, fallback strategies.

### Dependency Management
- **Containerization**: Docker, Kubernetes for environment isolation.
- **Environment Management**: Virtual environments, package managers.
- **Version Pinning**: Specific library versions to ensure reproducibility.
- **Asset Management**: Model binary storage and versioning.

### Production Considerations
- **Scaling**: Horizontal/vertical scaling, load balancing.
- **Performance Optimization**: Model quantization, distillation, pruning.
- **Monitoring**: Tracking predictions, resource usage, drift detection.
- **Logging**: Structured logs for debugging and audit trails.
- **Security**: Access controls, encryption, vulnerability management.
- **Compliance**: Meeting regulatory requirements (GDPR, HIPAA, etc.).

### CI/CD for ML
- **Automated Testing**: Model quality, performance, security.
- **Model Registry**: Tracking model versions and artifacts.
- **Pipeline Automation**: Automating deployment processes.
- **Rollback Strategies**: Safely reverting to previous versions.
- **A/B Testing**: Comparing model versions in production.

## Best Practices
1. **Start Simple**: Begin with straightforward deployment before scaling.
2. **Monitor Everything**: Track model performance, system health, and user feedback.
3. **Version Control**: Manage models and infrastructure as code.
4. **Document APIs**: Clear documentation for all interfaces.
5. **Plan for Failure**: Implement failover and recovery strategies.
6. **Test Thoroughly**: Verify model behavior in production-like conditions.
7. **Automate Deployment**: Implement CI/CD pipelines for reliable updates.
8. **Consider User Experience**: Balance technical requirements with usability.

## Tools & Technologies
- **Model Serving**: TensorFlow Serving, TorchServe, ONNX Runtime, Triton.
- **Containers**: Docker, Kubernetes, ECS.
- **ML Platforms**: MLflow, Kubeflow, BentoML, Seldon Core.
- **Monitoring**: Prometheus, Grafana, CloudWatch, New Relic.
- **API Frameworks**: Flask, FastAPI, Django REST, Spring Boot.
- **Orchestration**: Airflow, Prefect, Luigi.

## Implementation Example
```python
# Example: Model deployment using FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
import logging
import uvicorn
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define input schema
class PredictionInput(BaseModel):
    features: list
    request_id: str = None

# Define output schema
class PredictionOutput(BaseModel):
    prediction: int
    probability: float
    prediction_time: str
    request_id: str = None

# Initialize FastAPI
app = FastAPI(
    title="ML Model API",
    description="API for making predictions with a trained machine learning model",
    version="1.0.0"
)

# Global variables
MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")
model = None

# Startup event to load model
@app.on_event("startup")
async def load_model():
    global model
    try:
        logger.info(f"Loading model from {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise RuntimeError(f"Failed to load model: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

# Prediction endpoint
@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Log request
    request_id = input_data.request_id or datetime.now().strftime("%Y%m%d%H%M%S%f")
    logger.info(f"Prediction request received - ID: {request_id}")
    
    try:
        # Validate input
        features = np.array(input_data.features).reshape(1, -1)
        if features.shape[1] != model.n_features_in_:
            raise HTTPException(
                status_code=400, 
                detail=f"Model expects {model.n_features_in_} features, but {features.shape[1]} were provided"
            )
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0].max())
        
        # Log and return result
        logger.info(f"Prediction successful - ID: {request_id}, Result: {prediction}")
        return PredictionOutput(
            prediction=prediction,
            probability=probability,
            prediction_time=datetime.now().isoformat(),
            request_id=request_id
        )
    
    except Exception as e:
        logger.error(f"Error making prediction - ID: {request_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the API (for development)
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

## Docker Deployment Example
```dockerfile
# Dockerfile for ML model deployment
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and application code
COPY model.joblib .
COPY app.py .

# Expose port
EXPOSE 8000

# Set environment variables
ENV MODEL_PATH=model.joblib
ENV LOG_LEVEL=INFO

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Kubernetes Deployment Example
```yaml
# kubernetes_deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-api
  labels:
    app: ml-model-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-api
  template:
    metadata:
      labels:
        app: ml-model-api
    spec:
      containers:
      - name: ml-model-api
        image: ml-model-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "500Mi"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        env:
        - name: MODEL_PATH
          value: "/app/model.joblib"
        - name: LOG_LEVEL
          value: "INFO"
---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-api
spec:
  selector:
    app: ml-model-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Monitoring Setup Example
```python
# Example: Model monitoring with Prometheus metrics
from fastapi import FastAPI
import joblib
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Load model
model = joblib.load("model.joblib")

# Define Prometheus metrics
PREDICTION_COUNTER = Counter(
    "ml_prediction_total", 
    "Number of model predictions", 
    ["model_version", "prediction"]
)
PREDICTION_LATENCY = Histogram(
    "ml_prediction_latency_seconds", 
    "Time spent processing prediction", 
    ["model_version"]
)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

@app.post("/predict")
async def predict(features: list):
    model_version = "v1.0"
    
    with PREDICTION_LATENCY.labels(model_version=model_version).time():
        # Make prediction
        prediction = model.predict([features])[0]
    
    # Count prediction by class
    PREDICTION_COUNTER.labels(
        model_version=model_version,
        prediction=str(prediction)
    ).inc()
    
    return {"prediction": int(prediction)}

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

## References
- [Evaluate Performance](evaluate_performance.md) - Previous step to ensure model quality
- [Hyperparameter Tuning](hyperparameter_tuning.md) - Related step for model optimization
- [Data Acquisition](data_acquisition.md) - Related for data feedback loops in deployed systems
- [MLOps Best Practices](https://ml-ops.org/) - External resource
- [TensorFlow Serving Documentation](https://www.tensorflow.org/tfx/guide/serving) - External resource
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - External resource
- [Kubernetes for ML Deployments](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) - External resource
