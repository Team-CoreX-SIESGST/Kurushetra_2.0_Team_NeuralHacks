// OAuthCallback.jsx
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const OAuthCallback = () => {
  const location = useLocation();

  useEffect(() => {
    const hash = location.hash;
    if (hash) {
      const params = new URLSearchParams(hash.substring(1));
      const accessToken = params.get("access_token");

      if (accessToken) {
        // Send the token back to the opener window
        window.opener.postMessage(
          {
            type: "GOOGLE_OAUTH_SUCCESS",
            accessToken,
          },
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
    } else {
      window.opener.postMessage(
        {
          type: "GOOGLE_OAUTH_ERROR",
          error: "No authentication data found",
        },
        window.location.origin
      );
    }

    window.close();
  }, [location]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );
};

export default OAuthCallback;
