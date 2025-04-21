"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Inbox from "@/app/components/Inbox";
import SummaryButton from "../components/SummaryButton";

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
    <div>
      <h1 className="text-xl font-bold mb-4 p-8">Your Inbox</h1>
      <SummaryButton />
      <Inbox
        numEmails={20}
        page={currentPage}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
