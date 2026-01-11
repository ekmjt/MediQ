# MediQueue - Local Setup Guide

This guide will walk you through setting up the MediQueue application on your local machine.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.8+** - Check with `python --version` or `python3 --version`
- **Node.js 16+** - Check with `node --version`
- **npm** (comes with Node.js) - Check with `npm --version`
- **Google Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Step-by-Step Setup

### Step 1: Clone or Navigate to the Project

If you haven't already, navigate to the project directory:

```bash
cd /path/to/Hackathon
```

### Step 2: Set Up Environment Variables

**IMPORTANT**: Never commit your API keys or sensitive information to version control.

1. Create a `.env` file in the **root directory** of the project (same level as `backend` and `frontend` folders):

```bash
touch .env
```

2. Open the `.env` file in a text editor and add the following:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=sqlite:///./backend/database.db
```

3. Replace `your_actual_gemini_api_key_here` with your actual Google Gemini API key.

**Note**: The `.env` file is already included in `.gitignore` to prevent accidental commits.

### Step 3: Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a Python virtual environment (recommended):

```bash
python3 -m venv venv
```

   Or on Windows:
```bash
python -m venv venv
```

3. Activate the virtual environment:

   **On macOS/Linux:**
```bash
source venv/bin/activate
```

   **On Windows:**
```bash
venv\Scripts\activate
```

   You should see `(venv)` in your terminal prompt when activated.

4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5. Start the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

**Keep this terminal window open** - the backend needs to keep running.

### Step 4: Frontend Setup

Open a **new terminal window** (keep the backend running) and follow these steps:

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in the terminal)

### Step 5: Access the Application

1. Open your web browser
2. Navigate to the frontend URL (usually `http://localhost:5173`)
3. You should see the MediQueue interface

## Quick Start (Using Scripts)

For convenience, you can use the provided startup scripts:

### macOS/Linux:

```bash
chmod +x start.sh
./start.sh
```

### Windows:

```bash
start.bat
```

**Note**: Make sure your `.env` file is set up before running these scripts.

## Verifying the Setup

1. **Backend Check**: Visit `http://localhost:8000/docs` - You should see the FastAPI Swagger documentation
2. **Frontend Check**: Visit `http://localhost:5173` - You should see the MediQueue interface
3. **API Connection**: Try starting a triage assessment in the frontend - it should connect to the backend

## Troubleshooting

### Backend Issues

- **Python version**: Make sure Python 3.8+ is installed: `python3 --version`
- **Virtual environment**: Ensure the virtual environment is activated (you should see `(venv)` in your prompt)
- **Missing API key**: Check that `.env` file exists in the root directory with `GEMINI_API_KEY` set
- **Port already in use**: If port 8000 is busy, change it: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`
- **Dependencies not installing**: Try upgrading pip: `pip install --upgrade pip`

### Frontend Issues

- **Node.js version**: Make sure Node.js 16+ is installed: `node --version`
- **Dependencies failing**: Delete `node_modules` folder and `package-lock.json`, then run `npm install` again
- **Port already in use**: Vite will automatically use the next available port
- **Connection errors**: Make sure the backend is running on port 8000

### Database Issues

- The database (`backend/database.db`) is created automatically on first run
- If you need to reset: Delete `backend/database.db` and restart the backend server
- The database file is already in `.gitignore` and won't be committed

### Environment Variable Issues

- Make sure `.env` file is in the **root directory** (not in `backend/` or `frontend/`)
- Check that there are no spaces around the `=` sign: `GEMINI_API_KEY=your_key` (not `GEMINI_API_KEY = your_key`)
- Restart the backend server after creating or modifying `.env`

## Project Structure

```
Hackathon/
├── backend/
│   ├── app/              # Backend application code
│   ├── venv/             # Python virtual environment (gitignored)
│   ├── database.db       # SQLite database (gitignored)
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/              # Frontend source code
│   ├── node_modules/     # Node.js dependencies (gitignored)
│   └── package.json      # Node.js dependencies config
├── .env                  # Environment variables (gitignored)
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── Blueprint.md         # Project blueprint and documentation
└── start.sh / start.bat # Startup scripts
```

## Security Notes

- **Never commit** `.env` files or API keys
- The `.gitignore` file is configured to exclude:
  - `.env` files
  - Database files (`*.db`, `*.sqlite`)
  - Virtual environments (`venv/`, `env/`)
  - Node modules (`node_modules/`)
  - Other sensitive or generated files

## Next Steps

Once setup is complete, you can:
- Start using the application (see `Blueprint.md` for usage details)
- Explore the API documentation at `http://localhost:8000/docs`
- Review the project blueprint in `Blueprint.md`

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the `Blueprint.md` for project details
3. Check the backend logs in the terminal running `uvicorn`
4. Check the browser console for frontend errors

## License

Built for SFU Surge Hackathon 2024
