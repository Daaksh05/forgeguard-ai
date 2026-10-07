import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ForgeGuard AI | Operator Console",
  description: "Industrial maintenance decision-support operator dashboard.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
