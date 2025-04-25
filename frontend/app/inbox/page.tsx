"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Inbox from "@/app/components/Inbox";
import SummaryButton from "../components/SummaryButton";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function InboxPage() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      router.push("/");
    }
  }, [router]);

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="flex items-center justify-between">
        <Navbar />
      </div>
      <div className="flex">
        <div className="flex-shrink-0">
          <Sidebar />
        </div>
        <div className="flex-grow p-4">
          <Inbox
            numEmails={20}
            page={currentPage}
            onPageChange={setCurrentPage}
          />
        </div>
      </div>
    </div>
  );
}
