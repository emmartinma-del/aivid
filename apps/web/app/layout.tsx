import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AIvid – App Store Video Generator",
  description: "Generate professional App Store and Google Play preview videos in minutes with AI.",
  keywords: ["app store video", "preview video", "app marketing", "google play video"],
  openGraph: {
    title: "AIvid – App Store Video Generator",
    description: "AI-powered app store preview videos that drive downloads.",
    url: "https://app.aivid.ch",
    siteName: "AIvid",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
