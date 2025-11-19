"""
Analytics and Metrics for Measuring Impact

Tracks narrative spread, intervention effectiveness, and overall system performance
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from loguru import logger

from monitoring.narrative_detector import Narrative, Post
from response.coordinator import ResponseCampaign


@dataclass
class NarrativeMetrics:
    """Metrics for a disinformation narrative"""
    narrative_id: str
    total_posts: int
    unique_authors: int
    total_reach: int
    peak_velocity: float
    time_to_peak: timedelta
    platforms: List[str]
    dominant_platform: str
    growth_rate: float  # Posts per hour
    engagement_rate: float  # Engagement per post
    coordination_score: float


@dataclass
class InterventionMetrics:
    """Metrics for measuring intervention effectiveness"""
    campaign_id: str
    narrative_id: str
    intervention_time: datetime
    narrative_velocity_before: float
    narrative_velocity_after: float
    velocity_change_pct: float
    counter_content_reach: int
    counter_content_engagement: int
    estimated_prevented_exposure: int
    effectiveness_score: float  # 0-1


@dataclass
class SystemMetrics:
    """Overall system performance metrics"""
    period_start: datetime
    period_end: datetime
    narratives_detected: int
    narratives_by_priority: Dict[str, int]
    avg_detection_time: timedelta  # Time from first post to detection
    alerts_sent: int
    campaigns_launched: int
    total_counter_reach: int
    platform_reports_submitted: int
    false_positive_rate: float


class NarrativeAnalyzer:
    """Analyze narrative spread patterns"""

    def calculate_metrics(self, narrative: Narrative) -> NarrativeMetrics:
        """Calculate comprehensive metrics for a narrative"""

        # Platform distribution
        platform_counts = defaultdict(int)
        for post in narrative.posts:
            platform_counts[post.platform] += 1

        dominant_platform = max(platform_counts.items(), key=lambda x: x[1])[0]

        # Growth rate (posts per hour)
        if len(narrative.posts) > 1:
            time_span = (max(p.timestamp for p in narrative.posts) -
                        min(p.timestamp for p in narrative.posts))
            hours = max(time_span.total_seconds() / 3600, 1.0)
            growth_rate = len(narrative.posts) / hours
        else:
            growth_rate = 0.0

        # Engagement rate
        total_engagement = sum(p.engagement for p in narrative.posts)
        engagement_rate = total_engagement / len(narrative.posts) if narrative.posts else 0

        # Peak velocity (max posts in any 1-hour window)
        peak_velocity, time_to_peak = self._calculate_peak_velocity(narrative.posts)

        return NarrativeMetrics(
            narrative_id=narrative.id,
            total_posts=len(narrative.posts),
            unique_authors=len(narrative.related_accounts),
            total_reach=narrative.estimated_reach,
            peak_velocity=peak_velocity,
            time_to_peak=time_to_peak,
            platforms=list(platform_counts.keys()),
            dominant_platform=dominant_platform,
            growth_rate=growth_rate,
            engagement_rate=engagement_rate,
            coordination_score=narrative.coordination_score
        )

    def _calculate_peak_velocity(self, posts: List[Post]) -> Tuple[float, timedelta]:
        """Calculate peak velocity (max posts in any 1-hour window)"""
        if not posts:
            return 0.0, timedelta(0)

        # Sort by timestamp
        sorted_posts = sorted(posts, key=lambda p: p.timestamp)

        max_velocity = 0.0
        peak_time = timedelta(0)

        # Sliding window to find peak
        for i, post in enumerate(sorted_posts):
            window_end = post.timestamp + timedelta(hours=1)

            # Count posts in 1-hour window
            window_posts = [
                p for p in sorted_posts[i:]
                if p.timestamp <= window_end
            ]

            window_engagement = sum(p.engagement for p in window_posts)

            if window_engagement > max_velocity:
                max_velocity = window_engagement
                peak_time = post.timestamp - sorted_posts[0].timestamp

        return max_velocity, peak_time

    def predict_virality(self, narrative: Narrative) -> Dict[str, any]:
        """
        Predict if narrative will go viral

        Uses early indicators:
        - Initial growth rate
        - Coordination score
        - Engagement rate
        - Platform diversity
        """
        metrics = self.calculate_metrics(narrative)

        # Simple scoring model (in production, use ML)
        virality_score = 0.0

        # High growth rate
        if metrics.growth_rate > 50:
            virality_score += 0.3

        # High coordination (indicates organized campaign)
        virality_score += metrics.coordination_score * 0.3

        # High engagement rate
        if metrics.engagement_rate > 100:
            virality_score += 0.2

        # Multi-platform spread
        if len(metrics.platforms) > 2:
            virality_score += 0.2

        prediction = {
            'will_go_viral': virality_score > 0.6,
            'virality_score': virality_score,
            'estimated_peak_reach': int(metrics.total_reach * (1 + virality_score * 10)),
            'time_to_peak': timedelta(hours=12),  # Simplified
            'confidence': 0.7
        }

        return prediction


class InterventionAnalyzer:
    """Analyze effectiveness of interventions"""

    def measure_effectiveness(self,
                            campaign: ResponseCampaign,
                            narrative_before: Narrative,
                            narrative_after: Optional[Narrative]) -> InterventionMetrics:
        """
        Measure intervention effectiveness

        Args:
            campaign: The response campaign
            narrative_before: Narrative state before intervention
            narrative_after: Narrative state after intervention (if still spreading)

        Returns:
            Intervention effectiveness metrics
        """
        velocity_before = narrative_before.velocity

        if narrative_after:
            velocity_after = narrative_after.velocity
        else:
            velocity_after = 0.0  # Narrative stopped

        velocity_change = ((velocity_after - velocity_before) / velocity_before * 100
                          if velocity_before > 0 else 0)

        # Estimate prevented exposure (how many people we stopped from seeing disinfo)
        # Based on growth rate reduction
        prevented_exposure = max(0, int(
            (velocity_before - velocity_after) * 24  # Over 24 hours
        ))

        # Effectiveness score (0-1)
        # Higher score = narrative slowed down more
        if velocity_before > 0:
            effectiveness = max(0, min(1, 1 - (velocity_after / velocity_before)))
        else:
            effectiveness = 0.5  # Neutral if no baseline

        return InterventionMetrics(
            campaign_id=campaign.id,
            narrative_id=campaign.narrative.id,
            intervention_time=campaign.created_at,
            narrative_velocity_before=velocity_before,
            narrative_velocity_after=velocity_after,
            velocity_change_pct=velocity_change,
            counter_content_reach=campaign.actual_reach,
            counter_content_engagement=0,  # Would track from published content
            estimated_prevented_exposure=prevented_exposure,
            effectiveness_score=effectiveness
        )


class DashboardMetrics:
    """Generate metrics for dashboard display"""

    def __init__(self):
        self.narrative_analyzer = NarrativeAnalyzer()
        self.intervention_analyzer = InterventionAnalyzer()

    def generate_summary(self,
                        narratives: List[Narrative],
                        campaigns: List[ResponseCampaign],
                        period: timedelta = timedelta(days=7)) -> SystemMetrics:
        """
        Generate system-wide summary metrics

        Args:
            narratives: All detected narratives
            campaigns: All response campaigns
            period: Time period to analyze

        Returns:
            System metrics
        """
        cutoff = datetime.now() - period
        recent_narratives = [n for n in narratives if n.first_seen >= cutoff]

        # Count by priority
        priority_counts = defaultdict(int)
        for n in recent_narratives:
            priority_counts[n.priority] += 1

        # Average detection time (time from first post to detection)
        # In real system, would track when narrative was actually detected
        detection_times = []
        for n in recent_narratives:
            if len(n.posts) > 1:
                first_post = min(p.timestamp for p in n.posts)
                # Assume detection happened at last post time (simplified)
                last_post = max(p.timestamp for p in n.posts)
                detection_times.append(last_post - first_post)

        avg_detection = (sum(detection_times, timedelta(0)) / len(detection_times)
                        if detection_times else timedelta(0))

        # Total counter-reach
        total_counter_reach = sum(c.actual_reach for c in campaigns)

        return SystemMetrics(
            period_start=cutoff,
            period_end=datetime.now(),
            narratives_detected=len(recent_narratives),
            narratives_by_priority=dict(priority_counts),
            avg_detection_time=avg_detection,
            alerts_sent=len(recent_narratives),  # Simplified
            campaigns_launched=len(campaigns),
            total_counter_reach=total_counter_reach,
            platform_reports_submitted=0,  # Would track actual reports
            false_positive_rate=0.0  # Would track validated false positives
        )

    def generate_narrative_report(self, narrative: Narrative) -> Dict:
        """Generate detailed report for a single narrative"""
        metrics = self.narrative_analyzer.calculate_metrics(narrative)
        prediction = self.narrative_analyzer.predict_virality(narrative)

        return {
            'narrative': {
                'id': narrative.id,
                'claim': narrative.core_claim,
                'priority': narrative.priority,
                'first_seen': narrative.first_seen.isoformat(),
            },
            'metrics': {
                'posts': metrics.total_posts,
                'authors': metrics.unique_authors,
                'reach': metrics.total_reach,
                'velocity': narrative.velocity,
                'coordination': metrics.coordination_score,
                'platforms': metrics.platforms,
            },
            'prediction': prediction,
            'sample_posts': [
                {
                    'author': p.author,
                    'platform': p.platform,
                    'content': p.content[:200],
                    'url': p.url,
                    'engagement': p.engagement
                }
                for p in narrative.posts[:5]
            ]
        }


class TrendAnalyzer:
    """Analyze trends in disinformation over time"""

    def identify_trending_narratives(self,
                                    narratives: List[Narrative],
                                    window: timedelta = timedelta(hours=6)) -> List[Narrative]:
        """Identify narratives that are trending (rapid growth)"""
        cutoff = datetime.now() - window
        recent = [n for n in narratives if n.first_seen >= cutoff]

        # Sort by velocity
        trending = sorted(recent, key=lambda n: n.velocity, reverse=True)

        return trending[:10]  # Top 10 trending

    def identify_coordinated_campaigns(self,
                                      narratives: List[Narrative],
                                      coordination_threshold: float = 0.7) -> List[List[Narrative]]:
        """
        Identify related narratives that may be part of coordinated campaigns

        Groups narratives by:
        - Similar keywords
        - Overlapping accounts
        - Similar timing
        """
        # Group by keyword overlap
        groups = []

        for narrative in narratives:
            if narrative.coordination_score < coordination_threshold:
                continue

            # Find related narratives
            related = [narrative]

            for other in narratives:
                if other.id == narrative.id:
                    continue

                # Check for overlaps
                keyword_overlap = len(set(narrative.keywords) & set(other.keywords))
                account_overlap = len(narrative.related_accounts & other.related_accounts)

                if keyword_overlap > 2 or account_overlap > 3:
                    related.append(other)

            if len(related) > 1:
                groups.append(related)

        return groups
