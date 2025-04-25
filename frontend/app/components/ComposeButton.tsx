import React, { useState } from 'react'

const ComposeButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState({
    to: '',
    subject: '',
    body: ''
  });

  const handleSubmit = async (isDraft = false) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("accessToken");
      const response = await fetch(`http://localhost:8000/api/gmail/${isDraft ? 'draft' : 'send'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(email)
      });
      
      if (!response.ok) throw new Error('Failed to send email');
      
      setIsOpen(false);
      setEmail({ to: '', subject: '', body: '' });
    } catch (err) {
      console.error("Error sending email:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
      >
        Compose
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-[600px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">New Message</h2>
              <button 
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <input
              type="email"
              placeholder="To"
              value={email.to}
              onChange={(e) => setEmail({...email, to: e.target.value})}
              className="w-full mb-2 p-2 border rounded"
            />
            
            <input
              type="text"
              placeholder="Subject"
              value={email.subject}
              onChange={(e) => setEmail({...email, subject: e.target.value})}
              className="w-full mb-2 p-2 border rounded"
            />
            
            <textarea
              placeholder="Write your message..."
              value={email.body}
              onChange={(e) => setEmail({...email, body: e.target.value})}
              className="w-full h-64 mb-4 p-2 border rounded resize-none"
            />

            <div className="flex justify-end gap-2">
              <button
                onClick={() => handleSubmit(true)}
                disabled={loading}
                className="px-4 py-2 text-gray-600 border rounded hover:bg-gray-100 disabled:bg-gray-200"
              >
                Save as Draft
              </button>
              <button
                onClick={() => handleSubmit(false)}
                disabled={loading}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
                    Sending...
                  </div>
                ) : (
                  "Send"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ComposeButton;
