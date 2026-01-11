import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import QueueDisplay from './components/QueueDisplay';
import CheckInModal from './components/CheckInModal';
import { startTriage, completeTriage } from './services/api';
import websocketService from './services/websocket';
import './App.css';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [userId, setUserId] = useState(null);
  const [triageComplete, setTriageComplete] = useState(false);
  const [triageResult, setTriageResult] = useState(null);
  const [queuePosition, setQueuePosition] = useState(null);
  const [checkInData, setCheckInData] = useState(null);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    // Initialize WebSocket listeners
    websocketService.on('queue_update', (data) => {
      // Queue updates are handled by QueueDisplay component
      console.log('Queue updated:', data);
    });

    websocketService.on('check_in', (data) => {
      setCheckInData(data);
    });

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const handleStartTriage = async (e) => {
    e.preventDefault();
    // #region agent log
    console.log('[DEBUG] handleStartTriage entry', {name: name||null, phone: phone||null});
    fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.jsx:36',message:'handleStartTriage entry',data:{name:name||null,phone:phone||null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,B,C,D'})}).catch(()=>{});
    // #endregion
    try {
      // #region agent log
      console.log('[DEBUG] calling startTriage', {name: name||null, phone: phone||null});
      fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.jsx:39',message:'calling startTriage',data:{name:name||null,phone:phone||null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,B,C,D'})}).catch(()=>{});
      // #endregion
      const response = await startTriage(name || null, phone || null);
      // #region agent log
      console.log('[DEBUG] startTriage success', response);
      fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.jsx:42',message:'startTriage success',data:{sessionId:response.session_id,userId:response.user_id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,B,C,D'})}).catch(()=>{});
      // #endregion
      setSessionId(response.session_id);
      setUserId(response.user_id);
      setShowWelcome(false);
      
      // Connect WebSocket
      websocketService.connect(response.session_id);
    } catch (error) {
      // #region agent log
      console.log('[DEBUG] handleStartTriage error caught', {errorMessage: error.message, errorStack: error.stack, errorName: error.name, responseStatus: error.response?.status, responseData: error.response?.data, errorCode: error.code, requestURL: error.config?.url});
      fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.jsx:47',message:'handleStartTriage error caught',data:{errorMessage:error.message,errorStack:error.stack,errorName:error.name,responseStatus:error.response?.status,responseData:error.response?.data,errorCode:error.code,requestURL:error.config?.url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,B,C,D,E'})}).catch(()=>{});
      // #endregion
      console.error('Error starting triage:', error);
      alert('Failed to start triage. Please try again.');
    }
  };

  const handleCompleteTriage = async () => {
    if (!sessionId) return;

    try {
      const result = await completeTriage(sessionId);
      setTriageResult(result);
      setTriageComplete(true);
      setQueuePosition(result.queue_position);
      
      if (result.emergency) {
        alert('EMERGENCY DETECTED: ' + result.care_recommendation);
      }
    } catch (error) {
      console.error('Error completing triage:', error);
      alert('Failed to complete triage. Please try again.');
    }
  };

  const handleCloseCheckIn = () => {
    setCheckInData(null);
  };

  return (
    <div className="app">
      {showWelcome ? (
        <div className="welcome-screen">
          <div className="welcome-card">
            <h1>MediQueue</h1>
            <p className="subtitle">AI-Powered Hospital Triage System</p>
            <form onSubmit={handleStartTriage} className="welcome-form">
              <input
                type="text"
                placeholder="Your Name (Optional)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="welcome-input"
              />
              <input
                type="tel"
                placeholder="Phone Number (Optional)"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="welcome-input"
              />
              <button type="submit" className="start-button">
                Start Triage Assessment
              </button>
            </form>
          </div>
        </div>
      ) : (
        <div className="app-container">
          <div className="app-header">
            <h1>MediQueue</h1>
            {triageComplete && triageResult && (
              <div className="triage-summary">
                <div className="summary-item">
                  <span className="summary-label">Severity:</span>
                  <span className="summary-value">
                    {triageResult.triage_result.severity_score.toFixed(1)}/10
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Status:</span>
                  <span className={`summary-value ${triageResult.emergency ? 'emergency' : ''}`}>
                    {triageResult.emergency ? 'EMERGENCY' : 'In Queue'}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="app-content">
            <div className="chat-section">
              <ChatInterface
                sessionId={sessionId}
                onTriageComplete={handleCompleteTriage}
                disabled={triageComplete}
              />
              {!triageComplete && (
                <button
                  onClick={handleCompleteTriage}
                  className="complete-triage-button"
                >
                  Complete Triage Assessment
                </button>
              )}
              {triageComplete && triageResult && (
                <div className="triage-results">
                  <h3>Assessment Complete</h3>
                  <div className="result-item">
                    <strong>Severity Score:</strong> {triageResult.triage_result.severity_score.toFixed(1)}/10
                  </div>
                  <div className="result-item">
                    <strong>Reasoning:</strong> {triageResult.triage_result.severity_reasoning}
                  </div>
                  <div className="result-item">
                    <strong>Home Guidance:</strong> {triageResult.triage_result.home_guidance}
                  </div>
                  <div className="result-item">
                    <strong>Recommendation:</strong> {triageResult.care_recommendation}
                  </div>
                  {triageResult.misuse_warning && (
                    <div className="misuse-warning">
                      ⚠️ {triageResult.misuse_warning}
                    </div>
                  )}
                </div>
              )}
            </div>

            {triageComplete && (
              <div className="queue-section">
                <QueueDisplay
                  sessionId={sessionId}
                  userId={userId}
                  queuePosition={queuePosition}
                />
              </div>
            )}
          </div>

          {checkInData && (
            <CheckInModal
              sessionId={sessionId}
              checkInData={checkInData}
              onClose={handleCloseCheckIn}
            />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
