# Quick Setup Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Step-by-Step Setup

### 1. Clone/Navigate to Project
```bash
cd /Users/admin/Hackathon
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=sqlite:///./backend/database.db
```

### 3. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup (in a new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 5. Access the Application

Open your browser and go to: `http://localhost:3000`

## Quick Start (Using Scripts)

### macOS/Linux:
```bash
chmod +x start.sh
./start.sh
```

### Windows:
```bash
start.bat
```

## Troubleshooting

### Backend Issues
- Make sure Python 3.8+ is installed: `python --version`
- Make sure virtual environment is activated
- Check that `.env` file exists with valid `GEMINI_API_KEY`
- Check port 8000 is not already in use

### Frontend Issues
- Make sure Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again if dependencies fail
- Check port 3000 is not already in use

### Database Issues
- The database will be created automatically on first run
- If you need to reset, delete `backend/database.db` and restart the backend

## Testing the Application

1. **Start Triage**: Enter name/phone (optional) and click "Start Triage Assessment"
2. **Chat**: Have a conversation about symptoms
3. **Complete**: Click "Complete Triage Assessment"
4. **View Queue**: See your position and wait time
5. **Check-ins**: Wait 30 minutes (or modify scheduler interval for testing) to receive check-in prompts

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Demo Scenarios

1. **Normal Case**: Describe moderate symptoms (e.g., "I have a headache and feel nauseous")
2. **Emergency Case**: Describe severe symptoms (e.g., "I have chest pain and difficulty breathing")
3. **Queue Test**: Open multiple browser tabs/windows to simulate multiple users
4. **Check-in Test**: Modify `backend/app/scheduler.py` to use `minutes=1` instead of `minutes=30` for faster testing

