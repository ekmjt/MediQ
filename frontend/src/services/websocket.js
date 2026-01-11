import ReconnectingWebSocket from 'reconnecting-websocket';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.callbacks = {
      queue_update: [],
      check_in: [],
    };
  }

  connect(sessionId) {
    const wsUrl = import.meta.env.VITE_WS_URL || `ws://localhost:8000/ws/${sessionId}`;
    this.ws = new ReconnectingWebSocket(wsUrl);

    this.ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    });

    this.ws.addEventListener('open', () => {
      console.log('WebSocket connected');
    });

    this.ws.addEventListener('error', (error) => {
      console.error('WebSocket error:', error);
    });

    this.ws.addEventListener('close', () => {
      console.log('WebSocket disconnected');
    });
  }

  handleMessage(data) {
    const { type } = data;
    if (this.callbacks[type]) {
      this.callbacks[type].forEach((callback) => callback(data));
    }
  }

  on(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event].push(callback);
    }
  }

  off(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event] = this.callbacks[event].filter((cb) => cb !== callback);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default new WebSocketService();

