import type { Metadata } from "next";
import "./globals.css";
import { ToastProviderWrapper } from "@/components/ui/toaster";

export const metadata: Metadata = {
  title: "Doctor_zenZ — AI Medical Scribe",
  description: "AI-powered ambient medical scribe for Indian doctors",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>
        <ToastProviderWrapper>
          {children}
        </ToastProviderWrapper>
      </body>
    </html>
  );
}
