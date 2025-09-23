import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Certificate OCR - Extract Text from Documents',
  description: 'Upload certificates and documents to extract text using OCR technology',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <header className="border-b bg-white">
            <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
              <a href="/" className="text-lg font-semibold">Certificate OCR</a>
              <nav className="flex items-center gap-4 text-sm">
                <a className="text-gray-700 hover:text-black" href="/">OCR</a>
                <a className="text-gray-700 hover:text-black" href="/verify">Verify</a>
                <a className="text-gray-700 hover:text-black" href="/admin">Admin</a>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}