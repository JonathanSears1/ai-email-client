"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("accessToken", token);
      router.push("/inbox"); // ✅ Redirect to inbox
    } else {
      router.push("/"); // Fallback
    }
  }, []);

  return <p>Signing you in...</p>;
}
