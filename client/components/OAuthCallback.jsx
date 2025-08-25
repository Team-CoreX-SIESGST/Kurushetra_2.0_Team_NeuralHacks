// pages/oauth-callback.js or app/oauth-callback/page.js (depending on your Next.js version)
"use client"
import { useEffect } from "react";

export default function OAuthCallback() {
  useEffect(() => {
    // Extract access token from URL fragment
    const fragment = window.location.hash.substring(1);
    const params = new URLSearchParams(fragment);
    const accessToken = params.get("access_token");
    const error = params.get("error");

    if (error) {
      // Send error to parent window
      if (window.opener) {
        window.opener.postMessage(
          {
            type: "GOOGLE_OAUTH_ERROR",
            error: error,
          },
          window.location.origin
        );
      }
    } else if (accessToken) {
      // Send success to parent window
      if (window.opener) {
        window.opener.postMessage(
          {
            type: "GOOGLE_OAUTH_SUCCESS",
            accessToken: accessToken,
          },
          window.location.origin
        );
      }
    }

    // Close the popup after a short delay
    setTimeout(() => {
      window.close();
    }, 1000);
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Processing authentication...</p>
        <p className="text-sm text-gray-400 mt-2">You can close this window.</p>
      </div>
    </div>
  );
}
