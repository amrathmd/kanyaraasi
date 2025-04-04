# Invoice Manager

A Next.js application for managing invoice uploads and reviews with role-based access control.

## Features

- Google Authentication
- Role-based access control (Admin/User)
- Document upload and management
- Document preview
- Status tracking (Pending/Approved/Rejected)

## Prerequisites

- Node.js 18+ and npm
- Google OAuth credentials
- AWS S3 bucket (for production)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd invoice-manager
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file in the root directory and add the following environment variables:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AWS S3 (for production)
NEXT_PUBLIC_AWS_ACCESS_KEY_ID=your-aws-access-key
NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY=your-aws-secret-key
NEXT_PUBLIC_S3_BUCKET_NAME=your-bucket-name
```

4. Set up Google OAuth:
   - Go to the [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - http://localhost:3000/api/auth/callback/google (for development)
     - https://your-domain.com/api/auth/callback/google (for production)

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Admin Access
- Log in with the admin email (amrath@hugohub.com)
- View all uploaded documents
- Approve or reject documents
- Preview documents

### User Access
- Log in with any other Google account
- Upload documents
- View your uploaded documents
- Track document status

## Development

The project uses:
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- NextAuth.js for authentication
- AWS SDK for S3 operations
- Headless UI for components
- Heroicons for icons

## Production Deployment

1. Set up environment variables for production
2. Configure AWS S3 bucket and permissions
3. Deploy to your preferred hosting platform (Vercel, Netlify, etc.)

## License

MIT
