import type { ReactNode } from "react";
import Link from "next/link";

export const metadata = {
  title: "Nutrition App",
  description: "Foods browser, meal calculator, and admin add-food",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "sans-serif" }}>
        <header
          style={{
            borderBottom: "1px solid #ddd",
            padding: "12px 16px",
            display: "flex",
            gap: 16,
          }}
        >
          <Link href="/">Home</Link>
          <Link href="/foods">Foods</Link>
          <Link href="/calculator">Calculator</Link>
          <Link href="/admin/add-food">Admin Add Food</Link>
        </header>
        {children}
      </body>
    </html>
  );
}
