# Sentiment Intelligence Platform (SIP) - Git Commit Guide

This guide provides a step-by-step procedure to reconstruct the commit history of the Sentiment Intelligence Platform (SIP) codebase into 12 logical, production-grade commits matching the React and FastAPI architecture.

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
  * `backend/app/database.py`
  * `backend/app/schemas.py`
* **Purpose**: Establish validation schemas and create connection pooling.
* **Commands**:
  ```bash
  git add backend/app/database.py backend/app/schemas.py
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

### Commit 5: HuggingFace Inferences & Predictions Router
* **Files**:
  * `backend/app/routers/predict_router.py`
* **Purpose**: Build DistilBERT prediction pipeline and single/bulk endpoints.
* **Commands**:
  ```bash
  git add backend/app/routers/predict_router.py
  git commit -m "feat(backend): integrate HuggingFace pipelines with single and bulk prediction routers"
  ```

---

### Commit 6: History Audit & App Gateway Startup
* **Files**:
  * `backend/app/routers/history_router.py`
  * `backend/app/main.py`
* **Purpose**: Construct history log endpoints and wire routers to the main entrypoint.
* **Commands**:
  ```bash
  git add backend/app/routers/history_router.py backend/app/main.py
  git commit -m "feat(backend): build history audit trail endpoints, aggregated metrics and mount main app routers"
  ```

---

### Commit 7: Frontend Baseline & Stylesheet Customizations
* **Files**:
  * `frontend/package.json`
  * `frontend/vite.config.js`
  * `frontend/tailwind.config.js`
  * `frontend/src/index.css`
* **Purpose**: Configure npm package descriptors, Tailwind CSS styling, and Vite project structure.
* **Commands**:
  ```bash
  git add frontend/package.json frontend/vite.config.js frontend/tailwind.config.js frontend/src/index.css
  git commit -m "feat(frontend): configure package definitions, tailwind classes, and baseline build setup"
  ```

---

### Commit 8: API Client and Authorization Context
* **Files**:
  * `frontend/src/services/api.js`
  * `frontend/src/context/AuthContext.jsx`
  * `frontend/src/components/ProtectedRoute.jsx`
* **Purpose**: Build Axios REST clients, request interceptors, and protected auth wrappers.
* **Commands**:
  ```bash
  git add frontend/src/services/api.js frontend/src/context/AuthContext.jsx frontend/src/components/ProtectedRoute.jsx
  git commit -m "feat(frontend): develop axios API client, authentication contexts, and protected route handlers"
  ```

---

### Commit 9: User Registration, Login & Google Chooser
* **Files**:
  * `frontend/src/pages/Login.jsx`
  * `frontend/src/pages/Register.jsx`
* **Purpose**: Implement secure credential validation forms and persistent Google Account Chooser popups.
* **Commands**:
  ```bash
  git add frontend/src/pages/Login.jsx frontend/src/pages/Register.jsx
  git commit -m "feat(frontend): build user login/register pages and implement browser-persistent Google Account Chooser"
  ```

---

### Commit 10: Interactive Dashboard, Analyzer & Logs Pages
* **Files**:
  * `frontend/src/pages/Dashboard.jsx`
  * `frontend/src/pages/Analyzer.jsx`
  * `frontend/src/pages/History.jsx`
* **Purpose**: Integrate Plotly charting widgets, analyzer inputs, attributions, and pagination tables.
* **Commands**:
  ```bash
  git add frontend/src/pages/Dashboard.jsx frontend/src/pages/Analyzer.jsx frontend/src/pages/History.jsx
  git commit -m "feat(frontend): construct metric charts, text analyzer views, and historical logs table"
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
