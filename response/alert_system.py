"""
Alert System for Emerging Disinformation

Notifies response teams when critical narratives are detected
"""
import asyncio
from typing import List, Optional, Dict, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from loguru import logger

from monitoring.narrative_detector import Narrative
from verification.fact_checker import VerificationResult


class AlertChannel(str, Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    SMS = "sms"


@dataclass
class Alert:
    """Alert notification"""
    id: str
    narrative: Narrative
    verification: Optional[VerificationResult]
    created_at: datetime
    priority: str
    message: str
    channels: List[AlertChannel]
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class AlertManager:
    """
    Manages alert creation, routing, and tracking
    """

    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: Dict[AlertChannel, Callable] = {}
        self.alert_history: List[Alert] = []

    def register_handler(self, channel: AlertChannel, handler: Callable):
        """Register a handler for an alert channel"""
        self.alert_handlers[channel] = handler
        logger.info(f"Registered handler for {channel}")

    async def create_alert(self, narrative: Narrative,
                          verification: Optional[VerificationResult] = None) -> Alert:
        """
        Create and send an alert for a detected narrative

        Args:
            narrative: The detected disinformation narrative
            verification: Fact-check results (if available)

        Returns:
            Created alert
        """
        # Generate alert message
        message = self._format_alert_message(narrative, verification)

        # Determine channels based on priority
        channels = self._select_channels(narrative.priority)

        alert = Alert(
            id=f"alert_{narrative.id}_{int(datetime.now().timestamp())}",
            narrative=narrative,
            verification=verification,
            created_at=datetime.now(),
            priority=narrative.priority,
            message=message,
            channels=channels
        )

        # Send to all channels
        await self._send_alert(alert)

        # Track alert
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)

        logger.info(f"Created alert {alert.id} with priority {alert.priority}")
        return alert

    def _format_alert_message(self, narrative: Narrative,
                             verification: Optional[VerificationResult]) -> str:
        """Format alert message for human readability"""
        message = f"""
🚨 DISINFORMATION ALERT - {narrative.priority.upper()} PRIORITY

Narrative Detected: {narrative.core_claim[:200]}...

📊 Metrics:
- Posts: {len(narrative.posts)}
- Estimated Reach: {narrative.estimated_reach:,}
- Velocity: {narrative.velocity:.1f} engagements/hour
- Coordination Score: {narrative.coordination_score:.2f}

🔍 First Seen: {narrative.first_seen.strftime('%Y-%m-%d %H:%M UTC')}

🏷️ Keywords: {', '.join(narrative.keywords[:10])}

👥 Related Accounts: {len(narrative.related_accounts)} accounts
"""

        # Add verification results if available
        if verification:
            message += f"""
✅ FACT-CHECK STATUS: {verification.consensus_verdict.upper()}
Confidence: {verification.confidence:.0%}
Based on {len(verification.fact_checks)} source(s)

{verification.summary[:500]}
"""
        else:
            message += "\n⚠️ NO FACT-CHECK AVAILABLE - Manual verification needed\n"

        # Add sample posts
        message += "\n📱 Sample Posts:\n"
        for i, post in enumerate(narrative.posts[:3], 1):
            message += f"\n{i}. @{post.author} ({post.platform}):\n"
            message += f"   {post.content[:150]}...\n"
            message += f"   {post.url}\n"

        # Add recommended actions
        message += self._get_recommended_actions(narrative, verification)

        return message

    def _get_recommended_actions(self, narrative: Narrative,
                                 verification: Optional[VerificationResult]) -> str:
        """Suggest response actions based on narrative characteristics"""
        actions = "\n🎯 RECOMMENDED ACTIONS:\n"

        if narrative.priority == "critical":
            actions += "1. IMMEDIATE RESPONSE NEEDED\n"
            actions += "2. Activate rapid response team\n"
            actions += "3. Prepare counter-messaging\n"
            actions += "4. Contact platform trust & safety teams\n"
        elif narrative.priority == "high":
            actions += "1. Respond within 2 hours\n"
            actions += "2. Prepare fact-check response\n"
            actions += "3. Monitor for escalation\n"
        else:
            actions += "1. Monitor narrative spread\n"
            actions += "2. Prepare response if escalates\n"

        if verification and verification.consensus_verdict in ["false", "mostly_false"]:
            actions += "5. Share existing fact-checks widely\n"
            actions += "6. Engage credible voices to counter\n"

        if narrative.coordination_score > 0.7:
            actions += "7. Report coordinated inauthentic behavior to platforms\n"

        return actions

    def _select_channels(self, priority: str) -> List[AlertChannel]:
        """Select alert channels based on priority"""
        if priority == "critical":
            return [AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.SMS]
        elif priority == "high":
            return [AlertChannel.EMAIL, AlertChannel.SLACK]
        elif priority == "medium":
            return [AlertChannel.SLACK]
        else:
            return [AlertChannel.WEBHOOK]  # Low priority - log only

    async def _send_alert(self, alert: Alert):
        """Send alert through all configured channels"""
        tasks = []

        for channel in alert.channels:
            if channel in self.alert_handlers:
                handler = self.alert_handlers[channel]
                task = handler(alert)
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Mark alert as acknowledged"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts"""
        return [a for a in self.active_alerts.values() if not a.acknowledged]


class EmailAlertHandler:
    """Send alerts via email"""

    def __init__(self, smtp_host: str, smtp_port: int,
                 username: str, password: str,
                 from_addr: str, to_addrs: List[str]):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    async def send(self, alert: Alert):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            msg['Subject'] = f"[{alert.priority.upper()}] Disinformation Alert: {alert.narrative.core_claim[:50]}"

            msg.attach(MIMEText(alert.message, 'plain'))

            # Send email (in thread pool to avoid blocking)
            await asyncio.to_thread(self._send_smtp, msg)

            logger.info(f"Email alert sent for {alert.id}")

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def _send_smtp(self, msg: MIMEMultipart):
        """Send via SMTP (blocking operation)"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class WebhookAlertHandler:
    """Send alerts via webhook"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send(self, alert: Alert):
        """Send webhook alert"""
        try:
            payload = {
                'alert_id': alert.id,
                'priority': alert.priority,
                'narrative': {
                    'claim': alert.narrative.core_claim,
                    'posts': len(alert.narrative.posts),
                    'reach': alert.narrative.estimated_reach,
                    'velocity': alert.narrative.velocity,
                    'coordination': alert.narrative.coordination_score,
                },
                'message': alert.message,
                'timestamp': alert.created_at.isoformat()
            }

            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                logger.info(f"Webhook alert sent for {alert.id}")
            else:
                logger.warning(f"Webhook returned status {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    async def close(self):
        await self.client.aclose()


class SlackAlertHandler:
    """Send alerts to Slack"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send(self, alert: Alert):
        """Send Slack alert with rich formatting"""
        try:
            # Build Slack blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {alert.priority.upper()} Priority Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Narrative:* {alert.narrative.core_claim[:200]}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Posts:*\n{len(alert.narrative.posts)}"},
                        {"type": "mrkdwn", "text": f"*Reach:*\n{alert.narrative.estimated_reach:,}"},
                        {"type": "mrkdwn", "text": f"*Velocity:*\n{alert.narrative.velocity:.0f}/hr"},
                        {"type": "mrkdwn", "text": f"*Coordination:*\n{alert.narrative.coordination_score:.0%}"},
                    ]
                }
            ]

            # Add fact-check status if available
            if alert.verification:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Fact-Check:* {alert.verification.consensus_verdict.upper()} ({alert.verification.confidence:.0%} confidence)"
                    }
                })

            # Add action buttons
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Acknowledge"},
                        "value": alert.id,
                        "action_id": "acknowledge_alert"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Details"},
                        "url": f"http://dashboard/alerts/{alert.id}",
                        "action_id": "view_details"
                    }
                ]
            })

            payload = {
                "blocks": blocks,
                "text": f"Alert: {alert.narrative.core_claim[:100]}"  # Fallback text
            }

            response = await self.client.post(self.webhook_url, json=payload)

            if response.status_code == 200:
                logger.info(f"Slack alert sent for {alert.id}")
            else:
                logger.warning(f"Slack webhook returned {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def close(self):
        await self.client.aclose()
