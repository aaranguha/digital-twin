// Root Layout - Wraps every page in the app
// This is required by Next.js App Router

import './globals.css'  // Import Tailwind styles

// Metadata shows up in browser tab and search results
export const metadata = {
  title: "Aaran's Digital Twin",
  description: 'AI-powered professional twin',
}

// This component wraps ALL pages
// children = whatever page is currently being viewed
export default function RootLayout({
  children,
}: {
  children: React.ReactNode  // TypeScript: children can be any React content
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
