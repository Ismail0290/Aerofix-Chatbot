import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppHeader } from "@/components/AppHeader";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AeroFix — HVAC operations",
  description: "Monitor inverter AC fleets, failures, and maintenance context.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-zinc-950 text-zinc-100">
        <AppHeader />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-zinc-800/60 py-6 text-center text-xs text-zinc-600">
          Connected to AeroFix FastAPI · Supabase IoT data
        </footer>
      </body>
    </html>
  );
}
