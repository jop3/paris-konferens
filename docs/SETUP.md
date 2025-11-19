# Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis
- API keys for social media platforms

## Installation

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb disinfo_monitor

# Run migrations (if using Alembic)
alembic upgrade head
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/disinfo_monitor
REDIS_URL=redis://localhost:6379/0

# Twitter/X API (get from https://developer.twitter.com)
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Reddit API (get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Counter-Disinformation Monitor v1.0

# Alert Configuration
ALERT_EMAIL=alerts@yourdomain.com
ALERT_WEBHOOK=https://your-webhook-url.com/alerts

# Optional: Slack webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 4. Configure Monitoring Targets

Edit `config/config.py` to customize:

- **Keywords to monitor**: Topics you want to track
- **Subreddits**: Which Reddit communities to monitor
- **Alert thresholds**: When to trigger alerts
- **Fact-check sources**: Which fact-checkers to use

Example keywords for election integrity:
```python
MONITOR_KEYWORDS = [
    "voter fraud",
    "stolen election",
    "rigged election",
    "ballot harvesting",
    "illegal voting",
]
```

## Running the System

### Development Mode

```bash
# Run single monitoring cycle (for testing)
python main.py
```

### Production Mode

```bash
# Run continuous monitoring
python main.py

# Or use systemd service (see docs/deployment.md)
```

### Using Docker (Recommended)

```bash
# Build container
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## API Keys Setup

### Twitter/X API

1. Apply for developer access: https://developer.twitter.com
2. Create a new app
3. Generate Bearer Token (for API v2)
4. Add to `.env` file

**Rate limits**: Free tier allows 500,000 tweets/month

### Reddit API

1. Go to https://www.reddit.com/prefs/apps
2. Create an app (script type)
3. Note the client ID and secret
4. Add to `.env` file

**Rate limits**: 60 requests per minute

### Optional: Additional Platforms

- **Bluesky**: Uses AT Protocol, no API key needed
- **Mastodon**: Create app on your instance
- **Facebook/Instagram**: Requires business account

## Verification

Test the setup:

```bash
# Test platform connections
python -c "
from monitoring.platform_monitors import TwitterMonitor
import os
monitor = TwitterMonitor(os.getenv('TWITTER_BEARER_TOKEN'))
print('Twitter API: OK')
"

# Test narrative detection
python -c "
from monitoring.narrative_detector import NarrativeDetector
detector = NarrativeDetector()
print('Narrative detector: OK')
"
```

## Next Steps

1. **Configure alerts**: Set up Slack/email notifications
2. **Customize keywords**: Add topics relevant to your focus
3. **Set up response team**: Add team members who can respond
4. **Review ethical guidelines**: See `docs/ETHICS.md`

## Troubleshooting

### API Connection Errors

- Verify API keys are correct
- Check rate limits haven't been exceeded
- Ensure network can reach API endpoints

### Database Errors

- Verify PostgreSQL is running: `pg_isready`
- Check credentials in DATABASE_URL
- Ensure database exists

### No Narratives Detected

- Check if keywords are finding posts
- Lower detection thresholds in config
- Verify time windows are appropriate

## Support

For issues or questions:
- Check documentation in `/docs`
- Review logs in `/logs`
- Open GitHub issue with details
