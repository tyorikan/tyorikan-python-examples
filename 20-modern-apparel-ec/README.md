# Modern Apparel EC (Spanner + FastAPI + React)

A scalable, decoupled E-commerce platform inspired by modern apparel sites.

## Tech Stack
- **Frontend**: React, Vite, TypeScript, Tailwind CSS (v3), React Query
- **Backend**: FastAPI (Python), Spanner (Emulator)
- **Database**: Google Cloud Spanner

## Directory Structure
- `backend/`: FastAPI application
- `frontend/`: React application

## Local Development

### Prerequisites
- Docker (for Spanner Emulator)
- Python 3.10+
- Node.js 18+

### Setup & Run
1. **Start Spanner Emulator**:
   ```bash
   make spanner-up
   ```
   > **Note for Podman Users**: If `docker` is an alias for `podman`, `make` might fail. 
   > Please run `podman-compose up -d` (or `podman compose up -d`) directly.

2. **Initialize Database** (First time only):
   ```bash
   # Install backend deps
   pip install -r backend/requirements.txt
   # Run migration
   python backend/scripts/migrate.py
   ```

3. **Start Backend**:
   ```bash
   # The Makefile automatically sets SPANNER_EMULATOR_HOST=localhost:9010
   make backend
   ```
   Or manually:
   ```bash
   export SPANNER_EMULATOR_HOST=localhost:9010
   export GOOGLE_CLOUD_PROJECT=test-project
   export SPANNER_INSTANCE=test-instance
   export SPANNER_DATABASE=test-database
   cd backend && uvicorn app.main:app --reload
   ```
   Access API Docs at: http://localhost:8000/docs

4. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   make frontend
   # Or directly: npm run dev
   ```
   Access App at: http://localhost:5173

### Testing
- Backend: `PYTHONPATH=backend pytest backend/tests/test_products.py`
