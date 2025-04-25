"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Email from "./Email";

interface Email {
    subject: string;
    from: string;
    id: string;
    date: string;
}

interface CategorizedEmails {
    primary: Email[];
    social: Email[];
    promotions: Email[];
    updates: Email[];
}

interface InboxProps {
    numEmails?: number;
    page?: number;
    onPageChange?: (page: number) => void;
}

const Inbox = ({ numEmails = 10, page = 1, onPageChange }: InboxProps) => {
    const [emails, setEmails] = useState<CategorizedEmails>({
        primary: [],
        social: [],
        promotions: [],
        updates: []
    });
    const [loading, setLoading] = useState(true);
    const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

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
                setEmails(data);
            })
            .finally(() => setLoading(false));
    }, [page, numEmails]);

    const renderEmailList = (category: string, emails: Email[]) => (
        <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 capitalize">{category}</h2>
            <ul className="mb-4">
                {emails.map((email) => (
                    <li 
                        key={email.id} 
                        className="mb-2 border-b pb-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                        onClick={() => setSelectedEmailId(email.id)}
                    >
                        <strong className="text-gray-800">{email.subject}</strong> <br />
                        <span className="text-gray-600 text-sm">{email.from}</span>
                        <span className="text-gray-400 text-xs block mt-1">{email.date}</span>
                    </li>
                ))}
            </ul>
        </div>
    );

    return (
        <div>
            {loading ? (
                <div className="flex justify-center">
                    <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
                </div>
            ) : (
                <>
                    {renderEmailList('primary', emails.primary)}
                    {renderEmailList('social', emails.social)}
                    {renderEmailList('promotions', emails.promotions)}
                    {renderEmailList('updates', emails.updates)}

                    {selectedEmailId && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                            <div className="bg-white p-6 rounded-lg w-[800px] max-h-[90vh] overflow-y-auto">
                                <div className="flex justify-between items-center mb-4">
                                    <button 
                                        onClick={() => setSelectedEmailId(null)}
                                        className="text-gray-500 hover:text-gray-700"
                                    >
                                        ✕
                                    </button>
                                </div>
                                <Email 
                                    messageId={selectedEmailId}
                                    subject={Object.values(emails).flat().find(e => e.id === selectedEmailId)?.subject}
                                    from={Object.values(emails).flat().find(e => e.id === selectedEmailId)?.from}
                                />
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Inbox;