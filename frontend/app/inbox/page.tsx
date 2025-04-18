"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function InboxPage() {
  const [emails, setEmails] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      router.push("/");
      return;
    }

    fetch("http://localhost:8000/api/gmail/inbox", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setEmails(data.messages || []);
      });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-xl font-bold mb-4">Your Inbox</h1>
      <ul>
        {emails.map((email, idx) => (
          <li key={idx} className="mb-2 border-b pb-2">
            <strong>{email.subject}</strong> <br />
            <span className="text-gray-600 text-sm">{email.from}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
