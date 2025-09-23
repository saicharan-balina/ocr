# Certificate OCR Frontend

Next.js frontend for the Certificate OCR application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables (optional):
Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

3. Run the development server:
```bash
npm run dev
```

Application will be available at `http://localhost:3000`

## Features

- **File Upload**: Drag and drop or click to upload files
- **Real-time Processing**: Shows processing status with loading indicators
- **Result Display**: Clean presentation of extracted text
- **Multiple File Types**: Support for PDF, PNG, JPG, JPEG, BMP, TIFF
- **Backend Status**: Real-time connection status with the Flask backend
- **Responsive Design**: Works on desktop and mobile devices
- **Text Actions**: Copy to clipboard and download extracted text
- **Error Handling**: Comprehensive error messages and retry options

## File Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Home page component
├── components/
│   ├── FileUpload.tsx       # File upload component with drag & drop
│   └── ResultDisplay.tsx    # OCR results display component
├── lib/
│   └── api.ts              # API client for backend communication
├── package.json
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## Build for Production

```bash
npm run build
npm start
```

## Technology Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests