# Complete Setup Guide - Morgan Legal Tender with Frontend

This guide will walk you through setting up the entire Morgan Legal Tender system including the backend API and frontend UI with email and SMS integration.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  - Task Input Interface                                 │
│  - Email Inbox Viewer                                   │
│  - SMS Communication Panel                              │
│  - Agent Status Dashboard                               │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST API
┌───────────────────────▼─────────────────────────────────┐
│                  Backend (FastAPI)                      │
│  - Task Router                                          │
│  - AI Specialist Agents                                 │
│  - Email Service (IMAP)                                 │
│  - SMS Service (Twilio)                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌────────▼────────┐
│  AI Providers  │            │ Communication   │
│  - Claude      │            │  - Email (IMAP) │
│  - OpenAI      │            │  - Twilio SMS   │
│  - Gemini      │            └─────────────────┘
└────────────────┘
```

## Prerequisites

### Required Software
- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

### Required Accounts & API Keys
1. **AI Provider** (choose one or more):
   - Anthropic Claude API key
   - OpenAI API key
   - Google Gemini API key

2. **Email** (optional but recommended):
   - Email account with IMAP access (Gmail recommended)
   - Gmail App Password (if using Gmail)

3. **SMS** (optional but recommended):
   - Twilio account
   - Twilio phone number
   - Twilio API credentials

## Step-by-Step Setup

### Part 1: Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd morgan-legaltender/backend
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

```bash
# Copy the example file
cp ../.env.example ../.env

# Edit the .env file with your credentials
```

**Required Configuration:**

```env
# AI Provider (at least one required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here
# OR
GOOGLE_AI_API_KEY=your-key-here

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=development

# CORS (important for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Optional Email Configuration:**

```env
# For Gmail:
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
```

**How to get Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification (must be enabled)
3. App Passwords → Select "Mail" and "Other (Custom name)"
4. Copy the generated password

**Optional SMS Configuration:**

```env
# Twilio credentials
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

**How to get Twilio credentials:**
1. Sign up at https://www.twilio.com
2. Get a phone number from the console
3. Copy Account SID and Auth Token from dashboard

#### 5. Start Backend Server

```bash
# Make sure you're in the backend directory
cd backend

# Run the server
python main.py

# Or use uvicorn directly:
uvicorn main:app --reload --port 8000
```

The backend should now be running at `http://localhost:8000`

Visit `http://localhost:8000/docs` to see the API documentation.

### Part 2: Frontend Setup

#### 1. Open New Terminal (Keep Backend Running)

```bash
# Navigate to frontend directory from project root
cd morgan-legaltender/frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment

```bash
# Copy example file
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

#### 4. Start Frontend Development Server

```bash
npm run dev
```

The frontend should now be running at `http://localhost:3000`

## Using the Application

### 1. Access the Web Interface

Open your browser and go to `http://localhost:3000`

### 2. Submit a Legal Task

**Example Task:**
```
I need recent case law about negligence in slip and fall accidents
from the past 3 years. Client slipped on ice in a parking lot.
```

**What happens:**
1. System analyzes the text
2. Routes to **Legal Researcher** agent
3. AI generates research with citations and suggestions
4. Results displayed in clean summary format

### 3. Use Email Integration

#### Setup Email Forwarding:

**Option 1: IMAP Monitoring**
- Configure IMAP credentials in backend `.env`
- Frontend will poll the inbox
- View emails in the "Email Inbox" tab

**Option 2: Forward Rule**
- Set up email forwarding rule to send to your monitored inbox
- System automatically processes new emails

### 4. Send SMS Messages

1. Click "SMS" tab
2. Enter phone number in E.164 format: `+1234567890`
3. Type message
4. Click "Send Message"

**Receive SMS:**
- Configure Twilio webhook URL in Twilio console:
  - `https://your-domain.com/api/sms/webhook`
- Incoming messages appear in message history

### 5. Monitor Agent Performance

Click "Agent Status" tab to see:
- Active agents and their status
- Current load per agent
- Total tasks processed
- Task distribution by type
- Average processing times

## Troubleshooting

### Backend Issues

**Error: "No module named 'X'"**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "CORS policy error"**
- Check `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Restart backend server after changing `.env`

**Error: "AI API key not found"**
- Ensure you've set at least one AI provider key in `.env`
- Verify the key is valid

### Frontend Issues

**Error: "Cannot connect to API"**
1. Verify backend is running on port 8000
2. Check `VITE_API_BASE_URL` in frontend `.env`
3. Check browser console for CORS errors

**Error: "Module not found"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Email Issues

**Cannot connect to IMAP:**
- Gmail: Use App Password, not regular password
- Verify IMAP is enabled in email settings
- Check firewall/antivirus isn't blocking port 993

### SMS Issues

**SMS not sending:**
- Verify Twilio credentials are correct
- Check Twilio account has credits
- Ensure phone number format is E.164: `+1234567890`
- Check Twilio console for error logs

## Testing the System

### Test Task Router

```bash
# Using curl
curl -X POST http://localhost:8000/api/router/route \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I need to draft an email to client about their case status",
    "priority": 5
  }'
```

### Test SMS (Mock Mode)

If Twilio isn't configured, the system will operate in mock mode:
- SMS sends will return success but not actually send
- Useful for testing UI without Twilio account

### Test Email

Access the email inbox endpoint:
```
http://localhost:8000/api/email/inbox?limit=10
```

## Production Deployment

### Backend Deployment

1. Choose hosting provider (AWS, Google Cloud, Heroku, etc.)
2. Set environment variables in production
3. Use production WSGI server (already configured with uvicorn)
4. Set `ENVIRONMENT=production` in `.env`
5. Configure SSL certificate
6. Set up domain and DNS

### Frontend Deployment

```bash
# Build for production
cd frontend
npm run build

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
# - GitHub Pages
```

**Update environment:**
```env
VITE_API_BASE_URL=https://your-api-domain.com
```

### Twilio Webhook Setup

Once deployed, configure Twilio webhook:
1. Go to Twilio Console → Phone Numbers
2. Select your phone number
3. Under "Messaging", set webhook URL:
   - `https://your-domain.com/api/sms/webhook`
   - Method: POST

## Architecture Decisions

### Why These Technologies?

**Backend:**
- **FastAPI**: High performance, async support, automatic API docs
- **Python**: Best ecosystem for AI/ML libraries
- **Twilio**: Industry standard for SMS, reliable
- **IMAP**: Standard protocol, works with any email provider

**Frontend:**
- **React**: Popular, component-based, great ecosystem
- **TypeScript**: Type safety prevents bugs
- **Vite**: Fast development, modern build tool
- **Tailwind CSS**: Rapid UI development, customizable

## Next Steps

1. **Add Authentication**: Implement user login/JWT auth
2. **Database Integration**: Store tasks, emails, messages in PostgreSQL
3. **File Upload**: Add document upload for evidence sorter
4. **Real-time Updates**: Use WebSockets for live status updates
5. **Calendar Integration**: Connect to Google Calendar for appointments
6. **Analytics**: Add charts and metrics dashboard
7. **Mobile App**: Build React Native mobile app

## Security Considerations

### Production Checklist:

- [ ] Change all default passwords and secret keys
- [ ] Enable HTTPS/SSL
- [ ] Implement rate limiting
- [ ] Add authentication and authorization
- [ ] Sanitize all user inputs
- [ ] Enable CORS only for trusted domains
- [ ] Store secrets in environment variables, not code
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Implement logging and monitoring
- [ ] Backup database regularly
- [ ] Use secrets manager (AWS Secrets Manager, etc.)

## Support & Resources

- **Backend API Docs**: http://localhost:8000/docs
- **Twilio Docs**: https://www.twilio.com/docs
- **Anthropic Claude**: https://docs.anthropic.com
- **OpenAI**: https://platform.openai.com/docs
- **React**: https://react.dev
- **FastAPI**: https://fastapi.tiangolo.com

## License

MIT License - See LICENSE file

---

**Questions?** Contact: dhyan.sur@gmail.com
