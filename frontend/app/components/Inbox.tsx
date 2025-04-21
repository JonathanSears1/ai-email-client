"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Email {
    subject: string;
    from: string;
    id: string;
  }
  
  interface InboxProps {
    numEmails?: number;
    page?: number;
    onPageChange?: (page: number) => void;
  }
  
  const Inbox = ({ numEmails = 10, page = 1, onPageChange }: InboxProps) => {
    const [emails, setEmails] = useState<Email[]>([]);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(true);
  
    useEffect(() => {
      const token = localStorage.getItem("accessToken");
      if (!token) return;
  
      setLoading(true);
      fetch(`http://localhost:8000/api/gmail/inbox?page=${page}&limit=${numEmails}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
        .then((res) => res.json())
        .then((data) => {
          setEmails(data.messages || []);
          setTotalPages(Math.ceil((data.total || 0) / numEmails));
        })
        .finally(() => setLoading(false));
    }, [page, numEmails]);
  
    return (
      <div className="p-8">
        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        ) : (
          <>
            <ul className="mb-4">
              {emails.map((email) => (
                <li key={email.id} className="mb-2 border-b pb-2">
                  <strong>{email.subject}</strong> <br />
                  <span className="text-gray-600 text-sm">{email.from}</span>
                </li>
              ))}
            </ul>
  
            <div className="flex justify-between items-center">
              <button
                onClick={() => onPageChange?.(page - 1)}
                disabled={page <= 1}
                className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
              >
                Previous
              </button>
              <span>
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => onPageChange?.(page + 1)}
                disabled={page >= totalPages}
                className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

export default Inbox;