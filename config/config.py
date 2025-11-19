"""
Configuration management for counter-disinformation system
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class PriorityLevel(str, Enum):
    CRITICAL = "critical"  # Immediate intervention needed
    HIGH = "high"  # Respond within hours
    MEDIUM = "medium"  # Monitor and respond within 24h
    LOW = "low"  # Track but no immediate action


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Counter-Disinformation System"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/disinfo_monitor"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Social Media API Keys (set via environment variables)
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "Counter-Disinformation Monitor v1.0"

    # Monitoring Configuration
    MONITOR_KEYWORDS: List[str] = [
        # Election integrity
        "voter fraud", "stolen election", "rigged election", "ballot harvesting",
        # Health disinfo
        "vaccine injuries", "plandemic", "covid hoax", "ivermectin cure",
        # Institutional attacks
        "deep state", "fake news media", "corrupt fbi",
    ]

    # Platform monitoring targets
    MONITOR_SUBREDDITS: List[str] = [
        "politics", "news", "worldnews", "conservative", "conspiracy"
    ]

    MONITOR_TWITTER_ACCOUNTS: List[str] = []  # Add specific accounts to monitor

    # Fact-checking sources
    FACTCHECK_APIS: List[str] = [
        "factcheck.org",
        "snopes.com",
        "politifact.com",
        "fullfact.org",  # UK
        "correctiv.org",  # Germany
    ]

    # Alert thresholds
    VIRAL_THRESHOLD: int = 1000  # Engagement count to trigger alert
    VELOCITY_THRESHOLD: float = 100.0  # Engagements per hour
    COORDINATION_THRESHOLD: int = 5  # Number of coordinated accounts

    # Response settings
    ALERT_EMAIL: Optional[str] = None
    ALERT_WEBHOOK: Optional[str] = None
    RESPONSE_TEAM_SIZE: int = 5

    # ML Models
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    SIMILARITY_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Rate limiting (respect platform APIs)
    TWITTER_RATE_LIMIT: int = 450  # Requests per 15 min window
    REDDIT_RATE_LIMIT: int = 60  # Requests per minute

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
