import "./globals.css";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { Toaster } from "react-hot-toast";

import { GoogleOAuthProvider } from "@react-oauth/google";
const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "OmniSearch AI",
  description:
    "Connect your Google Drive and unlock powerful AI search across all your documents",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                const savedTheme = localStorage.getItem('theme');
                const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const theme = savedTheme === 'system' ? (systemDark ? 'dark' : 'light') : (savedTheme || 'system');
                document.documentElement.classList.add(theme === 'system' ? (systemDark ? 'dark' : 'light') : theme);
              })();
            `,
          }}
        />
      </head>
      <body className={inter.className}>
        <GoogleOAuthProvider
          clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}
        >
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <AuthProvider>
              {children}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: "var(--background)",
                    color: "var(--foreground)",
                    border: "1px solid var(--border)",
                  },
                }}
              />
            </AuthProvider>
          </ThemeProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
