import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

const SummaryButton = () => {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');

  const handleSummaryClick = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("accessToken");
      const response = await fetch("http://localhost:8000/api/gmail/summary", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      console.error("Error fetching summary:", err);
      setSummary("Error generating summary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={handleSummaryClick}
        disabled={loading}
        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {loading ? (
          <div className="flex items-center">
            <div className="animate-spin h-5 w-5 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
            Generating Summary...
          </div>
        ) : (
          "Generate Email Summary"
        )}
      </button>

      {summary && (
        <div className="mt-4 p-4 border-4 text-gray-600 rounded-lg border-blue-600 bg-gray-50">
          <ReactMarkdown>
            {summary}
          </ReactMarkdown>
        </div>
      )}
    </>
  );
}; 

export default SummaryButton;
