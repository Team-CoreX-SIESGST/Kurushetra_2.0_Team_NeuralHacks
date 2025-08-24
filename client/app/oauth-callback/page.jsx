"use client";
import { useEffect } from "react";
import { useSearchParams } from "next/navigation";

export default function OAuthCallback() {
  const searchParams = useSearchParams();

  useEffect(() => {
    // Google sends back the access_token in the URL hash, not search params
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const accessToken = params.get("access_token");

    if (accessToken) {
      window.opener.postMessage(
        { type: "GOOGLE_OAUTH_SUCCESS", accessToken },
        window.location.origin
      );
    } else {
      window.opener.postMessage(
        {
          type: "GOOGLE_OAUTH_ERROR",
          error: "No access token found",
        },
        window.location.origin
      );
    }

    window.close();
  }, [searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );
}
