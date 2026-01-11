import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startTriage = async (name, phone) => {
  // #region agent log
  console.log('[DEBUG] startTriage entry', {name, phone, baseURL: API_BASE_URL, endpoint: '/api/start-triage'});
  fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:12',message:'startTriage entry',data:{name,phone,baseURL:API_BASE_URL,endpoint:'/api/start-triage'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,C,D,E'})}).catch(()=>{});
  // #endregion
  try {
    console.log('[DEBUG] Making axios POST request to', API_BASE_URL + '/api/start-triage');
    const response = await api.post('/api/start-triage', { name, phone });
    // #region agent log
    console.log('[DEBUG] startTriage response received', {status: response.status, data: response.data});
    fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:15',message:'startTriage response received',data:{status:response.status,hasData:!!response.data},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,C,D,E'})}).catch(()=>{});
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    console.log('[DEBUG] startTriage axios error', {errorMessage: error.message, errorCode: error.code, responseStatus: error.response?.status, responseData: error.response?.data, requestURL: error.config?.url, requestMethod: error.config?.method});
    fetch('http://127.0.0.1:7243/ingest/f09626fe-7fc2-456b-86d1-69d0309ffc6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.js:18',message:'startTriage axios error',data:{errorMessage:error.message,errorCode:error.code,responseStatus:error.response?.status,responseData:error.response?.data,requestURL:error.config?.url,requestMethod:error.config?.method},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,C,D,E'})}).catch(()=>{});
    // #endregion
    throw error;
  }
};

export const sendMessage = async (sessionId, content) => {
  const response = await api.post('/api/message', {
    session_id: sessionId,
    content,
  });
  return response.data;
};

export const completeTriage = async (sessionId) => {
  const response = await api.post('/api/complete-triage', {
    session_id: sessionId,
  });
  return response.data;
};

export const getQueue = async () => {
  const response = await api.get('/api/queue');
  return response.data;
};

export const lowerPosition = async (sessionId) => {
  const response = await api.post('/api/lower-position', {
    session_id: sessionId,
  });
  return response.data;
};

export const sendCheckInResponse = async (sessionId, queueEntryId, response) => {
  const response_data = await api.post('/api/check-in-response', {
    session_id: sessionId,
    queue_entry_id: queueEntryId,
    response,
  });
  return response_data.data;
};

