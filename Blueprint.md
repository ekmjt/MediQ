# MediQueue - Conversational AI Triage System

MediQueue is a conversational AI application that helps streamline the hospital triage process from the comfort of a patient's home. Built for SFU Surge Hackathon.

## Features

- **At-Home Triage Assessment**: Patients use the MediQueue portal to answer questions, and the AI determines severity and assigns priority
- **Dynamic Queue Management**: Balances medical urgency with wait time for fair queue management
- **Home Guidance**: Provides initial advice on what patients can do at home while waiting
- **Periodic Check-ins**: Checks in every 30 minutes to ensure patient condition stability
- **User-Initiated Position Changes**: Users can voluntarily lower their queue position
- **Misuse Prevention**: Tracks and flags users who misrepresent their condition

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: Python + FastAPI
- **AI**: Google Gemini API
- **Database**: SQLite
- **Real-time**: WebSockets

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./backend/database.db
```

5. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend at `http://localhost:8000`.

## Usage

1. **Start Triage**: Enter your name and phone (optional) and click "Start Triage Assessment"
2. **Conversation**: Chat with the AI about your symptoms
3. **Complete Triage**: Click "Complete Triage Assessment" when done
4. **View Queue**: See your position in the queue and wait time
5. **Check-ins**: Respond to periodic check-ins about your condition
6. **Lower Position**: Optionally lower your position if your condition improves

## API Endpoints

### HTTP Endpoints

- `POST /api/start-triage` - Begin conversation, create user session
- `POST /api/message` - Send message to Gemini, get response
- `POST /api/complete-triage` - Finalize triage, add to queue
- `GET /api/queue` - Get current queue state
- `POST /api/lower-position` - User-initiated position change
- `POST /api/check-in-response` - Respond to periodic check-in

### WebSocket

- `WS /ws/{session_id}` - Real-time queue position updates and check-in notifications

## Project Structure

```
mediqueue/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routes, WebSocket handlers
│   │   ├── models.py            # SQLite models
│   │   ├── gemini_service.py   # Gemini API integration
│   │   ├── queue_manager.py     # Queue logic
│   │   ├── triage_logic.py      # Severity scoring
│   │   └── scheduler.py         # Periodic check-in scheduler
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── components/          # React components
│   │   └── services/            # API and WebSocket services
│   └── package.json
└── README.md
```

## Demo Scenarios

1. **Normal Triage**: User with moderate symptoms → Gets priority, sees queue position
2. **Emergency Case**: User reports chest pain → Immediate escalation, high priority
3. **Queue Dynamics**: Show how position changes as others join/leave
4. **Periodic Check-in**: Simulate 30-minute check-in popup
5. **Position Lowering**: User voluntarily moves down queue
6. **Misuse Detection**: Show warning for inconsistent reporting

## Notes

- This is a demo/prototype built for hackathon purposes
- Medical disclaimers apply - this is not a replacement for professional medical advice
- The system uses AI for triage assessment but always prioritizes patient safety
- Emergency cases are flagged immediately for human review

## License

Built for SFU Surge Hackathon 2024
