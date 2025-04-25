import { useState, useEffect } from "react"
import React from 'react'

interface EmailProps {
  from?: string;
  subject?: string;
  messageId?: string;
}

const Email = ({ messageId, from, subject }: EmailProps) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{body: string}>({
    body: ''
  });

  const fetchMessage = async (messageId: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        throw new Error("No access token found");
      }

      const response = await fetch(`http://localhost:8000/api/gmail/messages/${messageId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage({
        body: data.body
      });
    } catch (error) {
      console.error('Error fetching message:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (messageId) {
      fetchMessage(messageId);
    }
  }, [messageId]);

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl text-gray-500 font-bold">{subject}</h2>
        <p className="text-gray-600">From: {from}</p>
      </div>
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <div className="prose text-gray-700" dangerouslySetInnerHTML={{ __html: message.body }} />
      )}
    </div>
  );
}

export default Email
