import React, { useState, useEffect } from 'react';
import { getQueue, lowerPosition } from '../services/api';
import './QueueDisplay.css';

const QueueDisplay = ({ sessionId, userId, queuePosition }) => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadQueue = async () => {
    try {
      const data = await getQueue();
      setQueue(data.queue || []);
    } catch (error) {
      console.error('Error loading queue:', error);
    }
  };

  const handleLowerPosition = async () => {
    if (!window.confirm('Are you sure you want to lower your position in the queue?')) {
      return;
    }

    setLoading(true);
    try {
      await lowerPosition(sessionId);
      await loadQueue();
    } catch (error) {
      console.error('Error lowering position:', error);
      alert('Failed to lower position. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    if (severity >= 9) return '#dc3545'; // Critical - red
    if (severity >= 7) return '#fd7e14'; // High - orange
    if (severity >= 4) return '#ffc107'; // Medium - yellow
    return '#28a745'; // Low - green
  };

  const getSeverityLabel = (severity) => {
    if (severity >= 9) return 'Critical';
    if (severity >= 7) return 'High';
    if (severity >= 4) return 'Medium';
    return 'Low';
  };

  const userQueueEntry = queue.find((entry) => entry.user_id === userId);

  return (
    <div className="queue-display">
      <div className="queue-header">
        <h2>Queue Status</h2>
        {userQueueEntry && (
          <div className="user-position">
            <span className="position-label">Your Position:</span>
            <span className="position-number">{userQueueEntry.position}</span>
          </div>
        )}
      </div>

      {userQueueEntry && (
        <div className="user-queue-info">
          <div className="info-item">
            <span className="info-label">Severity:</span>
            <span
              className="severity-badge"
              style={{ backgroundColor: getSeverityColor(userQueueEntry.severity_score) }}
            >
              {getSeverityLabel(userQueueEntry.severity_score)} ({userQueueEntry.severity_score.toFixed(1)})
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Wait Time:</span>
            <span>{Math.round(userQueueEntry.wait_time_minutes)} minutes</span>
          </div>
          <button
            onClick={handleLowerPosition}
            disabled={loading}
            className="lower-position-button"
          >
            {loading ? 'Processing...' : 'Lower My Position'}
          </button>
        </div>
      )}

      <div className="queue-list">
        <div className="queue-list-header">
          <span>Position</span>
          <span>Severity</span>
          <span>Wait Time</span>
        </div>
        {queue.length === 0 ? (
          <div className="empty-queue">No one in queue</div>
        ) : (
          queue.map((entry) => (
            <div
              key={entry.user_id}
              className={`queue-item ${entry.user_id === userId ? 'current-user' : ''}`}
            >
              <span className="queue-position">{entry.position}</span>
              <span
                className="queue-severity"
                style={{ color: getSeverityColor(entry.severity_score) }}
              >
                {getSeverityLabel(entry.severity_score)}
              </span>
              <span className="queue-wait">{Math.round(entry.wait_time_minutes)}m</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default QueueDisplay;
