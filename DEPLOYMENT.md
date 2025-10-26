# Deployment Guide - Tender for Lawyers

## Quick Start (Development)

### Prerequisites

- Python 3.12+
- pip package manager
- Virtual environment tool (venv)

### Step 1: Clone and Setup

```bash
# Clone the repository
cd morgan-legaltender/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

```bash
# Copy example environment file
cp ../.env.example .env

# Edit .env file with your configuration
# At minimum, set:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - DATABASE_URL (if using database)
```

### Step 3: Run the Application

```bash
# Start the server
python app.py

# Or use uvicorn directly
uvicorn app:app --reload --port 8000
```

The API will be available at:
- Main API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py

# Run tests in parallel
pytest -n auto
```

See [TESTING.md](TESTING.md) for more details.

---

## Production Deployment

### Option 1: Docker Deployment (Recommended)

```dockerfile
# Create Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build image
docker build -t tender-lawyers .

# Run container
docker run -p 8000:8000 --env-file .env tender-lawyers
```

### Option 2: Traditional Server Deployment

#### Using Gunicorn (Recommended for production)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Using systemd service

Create `/etc/systemd/system/tender-lawyers.service`:

```ini
[Unit]
Description=Tender for Lawyers API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/tender-lawyers/backend
Environment="PATH=/var/www/tender-lawyers/backend/venv/bin"
ExecStart=/var/www/tender-lawyers/backend/venv/bin/gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable tender-lawyers
sudo systemctl start tender-lawyers
```

### Option 3: Cloud Platform Deployment

#### Heroku

```bash
# Create Procfile
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create tender-lawyers
git push heroku main
```

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.12 tender-lawyers

# Create environment
eb create tender-lawyers-env

# Deploy
eb deploy
```

#### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy tender-lawyers \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Environment Variables for Production

Critical environment variables for production:

```bash
# REQUIRED
ENVIRONMENT=production
SECRET_KEY=<generate-strong-secret-key>
DATABASE_URL=<production-database-url>
OPENAI_API_KEY=<your-api-key>  # or ANTHROPIC_API_KEY

# RECOMMENDED
DEBUG=false
AUTO_RELOAD=false
SENTRY_DSN=<your-sentry-dsn>
CORS_ORIGINS=https://yourdomain.com

# OPTIONAL
REDIS_HOST=<redis-host>
SALESFORCE_USERNAME=<username>
```

---

## Database Setup (Optional)

If using PostgreSQL for production:

```bash
# Create database
createdb tender_db

# Run migrations (if using Alembic)
alembic upgrade head
```

---

## Monitoring and Logging

### Sentry Integration

```python
# Already configured in app.py
# Just set SENTRY_DSN in environment
```

### Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "service": "task-router", ...}
```

---

## Performance Tuning

### Gunicorn Workers

```bash
# Calculate optimal workers: (2 x $num_cores) + 1
gunicorn app:app -w 9 -k uvicorn.workers.UvicornWorker
```

### Redis Caching

Enable Redis for caching AI responses:

```bash
# In .env
ENABLE_AI_CACHE=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Database Connection Pooling

```bash
# In .env
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

---

## Security Checklist

- [ ] Change all default secrets in .env
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Implement authentication
- [ ] Set up PII/PHI redaction
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Enable CORS only for trusted origins
- [ ] Use environment variables for secrets (never commit)

---

## Backup and Recovery

### Database Backups

```bash
# Backup database
pg_dump tender_db > backup_$(date +%Y%m%d).sql

# Restore database
psql tender_db < backup_20240115.sql
```

### Application State

```bash
# Backup important files
tar -czf tender_backup.tar.gz \
  backend/ \
  .env \
  data/
```

---

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use Redis for shared session state
- Database connection pooling

### Vertical Scaling

- Increase worker count
- Allocate more memory
- Use faster AI model API tiers

---

## Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Solution: Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/backend
```

**Issue: Database connection failed**
```bash
# Solution: Check DATABASE_URL and database status
psql $DATABASE_URL
```

**Issue: AI API rate limits**
```bash
# Solution: Enable caching and implement backoff
ENABLE_AI_CACHE=true
```

---

## Maintenance

### Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade fastapi
```

### Log Rotation

```bash
# Set up logrotate
sudo vim /etc/logrotate.d/tender-lawyers
```

---

## Support

For deployment issues:
- Check logs: `journalctl -u tender-lawyers -f`
- GitHub Issues: https://github.com/yourusername/morgan-legaltender/issues
- Email: dhyan.sur@gmail.com
