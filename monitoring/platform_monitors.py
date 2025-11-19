"""
Platform-specific monitoring implementations

Collects posts from various social media platforms while respecting rate limits
and Terms of Service.
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, AsyncIterator
import tweepy
import praw
from loguru import logger

from monitoring.narrative_detector import Post


class PlatformMonitor(ABC):
    """Base class for platform-specific monitors"""

    @abstractmethod
    async def search_keywords(self, keywords: List[str],
                             since: datetime) -> List[Post]:
        """Search for keywords on the platform"""
        pass

    @abstractmethod
    async def monitor_accounts(self, accounts: List[str],
                              since: datetime) -> List[Post]:
        """Monitor specific accounts"""
        pass

    @abstractmethod
    async def get_trending_topics(self) -> List[str]:
        """Get currently trending topics"""
        pass


class TwitterMonitor(PlatformMonitor):
    """
    Twitter/X monitoring implementation

    Uses Twitter API v2 with proper rate limiting and authentication
    """

    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(bearer_token=bearer_token,
                                    wait_on_rate_limit=True)
        self.platform = "twitter"

    async def search_keywords(self, keywords: List[str],
                             since: datetime,
                             max_results: int = 100) -> List[Post]:
        """
        Search for tweets containing keywords

        Args:
            keywords: List of search terms
            since: Get tweets after this timestamp
            max_results: Maximum tweets to retrieve per keyword
        """
        posts = []

        for keyword in keywords:
            try:
                # Build query with keyword and time filter
                query = f'"{keyword}" -is:retweet lang:en'

                # Search recent tweets
                response = self.client.search_recent_tweets(
                    query=query,
                    start_time=since.isoformat() + "Z",
                    max_results=min(max_results, 100),  # API limit
                    tweet_fields=['created_at', 'public_metrics', 'author_id'],
                    expansions=['author_id'],
                    user_fields=['username']
                )

                if not response.data:
                    continue

                # Build user lookup
                users = {u.id: u.username for u in response.includes.get('users', [])}

                for tweet in response.data:
                    metrics = tweet.public_metrics
                    engagement = (metrics['like_count'] +
                                metrics['retweet_count'] +
                                metrics['reply_count'])

                    post = Post(
                        id=tweet.id,
                        platform=self.platform,
                        author=users.get(tweet.author_id, 'unknown'),
                        content=tweet.text,
                        timestamp=tweet.created_at,
                        engagement=engagement,
                        url=f"https://twitter.com/i/web/status/{tweet.id}",
                        metadata={
                            'metrics': metrics,
                            'keyword': keyword
                        }
                    )
                    posts.append(post)

                # Respect rate limits (small delay between searches)
                await asyncio.sleep(1)

            except tweepy.TweepyException as e:
                logger.error(f"Twitter API error for keyword '{keyword}': {e}")
                continue

        logger.info(f"Collected {len(posts)} tweets for {len(keywords)} keywords")
        return posts

    async def monitor_accounts(self, accounts: List[str],
                              since: datetime) -> List[Post]:
        """Monitor specific Twitter accounts for new tweets"""
        posts = []

        for username in accounts:
            try:
                # Get user ID
                user = self.client.get_user(username=username)
                if not user.data:
                    continue

                user_id = user.data.id

                # Get recent tweets
                response = self.client.get_users_tweets(
                    id=user_id,
                    start_time=since.isoformat() + "Z",
                    max_results=100,
                    tweet_fields=['created_at', 'public_metrics'],
                    exclude=['retweets', 'replies']
                )

                if not response.data:
                    continue

                for tweet in response.data:
                    metrics = tweet.public_metrics
                    engagement = (metrics['like_count'] +
                                metrics['retweet_count'] +
                                metrics['reply_count'])

                    post = Post(
                        id=tweet.id,
                        platform=self.platform,
                        author=username,
                        content=tweet.text,
                        timestamp=tweet.created_at,
                        engagement=engagement,
                        url=f"https://twitter.com/{username}/status/{tweet.id}",
                        metadata={'metrics': metrics, 'monitored_account': True}
                    )
                    posts.append(post)

                await asyncio.sleep(1)

            except tweepy.TweepyException as e:
                logger.error(f"Error monitoring account @{username}: {e}")
                continue

        return posts

    async def get_trending_topics(self, woeid: int = 1) -> List[str]:
        """
        Get trending topics (Note: Requires Twitter API v1.1)
        woeid: Where On Earth ID (1 = worldwide, 23424977 = USA)
        """
        # Note: This requires v1.1 API access
        # Implementation would use trends/place endpoint
        # Returning placeholder for now
        return []


class RedditMonitor(PlatformMonitor):
    """
    Reddit monitoring implementation

    Monitors subreddits for posts and comments containing keywords
    """

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.platform = "reddit"

    async def search_keywords(self, keywords: List[str],
                             since: datetime,
                             subreddits: Optional[List[str]] = None,
                             limit: int = 100) -> List[Post]:
        """
        Search Reddit for keywords

        Args:
            keywords: Search terms
            since: Get posts after this time
            subreddits: List of subreddits to search (None = all)
            limit: Max results per keyword
        """
        posts = []
        since_timestamp = since.timestamp()

        # Determine search scope
        if subreddits:
            search_target = "+".join(subreddits)
            subreddit = self.reddit.subreddit(search_target)
        else:
            subreddit = self.reddit.subreddit("all")

        for keyword in keywords:
            try:
                # Search submissions
                for submission in subreddit.search(keyword,
                                                  sort='new',
                                                  time_filter='day',
                                                  limit=limit):
                    # Filter by timestamp
                    if submission.created_utc < since_timestamp:
                        continue

                    post = Post(
                        id=submission.id,
                        platform=self.platform,
                        author=str(submission.author) if submission.author else '[deleted]',
                        content=f"{submission.title}\n\n{submission.selftext}",
                        timestamp=datetime.fromtimestamp(submission.created_utc),
                        engagement=submission.score + submission.num_comments,
                        url=f"https://reddit.com{submission.permalink}",
                        metadata={
                            'subreddit': submission.subreddit.display_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'keyword': keyword
                        }
                    )
                    posts.append(post)

                await asyncio.sleep(2)  # Respect rate limits

            except Exception as e:
                logger.error(f"Reddit search error for '{keyword}': {e}")
                continue

        logger.info(f"Collected {len(posts)} Reddit posts for {len(keywords)} keywords")
        return posts

    async def monitor_accounts(self, accounts: List[str],
                              since: datetime) -> List[Post]:
        """Monitor specific Reddit users"""
        posts = []
        since_timestamp = since.timestamp()

        for username in accounts:
            try:
                user = self.reddit.redditor(username)

                # Get recent submissions
                for submission in user.submissions.new(limit=50):
                    if submission.created_utc < since_timestamp:
                        continue

                    post = Post(
                        id=submission.id,
                        platform=self.platform,
                        author=username,
                        content=f"{submission.title}\n\n{submission.selftext}",
                        timestamp=datetime.fromtimestamp(submission.created_utc),
                        engagement=submission.score + submission.num_comments,
                        url=f"https://reddit.com{submission.permalink}",
                        metadata={
                            'subreddit': submission.subreddit.display_name,
                            'monitored_account': True
                        }
                    )
                    posts.append(post)

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error monitoring Reddit user u/{username}: {e}")
                continue

        return posts

    async def get_trending_topics(self, subreddits: List[str] = None) -> List[str]:
        """Get trending topics from subreddit(s)"""
        if not subreddits:
            subreddits = ['all']

        trending = []
        for sub_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=10):
                    trending.append(post.title)
            except Exception as e:
                logger.error(f"Error getting trending from r/{sub_name}: {e}")

        return trending


class MultiPlatformMonitor:
    """
    Aggregates monitoring across multiple platforms
    """

    def __init__(self):
        self.monitors: Dict[str, PlatformMonitor] = {}

    def add_monitor(self, name: str, monitor: PlatformMonitor):
        """Register a platform monitor"""
        self.monitors[name] = monitor
        logger.info(f"Registered monitor for {name}")

    async def search_all_platforms(self, keywords: List[str],
                                   since: datetime) -> List[Post]:
        """
        Search all registered platforms concurrently
        """
        tasks = []
        for name, monitor in self.monitors.items():
            task = monitor.search_keywords(keywords, since)
            tasks.append(task)

        # Run all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_posts = []
        for result in results:
            if isinstance(result, list):
                all_posts.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Monitor error: {result}")

        logger.info(f"Collected {len(all_posts)} total posts from {len(self.monitors)} platforms")
        return all_posts

    async def monitor_all_accounts(self, accounts: Dict[str, List[str]],
                                   since: datetime) -> List[Post]:
        """
        Monitor accounts across platforms

        Args:
            accounts: Dict mapping platform name to list of account names
            since: Get posts since this time
        """
        tasks = []
        for platform_name, account_list in accounts.items():
            if platform_name in self.monitors:
                task = self.monitors[platform_name].monitor_accounts(
                    account_list, since
                )
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_posts = []
        for result in results:
            if isinstance(result, list):
                all_posts.extend(result)

        return all_posts
