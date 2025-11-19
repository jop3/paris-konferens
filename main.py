"""
Main Orchestration Script

Coordinates all components of the counter-disinformation system
"""
import asyncio
from datetime import datetime, timedelta
from typing import List
from loguru import logger

from config.config import settings
from monitoring.narrative_detector import NarrativeDetector
from monitoring.platform_monitors import (
    TwitterMonitor, RedditMonitor, MultiPlatformMonitor
)
from verification.fact_checker import VerificationPipeline
from response.alert_system import (
    AlertManager, EmailAlertHandler, SlackAlertHandler, WebhookAlertHandler, AlertChannel
)
from response.coordinator import ResponseCoordinator
from analytics.metrics import DashboardMetrics


class CounterDisinfoSystem:
    """
    Main counter-disinformation system orchestrator

    Coordinates:
    1. Platform monitoring
    2. Narrative detection
    3. Fact-checking
    4. Alert generation
    5. Response coordination
    6. Analytics tracking
    """

    def __init__(self):
        # Initialize components
        self.platform_monitor = MultiPlatformMonitor()
        self.narrative_detector = NarrativeDetector()
        self.verification_pipeline = VerificationPipeline()
        self.alert_manager = AlertManager()
        self.response_coordinator = ResponseCoordinator()
        self.dashboard_metrics = DashboardMetrics()

        # State tracking
        self.detected_narratives = []
        self.active_campaigns = []

        logger.info("Counter-Disinformation System initialized")

    async def setup(self):
        """Initialize platform monitors and alert handlers"""

        # Setup platform monitors
        if settings.TWITTER_BEARER_TOKEN:
            twitter = TwitterMonitor(settings.TWITTER_BEARER_TOKEN)
            self.platform_monitor.add_monitor("twitter", twitter)
            logger.info("Twitter monitor configured")

        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            reddit = RedditMonitor(
                settings.REDDIT_CLIENT_ID,
                settings.REDDIT_CLIENT_SECRET,
                settings.REDDIT_USER_AGENT
            )
            self.platform_monitor.add_monitor("reddit", reddit)
            logger.info("Reddit monitor configured")

        # Setup alert handlers
        if settings.ALERT_WEBHOOK:
            webhook_handler = WebhookAlertHandler(settings.ALERT_WEBHOOK)
            self.alert_manager.register_handler(
                AlertChannel.WEBHOOK,
                webhook_handler.send
            )
            logger.info("Webhook alerts configured")

        # Add more alert handlers as configured
        # Email, Slack, etc.

        logger.info("System setup complete")

    async def run_monitoring_cycle(self):
        """
        Execute one monitoring cycle

        1. Collect posts from platforms
        2. Detect narratives
        3. Verify claims
        4. Generate alerts
        5. Recommend responses
        """
        logger.info("=== Starting monitoring cycle ===")

        # Step 1: Collect posts from all platforms
        since = datetime.now() - timedelta(hours=6)  # Last 6 hours

        logger.info(f"Collecting posts since {since}")
        posts = await self.platform_monitor.search_all_platforms(
            keywords=settings.MONITOR_KEYWORDS,
            since=since
        )

        logger.info(f"Collected {len(posts)} posts")

        if not posts:
            logger.info("No new posts found")
            return

        # Step 2: Detect narratives
        logger.info("Analyzing posts for coordinated narratives...")
        narratives = await self.narrative_detector.analyze_posts(
            posts,
            time_window=timedelta(hours=24)
        )

        logger.info(f"Detected {len(narratives)} narratives")

        # Step 3: Verify claims in each narrative
        for narrative in narratives:
            logger.info(f"Processing narrative: {narrative.core_claim[:100]}...")

            # Fact-check the narrative
            verification_results = await self.verification_pipeline.verify_content(
                narrative.core_claim
            )

            verification = verification_results[0] if verification_results else None

            # Step 4: Generate alert
            if narrative.priority in ["critical", "high"]:
                alert = await self.alert_manager.create_alert(
                    narrative,
                    verification
                )
                logger.info(f"Alert created: {alert.id}")

            # Step 5: Recommend response strategy
            if narrative.priority in ["critical", "high", "medium"]:
                campaign = await self.response_coordinator.create_response_campaign(
                    narrative,
                    verification,
                    team_members=["response_team"]  # Would be actual team
                )
                self.active_campaigns.append(campaign)
                logger.info(f"Response campaign created: {campaign.id}")

            # Track narrative
            self.detected_narratives.append(narrative)

        # Step 6: Generate metrics
        metrics = self.dashboard_metrics.generate_summary(
            self.detected_narratives,
            self.active_campaigns
        )

        logger.info(f"Cycle complete. Detected: {metrics.narratives_detected}, "
                   f"Campaigns: {metrics.campaigns_launched}")

    async def run_continuous(self, interval_minutes: int = 30):
        """
        Run continuous monitoring

        Args:
            interval_minutes: Minutes between monitoring cycles
        """
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes}m)")

        while True:
            try:
                await self.run_monitoring_cycle()
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")

            # Wait before next cycle
            logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
            await asyncio.sleep(interval_minutes * 60)

    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down system...")
        await self.verification_pipeline.close()
        logger.info("Shutdown complete")


async def main():
    """Main entry point"""

    # Configure logging
    logger.add(
        "logs/disinfo_monitor_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )

    logger.info("=== Counter-Disinformation System Starting ===")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Monitoring keywords: {len(settings.MONITOR_KEYWORDS)}")

    # Initialize system
    system = CounterDisinfoSystem()
    await system.setup()

    try:
        # Run continuous monitoring
        await system.run_continuous(interval_minutes=30)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
