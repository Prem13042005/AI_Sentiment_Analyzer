# Sentiment Intelligence Platform (SIP) 🧠

Sentiment Intelligence Platform is an enterprise-grade NLP analytics dashboard and REST API gateway designed for analyzing customer reviews, feedback forms, and user-generated text at scale.

SIP integrates classical deep learning sequence architectures (BiLSTM, GRU, CNN) alongside state-of-the-art Transformer architectures (DistilBERT) to provide real-time predictions, bulk CSV data annotation, and local explainability insights (LIME and Attention weights visualization).

---

## 🏛️ System Architecture

```text
       ┌─────────────────────────────────────────────────────────┐
       │                  Streamlit UI Frontend                  │
       └────────────────────────────┬────────────────────────────┘
                                    │ HTTP Requests
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                   FastAPI API Gateway                   │
       └──────┬──────────────────────┬─────────────────────┬─────┘
              │                      │                     │
              ▼                      ▼                     ▼
       ┌──────────────┐       ┌──────────────┐      ┌──────────────┐
       │  ML models   │       │ PostgreSQL / │      │  Experiment  │
       │ (TF & Torch) │       │ SQLite DB    │      │   Tracker    │
       └──────────────┘       └──────────────┘      └──────────────┘
```

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit, Plotly, Pandas, HSL custom CSS modules
- **Backend API**: FastAPI, Uvicorn, Pydantic validation
- **NLP / ML Frameworks**: TensorFlow/Keras, PyTorch, Hugging Face Transformers, Scikit-learn
- **Database**: PostgreSQL / SQLite (with automated SQLAlchemy connection fallback)
- **Experiment Auditor**: MLflow
- **Container Orchestration**: Docker, Docker Compose

---

## 🚀 Quick Start (Local Setup)

Follow these steps to run the complete workspace locally.

### 1. Set Up Environment
Ensure you have Python 3.10+ installed. Clone the repository and initialize a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Bootstrap ML Models
SIP includes an automated compiler script that builds and trains the deep learning models on a small local corpus and caches HuggingFace tokenizers:
```bash
python backend/app/utils/train_models.py
```
This command compiles:
- **BiLSTM** weights
- **GRU with Attention** weights
- **CNN-LSTM** weights
- **DistilBERT** pre-trained models cache
- Accuracy benchmark logs

### 4. Run FastAPI Backend
Launch the API server locally:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to view the interactive Swagger API documentation.

### 5. Run Streamlit Frontend
In a new terminal window:
```bash
streamlit run frontend/app.py
```
The client dashboard is now available at [http://localhost:8501](http://localhost:8501).

---

## 🐳 Docker Deployment

To launch the complete enterprise environment (FastAPI Backend, Streamlit Frontend, and a dedicated PostgreSQL database container) running concurrently:

### 1. Build and Run Container Suite
```bash
docker-compose up --build
```

### 2. Services Bindings
- **Client Frontend UI**: `http://localhost:8501`
- **REST API Gateway**: `http://localhost:8000`
- **Postgres Database**: `localhost:5432`

---

## 🎯 Model Architectures

1. **Bidirectional LSTM**: Embedding $\to$ BiLSTM(128) $\to$ Dropout $\to$ Dense(64) $\to$ Output
2. **GRU with Attention**: Embedding $\to$ GRU(128) $\to$ Attention Layer $\to$ Dense $\to$ Output
3. **CNN-LSTM**: Embedding $\to$ Conv1D $\to$ MaxPooling $\to$ LSTM $\to$ Dense $\to$ Output
4. **DistilBERT**: Standard distilled Transformer fine-tuned on the SST-2 sentiment classification dataset.
5. **Ensemble Model**: Weighted vote averaging prediction outputs across all active classifiers.

---

## 🕵️ Explainable AI (XAI) Methods

SIP implements two diagnostic explainability mechanisms:
- **Local Interpretable Model-Agnostic Explanations (LIME)**: Perturbs input text randomly, calculates model outputs, and fits a Ridge regression model to calculate word-level sentiment attribution highlights.
- **Attention Heatmaps**: Extracts alignment vectors from the custom recurrent GRU Attention Layer, showing word-level classification focus.
