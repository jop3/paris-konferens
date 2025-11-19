"""
Response Coordination System

Coordinates counter-messaging responses to disinformation narratives
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
from loguru import logger

from monitoring.narrative_detector import Narrative
from verification.fact_checker import VerificationResult


class ResponseStrategy(str, Enum):
    """Response strategy types"""
    FACT_CHECK = "fact_check"  # Share verified fact-checks
    COUNTER_NARRATIVE = "counter_narrative"  # Alternative framing
    INOCULATION = "inoculation"  # Pre-bunking techniques
    AMPLIFY_TRUTH = "amplify_truth"  # Boost accurate information
    PLATFORM_REPORT = "platform_report"  # Report to platform T&S
    MEDIA_OUTREACH = "media_outreach"  # Contact journalists
    IGNORE = "ignore"  # Sometimes best not to amplify


class ResponseType(str, Enum):
    """Type of response content"""
    SOCIAL_POST = "social_post"
    ARTICLE = "article"
    INFOGRAPHIC = "infographic"
    VIDEO = "video"
    THREAD = "thread"
    PLATFORM_REPORT = "platform_report"


@dataclass
class ResponseContent:
    """Content for counter-messaging"""
    id: str
    narrative_id: str
    content_type: ResponseType
    text: str
    media_urls: List[str]
    hashtags: List[str]
    target_platforms: List[str]
    created_at: datetime
    created_by: str
    approved: bool = False
    approved_by: Optional[str] = None
    published: bool = False
    published_at: Optional[datetime] = None
    engagement_metrics: Dict = None


@dataclass
class ResponseCampaign:
    """Coordinated response campaign"""
    id: str
    narrative: Narrative
    verification: Optional[VerificationResult]
    strategy: ResponseStrategy
    content_pieces: List[ResponseContent]
    team_members: List[str]
    created_at: datetime
    status: str  # planning, active, completed
    target_reach: int
    actual_reach: int = 0


class ResponseCoordinator:
    """
    Coordinates response campaigns to counter disinformation

    Key principles:
    - Transparency: All content is clearly attributed
    - Quality over quantity: Focus on compelling, factual content
    - Strategic timing: Respond early before narratives spread
    - Multi-platform: Coordinate across platforms
    """

    def __init__(self):
        self.active_campaigns: Dict[str, ResponseCampaign] = {}
        self.content_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load response content templates"""
        return {
            'fact_check_twitter': """
🔍 FACT-CHECK: {claim}

✅ Verdict: {verdict}

{explanation}

Sources:
{sources}

#FactCheck #Verification
            """,

            'fact_check_thread': """
Thread: Fact-checking a viral claim 🧵

1/ The claim: "{claim}"

2/ The verdict: {verdict}

{thread_content}

{conclusion}
            """,

            'inoculation': """
⚠️ MANIPULATION ALERT

We're seeing a coordinated campaign spreading {narrative_type}.

Here's how to spot it:
{warning_signs}

Don't fall for it. Always verify before sharing.
            """,

            'pre_bunk': """
Heads up: We expect to see disinformation about {topic} soon.

Watch out for:
{tactics}

Get the facts: {fact_sources}
            """,
        }

    async def create_response_campaign(self,
                                      narrative: Narrative,
                                      verification: Optional[VerificationResult],
                                      team_members: List[str]) -> ResponseCampaign:
        """
        Create a coordinated response campaign

        Args:
            narrative: The narrative to counter
            verification: Fact-check results
            team_members: People coordinating the response

        Returns:
            Response campaign
        """
        # Determine response strategy
        strategy = self._select_strategy(narrative, verification)

        campaign = ResponseCampaign(
            id=f"campaign_{narrative.id}",
            narrative=narrative,
            verification=verification,
            strategy=strategy,
            content_pieces=[],
            team_members=team_members,
            created_at=datetime.now(),
            status="planning",
            target_reach=narrative.estimated_reach * 2  # Aim to reach 2x the disinfo reach
        )

        # Generate initial content recommendations
        content_recommendations = await self._generate_content_recommendations(
            campaign
        )

        logger.info(f"Created response campaign {campaign.id} with strategy {strategy}")
        logger.info(f"Recommended {len(content_recommendations)} content pieces")

        self.active_campaigns[campaign.id] = campaign

        return campaign

    def _select_strategy(self, narrative: Narrative,
                        verification: Optional[VerificationResult]) -> ResponseStrategy:
        """
        Select response strategy based on narrative characteristics

        Decision tree:
        - If verified as false → FACT_CHECK
        - If high coordination → PLATFORM_REPORT + FACT_CHECK
        - If rapidly spreading → COUNTER_NARRATIVE
        - If pre-viral → INOCULATION
        - If low priority → AMPLIFY_TRUTH or IGNORE
        """
        # Verified falsehood → fact-check
        if verification and verification.consensus_verdict in ["false", "mostly_false"]:
            return ResponseStrategy.FACT_CHECK

        # High coordination → report to platforms
        if narrative.coordination_score > 0.7:
            return ResponseStrategy.PLATFORM_REPORT

        # Rapid spread → counter-narrative
        if narrative.velocity > 200:
            return ResponseStrategy.COUNTER_NARRATIVE

        # Early stage → inoculation
        if narrative.velocity < 50 and len(narrative.posts) < 20:
            return ResponseStrategy.INOCULATION

        # Low priority → amplify accurate info instead
        if narrative.priority == "low":
            return ResponseStrategy.AMPLIFY_TRUTH

        return ResponseStrategy.FACT_CHECK

    async def _generate_content_recommendations(self,
                                               campaign: ResponseCampaign) -> List[Dict]:
        """
        Generate recommended content for the campaign

        Returns suggestions, not auto-posted content
        """
        recommendations = []

        if campaign.strategy == ResponseStrategy.FACT_CHECK:
            # Recommend fact-check posts
            recommendations.extend(
                self._recommend_fact_check_content(campaign)
            )

        elif campaign.strategy == ResponseStrategy.COUNTER_NARRATIVE:
            # Recommend alternative framing
            recommendations.extend(
                self._recommend_counter_narrative(campaign)
            )

        elif campaign.strategy == ResponseStrategy.INOCULATION:
            # Recommend pre-bunking content
            recommendations.extend(
                self._recommend_inoculation_content(campaign)
            )

        elif campaign.strategy == ResponseStrategy.PLATFORM_REPORT:
            # Generate platform reports
            recommendations.extend(
                self._generate_platform_reports(campaign)
            )

        return recommendations

    def _recommend_fact_check_content(self, campaign: ResponseCampaign) -> List[Dict]:
        """Recommend fact-check content"""
        recommendations = []

        if not campaign.verification:
            return recommendations

        # Twitter/X thread
        thread_content = self._build_fact_check_thread(
            campaign.narrative.core_claim,
            campaign.verification
        )

        recommendations.append({
            'type': ResponseType.THREAD,
            'platform': 'twitter',
            'content': thread_content,
            'priority': 'high',
            'template': 'fact_check_thread'
        })

        # Short fact-check post
        short_post = self._build_fact_check_post(
            campaign.narrative.core_claim,
            campaign.verification
        )

        recommendations.append({
            'type': ResponseType.SOCIAL_POST,
            'platforms': ['twitter', 'bluesky', 'mastodon'],
            'content': short_post,
            'priority': 'high',
            'template': 'fact_check_twitter'
        })

        return recommendations

    def _build_fact_check_thread(self, claim: str,
                                 verification: VerificationResult) -> str:
        """Build a fact-check thread"""
        thread = []

        # Tweet 1: The claim
        thread.append(f"FACT-CHECK THREAD 🧵\n\nClaim: \"{claim[:200]}\"")

        # Tweet 2: The verdict
        verdict_emoji = {
            "false": "❌",
            "mostly_false": "⚠️",
            "mixed": "⚖️",
            "mostly_true": "✓",
            "true": "✅"
        }
        emoji = verdict_emoji.get(verification.consensus_verdict, "🔍")

        thread.append(f"{emoji} Verdict: {verification.consensus_verdict.upper()}\n\nConfidence: {verification.confidence:.0%} based on {len(verification.fact_checks)} independent sources")

        # Tweet 3-N: Evidence
        if verification.fact_checks:
            thread.append("Evidence from trusted fact-checkers:")

            for i, fc in enumerate(verification.fact_checks[:3], 1):
                thread.append(f"{i}. {fc.source}: {fc.verdict.value}\n{fc.url}")

        # Final tweet: Call to action
        thread.append("Always verify before sharing. Spread facts, not fiction. 🔍✅")

        return "\n\n---TWEET BREAK---\n\n".join(thread)

    def _build_fact_check_post(self, claim: str,
                               verification: VerificationResult) -> str:
        """Build a concise fact-check post"""
        template = self.content_templates['fact_check_twitter']

        sources_text = "\n".join([
            f"- {fc.source}: {fc.url}"
            for fc in verification.fact_checks[:2]
        ])

        return template.format(
            claim=claim[:150],
            verdict=verification.consensus_verdict.upper(),
            explanation=verification.summary[:200],
            sources=sources_text
        )

    def _recommend_counter_narrative(self, campaign: ResponseCampaign) -> List[Dict]:
        """Recommend counter-narrative content"""
        # Generate alternative framing that addresses the underlying concern
        # without directly repeating the false claim (avoids backfire effect)

        recommendations = []

        # This would use more sophisticated content generation
        # For now, returning placeholder

        recommendations.append({
            'type': ResponseType.SOCIAL_POST,
            'platforms': ['twitter', 'bluesky'],
            'content': f"Here's what you need to know about {campaign.narrative.keywords[0]}...",
            'priority': 'medium',
            'note': 'Counter-narrative needed - avoids repeating false claim'
        })

        return recommendations

    def _recommend_inoculation_content(self, campaign: ResponseCampaign) -> List[Dict]:
        """Recommend inoculation/pre-bunking content"""
        recommendations = []

        template = self.content_templates['inoculation']

        content = template.format(
            narrative_type=campaign.narrative.keywords[0] if campaign.narrative.keywords else "false claims",
            warning_signs="- Coordinated posting\n- Emotional language\n- Lack of sources"
        )

        recommendations.append({
            'type': ResponseType.SOCIAL_POST,
            'platforms': ['twitter', 'bluesky', 'mastodon'],
            'content': content,
            'priority': 'medium',
            'template': 'inoculation'
        })

        return recommendations

    def _generate_platform_reports(self, campaign: ResponseCampaign) -> List[Dict]:
        """Generate reports for platform Trust & Safety teams"""
        reports = []

        # Group posts by platform
        by_platform = {}
        for post in campaign.narrative.posts:
            if post.platform not in by_platform:
                by_platform[post.platform] = []
            by_platform[post.platform].append(post)

        # Generate report for each platform
        for platform, posts in by_platform.items():
            report = {
                'type': ResponseType.PLATFORM_REPORT,
                'platform': platform,
                'violation_type': 'Coordinated Inauthentic Behavior',
                'posts': [p.url for p in posts],
                'accounts': list(set(p.author for p in posts)),
                'evidence': {
                    'coordination_score': campaign.narrative.coordination_score,
                    'temporal_clustering': 'High',
                    'identical_content': len(set(p.content for p in posts)) < len(posts) * 0.5
                },
                'priority': 'high' if campaign.narrative.coordination_score > 0.7 else 'medium'
            }

            reports.append(report)

        return reports


class ContentReviewQueue:
    """
    Queue for reviewing and approving response content

    All content must be human-reviewed before publication
    """

    def __init__(self):
        self.pending_review: List[ResponseContent] = []
        self.approved: List[ResponseContent] = []

    def submit_for_review(self, content: ResponseContent):
        """Submit content for review"""
        self.pending_review.append(content)
        logger.info(f"Content {content.id} submitted for review")

    def approve(self, content_id: str, approver: str) -> bool:
        """Approve content for publication"""
        for content in self.pending_review:
            if content.id == content_id:
                content.approved = True
                content.approved_by = approver
                self.approved.append(content)
                self.pending_review.remove(content)
                logger.info(f"Content {content_id} approved by {approver}")
                return True

        return False

    def get_pending(self) -> List[ResponseContent]:
        """Get content pending review"""
        return self.pending_review
