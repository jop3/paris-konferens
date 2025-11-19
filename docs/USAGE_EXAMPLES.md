# Usage Examples

## Quick Start

### Run a Single Monitoring Cycle

```python
import asyncio
from main import CounterDisinfoSystem

async def test_run():
    system = CounterDisinfoSystem()
    await system.setup()
    await system.run_monitoring_cycle()
    await system.shutdown()

asyncio.run(test_run())
```

### Monitor Specific Keywords

```python
from monitoring.platform_monitors import TwitterMonitor
from monitoring.narrative_detector import NarrativeDetector
from datetime import datetime, timedelta
import asyncio

async def monitor_keyword(keyword: str):
    # Initialize
    monitor = TwitterMonitor(bearer_token="YOUR_TOKEN")
    detector = NarrativeDetector()

    # Search for keyword in last 24 hours
    since = datetime.now() - timedelta(hours=24)
    posts = await monitor.search_keywords([keyword], since)

    print(f"Found {len(posts)} posts mentioning '{keyword}'")

    # Detect narratives
    narratives = await detector.analyze_posts(posts)

    for narrative in narratives:
        print(f"\nNarrative detected:")
        print(f"  Priority: {narrative.priority}")
        print(f"  Claim: {narrative.core_claim[:200]}")
        print(f"  Posts: {len(narrative.posts)}")
        print(f"  Reach: {narrative.estimated_reach:,}")
        print(f"  Velocity: {narrative.velocity:.1f}/hour")
        print(f"  Coordination: {narrative.coordination_score:.2%}")

asyncio.run(monitor_keyword("election integrity"))
```

### Verify a Claim

```python
from verification.fact_checker import VerificationPipeline
import asyncio

async def check_claim(claim: str):
    pipeline = VerificationPipeline()

    results = await pipeline.verify_content(claim)

    for result in results:
        print(f"\nClaim: {result.original_claim}")
        print(f"Verdict: {result.consensus_verdict}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Based on {len(result.fact_checks)} sources")
        print(f"\n{result.summary}")

    await pipeline.close()

asyncio.run(check_claim(
    "The 2020 election had widespread voter fraud"
))
```

### Set Up Custom Alerts

```python
from response.alert_system import AlertManager, SlackAlertHandler, AlertChannel
from monitoring.narrative_detector import Narrative
import asyncio

async def setup_alerts():
    # Initialize alert manager
    alert_mgr = AlertManager()

    # Add Slack handler
    slack = SlackAlertHandler("https://hooks.slack.com/services/YOUR/WEBHOOK")
    alert_mgr.register_handler(AlertChannel.SLACK, slack.send)

    # Create alert for a narrative (example)
    # In practice, this comes from the monitoring system
    alert = await alert_mgr.create_alert(your_narrative)

    print(f"Alert created: {alert.id}")
    print(f"Sent to channels: {alert.channels}")

# asyncio.run(setup_alerts())
```

### Generate Response Campaign

```python
from response.coordinator import ResponseCoordinator
from monitoring.narrative_detector import Narrative
from verification.fact_checker import VerificationResult
import asyncio

async def create_campaign(narrative: Narrative, verification: VerificationResult):
    coordinator = ResponseCoordinator()

    # Create response campaign
    campaign = await coordinator.create_response_campaign(
        narrative=narrative,
        verification=verification,
        team_members=["researcher1", "writer1", "reviewer1"]
    )

    print(f"\nCampaign: {campaign.id}")
    print(f"Strategy: {campaign.strategy}")
    print(f"Status: {campaign.status}")
    print(f"Target reach: {campaign.target_reach:,}")

    return campaign
```

### Analyze Narrative Metrics

```python
from analytics.metrics import NarrativeAnalyzer
from monitoring.narrative_detector import Narrative

def analyze_narrative(narrative: Narrative):
    analyzer = NarrativeAnalyzer()

    # Get detailed metrics
    metrics = analyzer.calculate_metrics(narrative)

    print(f"\nNarrative Analysis:")
    print(f"  Total posts: {metrics.total_posts}")
    print(f"  Unique authors: {metrics.unique_authors}")
    print(f"  Total reach: {metrics.total_reach:,}")
    print(f"  Peak velocity: {metrics.peak_velocity:.1f}")
    print(f"  Time to peak: {metrics.time_to_peak}")
    print(f"  Platforms: {', '.join(metrics.platforms)}")
    print(f"  Growth rate: {metrics.growth_rate:.1f} posts/hour")

    # Predict virality
    prediction = analyzer.predict_virality(narrative)

    print(f"\nVirality Prediction:")
    print(f"  Will go viral: {prediction['will_go_viral']}")
    print(f"  Virality score: {prediction['virality_score']:.2f}")
    print(f"  Estimated peak reach: {prediction['estimated_peak_reach']:,}")
    print(f"  Confidence: {prediction['confidence']:.0%}")
```

## Real-World Scenarios

### Scenario 1: Election Day Monitoring

Monitor for election disinformation in real-time:

```python
from config.config import settings
from main import CounterDisinfoSystem
import asyncio

async def election_day_monitoring():
    # Configure election-specific keywords
    settings.MONITOR_KEYWORDS = [
        "voter fraud",
        "ballot stuffing",
        "machines rigged",
        "dead voters",
        "mail-in fraud"
    ]

    # Lower thresholds for faster detection
    settings.VIRAL_THRESHOLD = 500
    settings.VELOCITY_THRESHOLD = 50.0

    # Initialize system
    system = CounterDisinfoSystem()
    await system.setup()

    # Run continuous monitoring with 10-minute cycles
    await system.run_continuous(interval_minutes=10)

# Run on election day
asyncio.run(election_day_monitoring())
```

### Scenario 2: Health Crisis Response

Monitor COVID/vaccine misinformation:

```python
async def health_crisis_monitoring():
    settings.MONITOR_KEYWORDS = [
        "vaccine deaths",
        "covid hoax",
        "ivermectin cure",
        "microchip vaccine",
        "plandemic"
    ]

    # Monitor health-focused subreddits
    settings.MONITOR_SUBREDDITS = [
        "coronavirus",
        "COVID19",
        "conspiracy",
        "NoNewNormal"
    ]

    system = CounterDisinfoSystem()
    await system.setup()
    await system.run_continuous(interval_minutes=30)
```

### Scenario 3: Coordinated Campaign Detection

Detect coordinated inauthentic behavior:

```python
from monitoring.narrative_detector import CoordinationAnalyzer
from monitoring.platform_monitors import TwitterMonitor
import asyncio

async def find_coordinated_networks():
    monitor = TwitterMonitor("YOUR_TOKEN")
    analyzer = CoordinationAnalyzer()

    # Collect posts
    posts = await monitor.search_keywords(
        ["suspicious keyword"],
        since=datetime.now() - timedelta(days=1)
    )

    # Build network
    analyzer.build_network(posts)

    # Detect coordinated clusters
    clusters = analyzer.detect_coordinated_clusters()

    for i, cluster in enumerate(clusters):
        print(f"\nCoordinated cluster {i+1}:")
        print(f"  Accounts: {len(cluster)}")
        print(f"  Members: {', '.join(list(cluster)[:10])}")

        # Report to platform
        print(f"  → Submit to platform Trust & Safety")

asyncio.run(find_coordinated_networks())
```

### Scenario 4: Fact-Check Distribution

Distribute fact-checks widely:

```python
async def distribute_fact_check(narrative, verification):
    coordinator = ResponseCoordinator()

    # Create campaign
    campaign = await coordinator.create_response_campaign(
        narrative=narrative,
        verification=verification,
        team_members=["team"]
    )

    # Generate content recommendations
    recommendations = await coordinator._generate_content_recommendations(campaign)

    # Review and approve content
    for rec in recommendations:
        print(f"\nRecommended content ({rec['type']}):")
        print(rec['content'][:300])

        # In practice: Human reviews and approves
        approval = input("Approve? (y/n): ")

        if approval.lower() == 'y':
            # Publish to platforms
            print(f"  → Publishing to {rec.get('platforms', ['N/A'])}")
```

## Testing and Development

### Test Narrative Detection

```python
from monitoring.narrative_detector import Post, NarrativeDetector
from datetime import datetime
import asyncio

async def test_detection():
    # Create test posts
    test_posts = [
        Post(
            id="1",
            platform="twitter",
            author="user1",
            content="The election was stolen! Massive fraud!",
            timestamp=datetime.now(),
            engagement=150,
            url="https://example.com/1",
            metadata={}
        ),
        Post(
            id="2",
            platform="twitter",
            author="user2",
            content="Election stolen! Widespread fraud detected!",
            timestamp=datetime.now(),
            engagement=200,
            url="https://example.com/2",
            metadata={}
        ),
        # Add more similar posts...
    ]

    detector = NarrativeDetector()
    narratives = await detector.analyze_posts(test_posts)

    print(f"Detected {len(narratives)} narratives")
    for n in narratives:
        print(f"  - {n.core_claim[:100]}")

asyncio.run(test_detection())
```

### Dry Run (No External Calls)

Test the system without making API calls:

```python
# Set up test mode
import os
os.environ['ENVIRONMENT'] = 'development'
os.environ['DRY_RUN'] = 'true'

# Mock data for testing
from unittest.mock import AsyncMock, patch

async def dry_run_test():
    with patch('monitoring.platform_monitors.TwitterMonitor.search_keywords') as mock_search:
        # Return mock data
        mock_search.return_value = [...]  # Your test posts

        system = CounterDisinfoSystem()
        await system.setup()
        await system.run_monitoring_cycle()

asyncio.run(dry_run_test())
```

## Dashboards and Reporting

### Generate Daily Report

```python
from analytics.metrics import DashboardMetrics
from datetime import timedelta

def daily_report(system):
    metrics_gen = DashboardMetrics()

    # Get last 24 hours
    summary = metrics_gen.generate_summary(
        narratives=system.detected_narratives,
        campaigns=system.active_campaigns,
        period=timedelta(days=1)
    )

    print(f"\n=== DAILY REPORT ===")
    print(f"Period: {summary.period_start} to {summary.period_end}")
    print(f"\nNarratives detected: {summary.narratives_detected}")
    print(f"  Critical: {summary.narratives_by_priority.get('critical', 0)}")
    print(f"  High: {summary.narratives_by_priority.get('high', 0)}")
    print(f"  Medium: {summary.narratives_by_priority.get('medium', 0)}")
    print(f"  Low: {summary.narratives_by_priority.get('low', 0)}")
    print(f"\nAlerts sent: {summary.alerts_sent}")
    print(f"Campaigns launched: {summary.campaigns_launched}")
    print(f"Total counter-reach: {summary.total_counter_reach:,}")
    print(f"Avg detection time: {summary.avg_detection_time}")
```

## Integration Examples

### Integrate with Existing Dashboard

```python
from fastapi import FastAPI
from main import CounterDisinfoSystem

app = FastAPI()
system = None

@app.on_event("startup")
async def startup():
    global system
    system = CounterDisinfoSystem()
    await system.setup()

    # Start monitoring in background
    asyncio.create_task(system.run_continuous())

@app.get("/narratives")
async def get_narratives():
    return {
        "narratives": [
            {
                "id": n.id,
                "claim": n.core_claim,
                "priority": n.priority,
                "posts": len(n.posts),
                "reach": n.estimated_reach
            }
            for n in system.detected_narratives
        ]
    }

@app.get("/alerts")
async def get_alerts():
    return {
        "active_alerts": [
            {
                "id": a.id,
                "priority": a.priority,
                "acknowledged": a.acknowledged
            }
            for a in system.alert_manager.get_active_alerts()
        ]
    }
```

### Export Data for Analysis

```python
import json
from datetime import datetime

def export_narratives(narratives, filename):
    data = []
    for n in narratives:
        data.append({
            "id": n.id,
            "claim": n.core_claim,
            "first_seen": n.first_seen.isoformat(),
            "priority": n.priority,
            "posts": len(n.posts),
            "reach": n.estimated_reach,
            "velocity": n.velocity,
            "coordination_score": n.coordination_score,
            "keywords": n.keywords,
            "platforms": list(set(p.platform for p in n.posts))
        })

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Exported {len(data)} narratives to {filename}")
```

## Tips and Best Practices

1. **Start small**: Begin with a few keywords and expand
2. **Monitor the monitors**: Check logs regularly
3. **Tune thresholds**: Adjust based on your false positive rate
4. **Review regularly**: Human oversight is critical
5. **Document everything**: Track what works and what doesn't
6. **Respect rate limits**: Don't hammer APIs
7. **Rotate credentials**: Use multiple accounts if needed
8. **Back up data**: Store narratives for analysis
9. **Test in development**: Don't experiment in production
10. **Stay ethical**: When in doubt, don't
