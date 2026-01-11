import React, { useState, useEffect } from 'react';
import { sendCheckInResponse } from '../services/api';
import './CheckInModal.css';

const CheckInModal = ({ sessionId, checkInData, onClose }) => {
  const [response, setResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Auto-close after 5 minutes if no response
    const timeout = setTimeout(() => {
      if (!response) {
        handleSubmit('same'); // Default to 'same' if no response
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearTimeout(timeout);
  }, [response]);

  const handleSubmit = async (selectedResponse) => {
    if (submitting) return;

    setSubmitting(true);
    setResponse(selectedResponse);

    try {
      await sendCheckInResponse(
        sessionId,
        checkInData.queue_entry_id,
        selectedResponse
      );
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (error) {
      console.error('Error submitting check-in:', error);
      alert('Failed to submit check-in response. Please try again.');
      setSubmitting(false);
      setResponse('');
    }
  };

  if (!checkInData) return null;

  return (
    <div className="modal-overlay" onClick={() => !submitting && onClose()}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Check-In</h3>
          {!submitting && (
            <button className="close-button" onClick={onClose}>×</button>
          )}
        </div>
        <div className="modal-body">
          <p className="check-in-question">{checkInData.message}</p>
          <div className="response-buttons">
            <button
              className={`response-button ${response === 'better' ? 'selected' : ''}`}
              onClick={() => handleSubmit('better')}
              disabled={submitting}
            >
              Better
            </button>
            <button
              className={`response-button ${response === 'same' ? 'selected' : ''}`}
              onClick={() => handleSubmit('same')}
              disabled={submitting}
            >
              Same
            </button>
            <button
              className={`response-button ${response === 'worse' ? 'selected' : ''}`}
              onClick={() => handleSubmit('worse')}
              disabled={submitting}
            >
              Worse
            </button>
          </div>
          {submitting && (
            <div className="submitting-message">
              Thank you for your response. Your check-in has been recorded.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CheckInModal;
