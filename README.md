# Sentiment Intelligence Platform (SIP) 🧠

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.2-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-enabled-2496ED.svg)](https://www.docker.com/)

An enterprise-grade sentiment analysis platform and REST API gateway featuring advanced deep learning models, LIME explainability, and multi-user tracking.

## Features
* ✅ **5-model ensemble**: Includes BiLSTM, GRU with Attention, CNN-LSTM, DistilBERT, and a weighted Ensemble consensus model.
* ✅ **Explainable AI**: Real-time word attributions using local surrogate LIME models and recurrent sequence attention weight listings.
* ✅ **JWT User Authentication**: Secure registration, login, state-bound session cookies, and resource role boundaries.
* ✅ **Prediction History Audit**: Full searchable log listing with keyword filters, aggregations, charts, and CSV exporting capabilities.
* ✅ **Bulk CSV Annotation**: Upload dataset batches (up to 100 entries) and predict them simultaneously.
* ✅ **MLflow Experiment Tracking**: Tracks model training metrics and parameters.
* ✅ **One-command Docker Deployment**: Multi-container setup for the frontend, backend API, and a PostgreSQL database.

## Screenshots

Below are references representing key views of the interface:

* **Landing Portal**: A walkthrough of the system, performance benchmarks, and user access gates.
  ![Landing Portal](frontend/assets/screenshots/landing.png)
* **Authenticated Dashboard**: Aggregated summary charts, sentiment shares, activity trends, and recent classifications.
  ![Dashboard Page](frontend/assets/screenshots/dashboard.png)
* **Model Analyzer**: Single text analyzer displaying Attributions (LIME), attention weights, and consensus breakdowns.
  ![Model Analyzer](frontend/assets/screenshots/analyzer.png)
* **Prediction History Audit**: Filterable log records table with deletion controls and CSV export handlers.
  ![History Page](frontend/assets/screenshots/history.png)

## Model Performance

Benchmarks are tracked across the SST-2 sentiment validation set:

| Model | Accuracy | F1 Score | Inference Speed |
| :--- | :---: | :---: | :---: |
| **Ensemble** | 92.1% | 91.9% | 78ms |
| **DistilBERT** | 91.4% | 91.2% | 48ms |
| **BiLSTM** | 85.2% | 84.9% | 12ms |
| **GRU with Attention** | 83.7% | 83.4% | 10ms |
| **CNN-LSTM** | 81.9% | 81.5% | 8ms |

## Quick Start (Docker)

Initialize the platform using Docker Compose (runs PostgreSQL, FastAPI backend, and Streamlit frontend):

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/sentiment-intelligence-platform.git
cd sentiment-intelligence-platform

# 2. Setup your local environment file
cp .env.example .env  # edit database credentials and your JWT secret keys

# 3. Build and launch the container suite
docker-compose up --build
```
* **Client Frontend UI**: `http://localhost:8501`
* **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`

## Quick Start (Local Setup)

To setup and run the API and Client services directly on your host machine:

### 1. Set Up Environment & Install Dependencies
Ensure you have Python 3.10+ installed.
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required modules
pip install -r requirements.txt
```

### 2. Pre-train & Compile Deep Learning Models
Bootstrap Keras neural architectures and cache preprocessor tokenizers:
```bash
python backend/app/utils/train_models.py
```

### 3. Launch Services
Start the FastAPI server:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
In a separate terminal, launch the Streamlit frontend client app:
```bash
streamlit run frontend/app.py
```

## API Reference

### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "operator1", "email": "operator1@example.com", "password": "password_secure_123"}'
```

### 2. User Login (Obtain Token)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=operator1&password=password_secure_123"
```

### 3. Sentiment Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"text": "The new update runs incredibly fast!", "model_name": "ensemble"}'
```

### 4. Bulk Predict
```bash
curl -X POST "http://localhost:8000/api/v1/predict/bulk" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"texts": ["Awesome performance.", "Worst service ever."]}'
```

### 5. Prediction History Logs
```bash
curl -X GET "http://localhost:8000/api/v1/history/?skip=0&limit=10" \
     -H "Authorization: Bearer <access_token>"
```

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── __init__.py           # Database connection and init methods
│   │   ├── middleware/
│   │   │   └── logger.py             # Custom logging middleware
│   │   ├── models/
│   │   │   ├── user.py               # User database table definition
│   │   │   └── analysis.py           # Analysis log database table definition
│   │   ├── routers/
│   │   │   ├── auth_router.py        # /register, /login, /me routes
│   │   │   ├── history_router.py     # /history listings and stats aggregations
│   │   │   └── predict_router.py     # /predict and /predict/bulk ML outputs
│   │   ├── schemas/
│   │   │   └── __init__.py           # Pydantic validation schemas
│   │   ├── utils/
│   │   │   ├── lime_explain.py       # Custom LIME surrogate model logic
│   │   │   ├── mlflow_tracker.py     # MLflow metric audit hook
│   │   │   ├── model_registry.py     # Singleton loader for keras/bert models
│   │   │   ├── preprocess.py         # Text prep and token cleaning
│   │   │   └── train_models.py       # Local training bootsrap script
│   │   ├── auth.py                   # CryptContext pw hashing and JWT validations
│   │   └── main.py                   # FastAPI start gateway, CORS and startup events
│   └── __init__.py
├── frontend/
│   ├── assets/
│   │   └── style.css                 # Custom badges styling rules
│   ├── pages/
│   │   ├── 1_Login.py                # Session authentication page
│   │   ├── 2_Register.py             # User signup page
│   │   ├── 3_Dashboard.py            # Aggregate metrics charts and insights
│   │   ├── 4_Analyzer.py             # Text analyzer and LIME attributions
│   │   ├── 5_History.py              # Paginated run logs list and csv exporter
│   │   ├── 6_Bulk_Upload.py          # Batch CSV file processing tool
│   │   └── 7_About.py                # Tech specifications and diagrams
│   ├── utils/
│   │   ├── api_client.py             # Frontend API request library
│   │   ├── auth_state.py             # Client session states and filter guards
│   │   └── charts.py                 # Plotly visual widgets builders
│   └── app.py                        # Landing gate layout and benchmarks
├── models/
│   ├── bilstm/                       # Saved BiLSTM neural network
│   ├── cnn_lstm/                     # Saved CNN-LSTM neural network
│   ├── distilbert/                   # Cached local transformer weights
│   ├── ensemble/                     # Ensemble weighted votes configuration
│   ├── gru_attention/                # Saved GRU attention network
│   └── benchmarks.json               # Local compile metrics tracking
├── tests/
│   ├── conftest.py                   # Pytest mock libraries and SQLite setups
│   ├── test_auth.py                  # Integration checks for register/login paths
│   ├── test_history.py               # Checks for logs metrics and history edits
│   └── test_predict.py               # Checks for single/bulk predict validations
├── .env.example                      # DB config and token template keys
├── .gitignore                        # Cache, DB, venv paths ignore configurations
├── docker-compose.yml                # Docker orchestrations template
├── Dockerfile.backend                # Containerizer for the FastAPI service
├── Dockerfile.frontend               # Containerizer for the Streamlit service
├── pytest.ini                        # Pytest runtime configuration
├── README.md                         # Main repository user guide
└── requirements.txt                  # Strict production library version pins
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
