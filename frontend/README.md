# Morgan Legal Tender - Frontend

Modern React-based web interface for the Morgan Legal Tender AI-powered legal assistant system.

## Features

- **Task Input & Routing**: Submit any legal task or client message and have it automatically routed to the appropriate AI specialist
- **Email Integration**: Monitor and process emails forwarded to your legal inbox
- **SMS Communication**: Send and receive SMS messages via Twilio integration
- **Agent Status Dashboard**: Real-time monitoring of AI agent performance and task distribution
- **Summary Reports**: Clean, organized display of AI-generated legal research, client communications, and more

## Tech Stack

- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful icon library

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000` (or configured URL)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

The optimized production build will be in the `dist/` directory.

### 5. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── TaskInput.tsx    # Main task input form
│   │   ├── ResultDisplay.tsx # Task result display
│   │   ├── EmailPanel.tsx   # Email inbox viewer
│   │   ├── SMSPanel.tsx     # SMS interface
│   │   └── AgentStatus.tsx  # Agent monitoring dashboard
│   ├── services/            # API service layer
│   │   └── api.ts           # API client and types
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Features Overview

### Task Assistant

The main interface where lawyers can input any legal task or client communication. The system will:

1. Analyze the input
2. Determine the appropriate AI specialist agent
3. Route and process the task
4. Display a comprehensive summary report

Supported task types:
- Legal research
- Client communication drafting
- Records retrieval
- Appointment scheduling
- Document organization

### Email Integration

Monitor emails forwarded to your configured inbox. The system can:

- Fetch emails via IMAP
- Display email inbox in the UI
- Process emails and route to appropriate agents
- Track processing status

**Setup Requirements:**
- Configure IMAP credentials in backend `.env`
- Gmail users: Enable "Less secure app access" or use App Passwords

### SMS Communication

Send and receive SMS messages through Twilio integration:

- Send SMS to clients directly from the UI
- View message history
- Receive incoming messages via webhook
- Track delivery status

**Setup Requirements:**
- Twilio account with phone number
- Configure Twilio credentials in backend `.env`
- Set up webhook URL in Twilio console: `https://your-domain.com/api/sms/webhook`

### Agent Status Dashboard

Real-time monitoring of AI specialist agents:

- View active/inactive agent status
- Monitor current load and task counts
- Track task distribution by type
- View processing metrics

## API Integration

The frontend communicates with the backend API at `/api/*` endpoints:

- `/api/router/route` - Submit tasks for routing
- `/api/router/agents/status` - Get agent status
- `/api/router/stats` - Get routing statistics
- `/api/email/inbox` - Fetch emails
- `/api/email/forward` - Process forwarded email
- `/api/sms/send` - Send SMS
- `/api/sms/history` - Get SMS history

## Configuration

### Proxy Configuration

The Vite dev server is configured to proxy API requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### CORS

Ensure the backend is configured to allow requests from the frontend origin. The backend `.env` should include:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Deployment

### Production Build

```bash
npm run build
```

### Deploy to Static Hosting

The `dist/` folder can be deployed to any static hosting service:

- **Vercel**: `vercel --prod`
- **Netlify**: Drag and drop `dist/` folder
- **AWS S3**: Upload `dist/` contents
- **GitHub Pages**: Push `dist/` to `gh-pages` branch

### Environment Variables

For production deployments, set the API URL:

```env
VITE_API_BASE_URL=https://your-api-domain.com
```

## Troubleshooting

### API Connection Issues

If you see connection errors:

1. Verify backend is running on the configured URL
2. Check CORS settings in backend `.env`
3. Ensure no firewall blocking requests
4. Check browser console for detailed errors

### Email Not Loading

1. Verify IMAP credentials in backend `.env`
2. For Gmail: Enable App Passwords and use that instead of regular password
3. Check backend logs for IMAP connection errors

### SMS Not Working

1. Verify Twilio credentials in backend `.env`
2. Ensure Twilio phone number is SMS-enabled
3. Check Twilio console for error messages
4. Verify phone numbers are in E.164 format (+1234567890)

## Development Tips

### Hot Reload

The development server supports hot module replacement (HMR). Changes to components will update instantly without full page reload.

### TypeScript

The project uses strict TypeScript. All API types are defined in `src/services/api.ts`.

### Styling

Uses Tailwind CSS utility classes. Custom colors are defined in `tailwind.config.js`:

- `legal-blue` - Primary brand color
- `legal-gold` - Accent color

## Support

For issues, questions, or contributions:

- Email: dhyan.sur@gmail.com
- Backend API Documentation: http://localhost:8000/docs

## License

MIT License - See LICENSE file for details
