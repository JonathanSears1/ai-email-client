"use client";

import { useState } from "react";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/auth/login");
      const data = await res.json();

      if (data.auth_url) {
        window.location.href = data.auth_url; // ✅ Redirect browser to Google login
      } else {
        console.error("No auth URL returned");
        setLoading(false);
      }
    } catch (err) {
      console.error("Login error", err);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-2xl font-semibold mb-4">Welcome to AI Mail</h1>
      <button
        onClick={handleGoogleLogin}
        disabled={loading}
        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
      >
        {loading ? "Redirecting..." : "Sign in with Google"}
      </button>
    </div>
  );
}
