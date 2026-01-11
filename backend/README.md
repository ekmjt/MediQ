# MediQueue Backend

FastAPI backend for the MediQueue triage system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./backend/database.db
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Database

The database is automatically initialized on first run. SQLite database file will be created at `backend/database.db`.

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

