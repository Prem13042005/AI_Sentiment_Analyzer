# Sentix AI - Sentiment Intelligence Platform 🧠

An enterprise-grade sentiment analysis platform and REST API gateway featuring advanced deep learning models, LIME explainability, and multi-user tracking.

The client is built using a modern **React & Tailwind CSS** frontend, which communicates with a fast **FastAPI** python backend and a **PostgreSQL** database.

---

## 🤖 Model Details

- **Architecture**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Dataset**: Stanford Sentiment Treebank (SST-2) validation set
- **Performance**: **91.4% F1 Score** (Accuracy: 91.2%, inference latency: ~48ms on CPU)

---

## ⚡ Quick Start (Docker Compose)

Launch the entire stack (PostgreSQL, FastAPI backend, and React frontend) using three simple commands:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/sentiment-intelligence-platform.git
cd sentiment-intelligence-platform

# 2. Setup your local environment file
cp .env.example .env

# 3. Build and launch all services
docker-compose up --build
```

- **Frontend Portal**: `http://localhost` (Port 80)
- **API Swagger Documentation**: `http://localhost:8000/docs`

---

## 🛠️ Local Development Setup

To run the API and Client services directly on your host machine:

### 1. Backend Setup
Ensure you have Python 3.10+ installed.
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run the FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup
Ensure you have Node.js 18+ installed.
```bash
cd frontend
npm install
npm run dev
```
- **Local Dev Server**: `http://localhost:5173`

---

## 🔑 Demo Credentials

For testing and review, use the following pre-configured account details:
- **Username**: `demo`
- **Password**: `demo123`

---

## 📊 API Reference

| Endpoint | Method | Authentication | Description |
| :--- | :---: | :---: | :--- |
| `/api/v1/auth/register` | `POST` | None | Register a new operator |
| `/api/v1/auth/login` | `POST` | None | Authenticate credentials and get JWT token |
| `/api/v1/auth/google` | `POST` | None | Register or authenticate via Google OAuth |
| `/api/v1/auth/me` | `GET` | Bearer Token | Retrieve currently logged-in user profile |
| `/api/v1/predict` | `POST` | Bearer Token | Classify sentiment of a single review |
| `/api/v1/predict/bulk` | `POST` | Bearer Token | Classify sentiment of multiple text inputs |
| `/api/v1/history/` | `GET` | Bearer Token | Fetch paginated prediction logs |
| `/api/v1/history/stats` | `GET` | Bearer Token | Retrieve aggregate metrics and counts |
| `/api/v1/history/{id}` | `DELETE` | Bearer Token | Delete a specific prediction log |

---

## 🖼️ Application Screenshots

| Landing Portal | Authenticated Dashboard |
| :---: | :---: |
| *Placeholder for Landing Portal* | *Placeholder for Dashboard* |

| Model Analyzer | Prediction History Audit |
| :---: | :---: |
| *Placeholder for Analyzer Page* | *Placeholder for History Page* |
