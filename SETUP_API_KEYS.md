# API Keys Setup Guide

## Quick Start - Getting API Keys

### Option 1: OpenAI (Recommended for Beginners)

**Easiest to set up and most reliable**

1. Go to: https://platform.openai.com/signup
2. Create an account (you'll get $5 free credit for new accounts)
3. Go to: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)
6. Add to your `.env` file:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Cost**: ~$0.002 per request (very cheap for testing)

---

### Option 2: Anthropic Claude (Most Powerful)

**Best for complex legal analysis**

1. Go to: https://console.anthropic.com/
2. Sign up for an account
3. Go to: https://console.anthropic.com/settings/keys
4. Generate an API key
5. Copy the key (starts with `sk-ant-...`)
6. Add to your `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Cost**: ~$0.003 per request (slightly more expensive but better quality)

---

### Option 3: Google Gemini (Free!)

**Best if you don't want to pay anything**

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Add to your `.env` file:

```bash
GOOGLE_AI_API_KEY=your-google-key-here
```

**Cost**: Free tier includes 60 requests per minute

---

## Step-by-Step Setup

### 1. Get at least ONE API key

Choose one of the options above and get an API key.

### 2. Create/Edit `.env` file

```bash
# In the backend directory
cd backend

# Copy example file (if not already done)
cp ../.env.example .env

# Edit the file
nano .env  # or use your preferred editor
```

### 3. Add Your API Key

Open `.env` and replace the placeholder:

**Before:**
```bash
OPENAI_API_KEY=your-openai-key-here
```

**After:**
```bash
OPENAI_API_KEY=sk-proj-abc123xyz...your-actual-key
```

### 4. Save and Test

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Test that the key loads
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"

# Should print: API Key loaded: True
```

---

## Testing Your Setup

### Quick Test Script

Create a test file to verify your API key works:

```python
# test_api_key.py
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
google_key = os.getenv('GOOGLE_AI_API_KEY')

print("=" * 50)
print("API Key Status Check")
print("=" * 50)

if openai_key and openai_key != "your-openai-key-here":
    print("✅ OpenAI API Key: Configured")
else:
    print("❌ OpenAI API Key: Not configured")

if anthropic_key and anthropic_key != "":
    print("✅ Anthropic API Key: Configured")
else:
    print("❌ Anthropic API Key: Not configured")

if google_key and google_key != "":
    print("✅ Google API Key: Configured")
else:
    print("❌ Google API Key: Not configured")

print("=" * 50)

# Test if at least one key is configured
has_key = any([
    openai_key and openai_key != "your-openai-key-here",
    anthropic_key and anthropic_key != "",
    google_key and google_key != ""
])

if has_key:
    print("\n✅ You're ready to run the server!")
    print("\nRun: python app.py")
else:
    print("\n⚠️  No API keys configured!")
    print("Please add at least one API key to .env file")
```

Run this test:

```bash
python test_api_key.py
```

### Start the Server

```bash
# If test passed, start the server
python app.py

# Should see:
# Starting Morgan Legal Tender - Task Router API
# Server running at http://localhost:8000
```

### Test an Endpoint

```bash
# Test the orchestrator with your API key
curl -X POST "http://localhost:8000/api/orchestrator/test-input?text=I%20need%20medical%20records%20from%20Dr.%20Smith"
```

---

## Troubleshooting

### Error: "API key not found"

**Problem**: The `.env` file isn't being loaded

**Solution**:
```bash
# Make sure you're in the backend directory
pwd  # Should end with /backend

# Check if .env exists
ls -la .env

# Check if dotenv is installed
pip list | grep python-dotenv
```

### Error: "Invalid API key"

**Problem**: The API key is wrong or expired

**Solution**:
1. Go back to the API provider's website
2. Generate a new key
3. Replace in `.env` file
4. Restart the server

### Error: "Module not found"

**Problem**: Dependencies not installed

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Mock Adapter Still Running

**Problem**: Code is using mock instead of real API

**Solution**: Check that:
1. API key is in `.env` file
2. `.env` file is in the `backend` directory
3. You restarted the server after adding the key

---

## Security Best Practices

### ⚠️ NEVER commit `.env` to git!

The `.env` file is already in `.gitignore`, but double-check:

```bash
# Check if .env is ignored
git status

# .env should NOT appear in the list
# If it does, it means it's NOT ignored!
```

### Keep Your Keys Secret

- ❌ Don't share your `.env` file
- ❌ Don't post API keys in Discord/Slack
- ❌ Don't commit them to GitHub
- ✅ Only store in `.env` file locally
- ✅ Use different keys for development/production

### Rotating Keys

If you accidentally expose a key:

1. Immediately go to the provider's website
2. Delete/revoke the exposed key
3. Generate a new one
4. Update your `.env` file

---

## Cost Management

### OpenAI Pricing

- GPT-4o-mini: ~$0.002 per request
- GPT-4: ~$0.03 per request
- Set usage limits in OpenAI dashboard

### Anthropic Pricing

- Claude Sonnet: ~$0.003 per request
- Claude Opus: ~$0.015 per request
- Monitor usage in Anthropic console

### Google Gemini Pricing

- Gemini 1.5 Flash: FREE (60 req/min)
- Gemini 1.5 Pro: FREE (2 req/min)
- No credit card required!

**Recommendation for Testing**: Start with Google Gemini (free) or OpenAI (cheap)

---

## Environment Variables Reference

Here are all the important variables in `.env`:

```bash
# Required (pick at least ONE)
OPENAI_API_KEY=sk-...           # OpenAI key
ANTHROPIC_API_KEY=sk-ant-...    # Anthropic key
GOOGLE_AI_API_KEY=...           # Google key

# Optional but useful
ENVIRONMENT=development          # development or production
PORT=8000                       # Server port
DEBUG=false                     # Enable debug logging
ENABLE_AI_CACHE=true           # Cache AI responses (saves money!)
```

---

## Next Steps

After setting up your API keys:

1. ✅ Test the orchestrator endpoint
2. ✅ Try each specialist individually
3. ✅ Process a real email/text message
4. ✅ Review the API documentation at http://localhost:8000/docs

---

## Getting Help

If you're still stuck:

1. Check the server logs for error messages
2. Make sure `.env` is in the `backend` directory
3. Verify your API key is valid on the provider's website
4. Try the test script above to debug

**Common Issue**: Forgot to activate the virtual environment
```bash
source venv/bin/activate  # Do this first!
```

---

## Summary

**Minimal Setup (Choose ONE):**

**Option A - OpenAI (Easiest)**
```bash
# Get key from: https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=sk-proj-your-key" >> backend/.env
cd backend
python app.py
```

**Option B - Google Gemini (Free)**
```bash
# Get key from: https://makersuite.google.com/app/apikey
echo "GOOGLE_AI_API_KEY=your-key" >> backend/.env
cd backend
python app.py
```

That's it! You're ready to run the AI assistant! 🚀
