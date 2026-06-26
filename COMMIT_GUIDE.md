# Sentiment Intelligence Platform (SIP) - Git Commit Guide

This guide provides a step-by-step procedure to reconstruct the commit history of the Sentiment Intelligence Platform (SIP) codebase into 12 logical, production-grade commits. 

Before starting, initialize a new git repository in the workspace root:
```bash
git init
```

---

### Commit 1: Repository Initialization & Dependency Pinning
* **Files**: `requirements.txt`, `.gitignore`
* **Purpose**: Set up the project baseline and track version configurations.
* **Commands**:
  ```bash
  git add requirements.txt .gitignore
  git commit -m "feat: initialize repository, pin production requirements and add gitignore"
  ```

---

### Commit 2: Core Database Setup & Validation Schemas
* **Files**: 
  * `backend/app/database/__init__.py`
  * `backend/app/schemas/__init__.py`
* **Purpose**: Establish validation schemas and create connection pooling.
* **Commands**:
  ```bash
  git add backend/app/database/__init__.py backend/app/schemas/__init__.py
  git commit -m "feat(backend): configure SQLAlchemy connection pool and define Pydantic v2 schemas"
  ```

---

### Commit 3: SQLAlchemy Models definitions
* **Files**:
  * `backend/app/models/user.py`
  * `backend/app/models/analysis.py`
* **Purpose**: Create relational mappings for authentication and predictions history.
* **Commands**:
  ```bash
  git add backend/app/models/user.py backend/app/models/analysis.py
  git commit -m "feat(backend): create User and Analysis database models with UUID primary keys"
  ```

---

### Commit 4: Password Cryptography & JWT Security Handlers
* **Files**:
  * `backend/app/auth.py`
  * `backend/app/routers/auth_router.py`
* **Purpose**: Implement secure hashing and registration/login endpoints.
* **Commands**:
  ```bash
  git add backend/app/auth.py backend/app/routers/auth_router.py
  git commit -m "feat(backend): implement passlib bcrypt hashing and JWT auth handlers with registration/login endpoints"
  ```

---

### Commit 5: Deep Learning Registry & Inferences
* **Files**:
  * `backend/app/utils/model_registry.py`
  * `backend/app/utils/preprocess.py`
  * `backend/app/utils/lime_explain.py`
  * `backend/app/utils/train_models.py`
  * `backend/app/utils/mlflow_tracker.py`
  * `backend/app/routers/predict_router.py`
* **Purpose**: Build singleton model loader and predict routers with LIME interpretability support.
* **Commands**:
  ```bash
  git add backend/app/utils/model_registry.py backend/app/utils/preprocess.py backend/app/utils/lime_explain.py backend/app/utils/train_models.py backend/app/utils/mlflow_tracker.py backend/app/routers/predict_router.py
  git commit -m "feat(backend): build Singleton ModelRegistry and integrate predict routes with LIME attributions"
  ```

---

### Commit 6: History Audit & App Gateway Startup
* **Files**:
  * `backend/app/routers/history_router.py`
  * `backend/app/middleware/logger.py`
  * `backend/app/main.py`
* **Purpose**: Construct history log endpoints and wire routers to the main entrypoint.
* **Commands**:
  ```bash
  git add backend/app/routers/history_router.py backend/app/middleware/logger.py backend/app/main.py
  git commit -m "feat(backend): build history audit trail endpoints, aggregated metrics and mount main app routers"
  ```

---

### Commit 7: Frontend Landing & Stylesheet Customizations
* **Files**:
  * `frontend/app.py`
  * `frontend/assets/style.css`
* **Purpose**: Create landing view and establish layout themes.
* **Commands**:
  ```bash
  git add frontend/app.py frontend/assets/style.css
  git commit -m "feat(frontend): create main Streamlit landing page layout and inject custom CSS theme styles"
  ```

---

### Commit 8: Frontend Session State & User Gateways
* **Files**:
  * `frontend/utils/api_client.py`
  * `frontend/utils/auth_state.py`
  * `frontend/pages/1_Login.py`
  * `frontend/pages/2_Register.py`
* **Purpose**: Establish API client library and auth screens.
* **Commands**:
  ```bash
  git add frontend/utils/api_client.py frontend/utils/auth_state.py frontend/pages/1_Login.py frontend/pages/2_Register.py
  git commit -m "feat(frontend): implement API client, state manager, and build Login/Register screens"
  ```

---

### Commit 9: Dashboard Reports & Real-Time Classifier views
* **Files**:
  * `frontend/utils/charts.py`
  * `frontend/pages/3_Dashboard.py`
  * `frontend/pages/4_Analyzer.py`
* **Purpose**: Integrate Plotly charting widgets, dashboard screens, and model analyzers.
* **Commands**:
  ```bash
  git add frontend/utils/charts.py frontend/pages/3_Dashboard.py frontend/pages/4_Analyzer.py
  git commit -m "feat(frontend): integrate Plotly visualization utils, metrics dashboard and model analyzer"
  ```

---

### Commit 10: Run Logs Audit & Bulk Dataset Annotation Tools
* **Files**:
  * `frontend/pages/5_History.py`
  * `frontend/pages/6_Bulk_Upload.py`
  * `frontend/pages/7_About.py`
* **Purpose**: Develop bulk CSV processors, log managers, and repository about pages.
* **Commands**:
  ```bash
  git add frontend/pages/5_History.py frontend/pages/6_Bulk_Upload.py frontend/pages/7_About.py
  git commit -m "feat(frontend): create logs audit manager, bulk CSV annotation uploader and info page"
  ```

---

### Commit 11: Multi-Container Docker Infrastructure
* **Files**:
  * `Dockerfile.backend`
  * `Dockerfile.frontend`
  * `docker-compose.yml`
  * `.env.example`
* **Purpose**: Configure multi-container scaling templates and environment examples.
* **Commands**:
  ```bash
  git add Dockerfile.backend Dockerfile.frontend docker-compose.yml .env.example
  git commit -m "infra: construct split backend/frontend Dockerfiles and docker-compose deployment schema"
  ```

---

### Commit 12: Test Suites & Final Documentation
* **Files**:
  * `pytest.ini`
  * `tests/conftest.py`
  * `tests/test_auth.py`
  * `tests/test_predict.py`
  * `tests/test_history.py`
  * `README.md`
* **Purpose**: Configure testing setup, fixtures, write tests, and document the project usage.
* **Commands**:
  ```bash
  git add pytest.ini tests/conftest.py tests/test_auth.py tests/test_predict.py tests/test_history.py README.md
  git commit -m "test & docs: write conftest mocks and integration tests, finalize repository documentation"
  ```
