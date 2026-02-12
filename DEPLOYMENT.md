# Deployment Guide

Your Community Management System is ready for deployment! This guide explains how to run the application in production mode.

The application allows you to serve both the Backend API (FastAPI) and the Frontend App (Vue.js) from a single Python server.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)

## Step 1: Build the Frontend

First, you need to compile the Vue.js frontend into static files that the backend can serve.

1. Open a terminal in `h5-app` directory:
   ```bash
   cd h5-app
   ```
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Build the production assets:
   ```bash
   npm run build
   ```
   *This creates a `dist` folder with the compiled application.*

## Step 2: Prepare the Backend

1. Return to the root directory:
   ```bash
   cd ..
   ```
2. Create and activate a Virtual Environment (Recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 3: Run the Server

Start the application using Uvicorn (an ASGI server). Do **not** run `python app.py` as that launches the prototype Streamlit interface.

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Step 4: Access the Application

Open your browser and navigate to:
[http://localhost:8000/](http://localhost:8000/)

You will see the H5 App home page. Redirects (e.g. login) will work automatically.

## Deployment to Cloud (e.g., Render/Railway)

1. **Build Command**: `cd h5-app && npm install && npm run build && cd .. && pip install -r requirements.txt`
2. **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## Production Readiness Checklist (Before Verify)

- [x] **Database**: Configured to use SQLite (`community_app.db`).
    > **⚠️ IMPORTANT for Cloud Deployment (Render/Railway/etc.)**:
    > Cloud platforms often reset the file system on every restart.
    > You **MUST** add a **Persistent Disk (Volume)** and mount it to the application path to save your database file.
    > Otherwise, all data will be lost when the app restarts.

- [ ] **Security Keys**: Change the `SECRET_KEY` in `app.py` or use environment variables.
- [ ] **Admin Password**: The default admin password is set in `create_admin.py`. Change it immediately after deployment.
- [ ] **HTTPS**: Ensure your hosting platform provides SSL (most like Render/Vercel do automatically).
- [ ] **CORS**: In `app.py`, update `allow_origins=["*"]` to your specific domain for better security.
