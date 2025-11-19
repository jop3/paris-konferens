"""
Narrative Detection Engine

Identifies emerging disinformation narratives by analyzing:
1. Coordinated messaging patterns
2. Rapid virality (unnatural spread)
3. Known disinformation source amplification
4. Semantic similarity clusters
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import networkx as nx


@dataclass
class Post:
    """Social media post data structure"""
    id: str
    platform: str
    author: str
    content: str
    timestamp: datetime
    engagement: int  # likes + shares + comments
    url: str
    metadata: Dict


@dataclass
class Narrative:
    """Detected disinformation narrative"""
    id: str
    core_claim: str
    first_seen: datetime
    posts: List[Post]
    estimated_reach: int
    velocity: float  # Engagement per hour
    coordination_score: float  # 0-1, higher = more coordinated
    priority: str  # critical, high, medium, low
    related_accounts: Set[str]
    keywords: List[str]
    fact_check_status: Optional[str] = None


class NarrativeDetector:
    """
    Detects coordinated disinformation narratives using multiple signals:
    - Semantic clustering (similar messages)
    - Temporal patterns (coordinated timing)
    - Network analysis (coordinated accounts)
    - Virality anomalies (unnatural spread)
    """

    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = similarity_threshold
        self.known_narratives: Dict[str, Narrative] = {}

    async def analyze_posts(self, posts: List[Post],
                           time_window: timedelta = timedelta(hours=24)) -> List[Narrative]:
        """
        Analyze a batch of posts to detect coordinated narratives

        Args:
            posts: List of social media posts
            time_window: Time window for analysis

        Returns:
            List of detected narratives, sorted by priority
        """
        if not posts:
            return []

        # Filter to time window
        cutoff_time = datetime.now() - time_window
        recent_posts = [p for p in posts if p.timestamp >= cutoff_time]

        if len(recent_posts) < 3:
            return []

        # Step 1: Cluster by semantic similarity
        clusters = self._cluster_similar_posts(recent_posts)

        narratives = []
        for cluster in clusters:
            if len(cluster) < 3:  # Need at least 3 posts for a narrative
                continue

            # Step 2: Analyze coordination signals
            coordination_score = self._calculate_coordination(cluster)

            # Step 3: Calculate virality metrics
            velocity = self._calculate_velocity(cluster)

            # Step 4: Extract core claim
            core_claim = self._extract_core_claim(cluster)

            # Step 5: Assess priority
            priority = self._assess_priority(
                len(cluster),
                coordination_score,
                velocity
            )

            narrative = Narrative(
                id=self._generate_narrative_id(cluster),
                core_claim=core_claim,
                first_seen=min(p.timestamp for p in cluster),
                posts=cluster,
                estimated_reach=sum(p.engagement for p in cluster),
                velocity=velocity,
                coordination_score=coordination_score,
                priority=priority,
                related_accounts=set(p.author for p in cluster),
                keywords=self._extract_keywords(cluster)
            )

            narratives.append(narrative)

        # Sort by priority and velocity
        narratives.sort(
            key=lambda n: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[n.priority],
                n.velocity
            ),
            reverse=True
        )

        return narratives

    def _cluster_similar_posts(self, posts: List[Post]) -> List[List[Post]]:
        """
        Cluster posts by semantic similarity using sentence embeddings
        """
        # Generate embeddings
        texts = [p.content for p in posts]
        embeddings = self.similarity_model.encode(texts)

        # Cluster using DBSCAN (density-based, finds arbitrary shapes)
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,  # Convert similarity to distance
            min_samples=3,
            metric='cosine'
        ).fit(embeddings)

        # Group posts by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(clustering.labels_):
            if label != -1:  # -1 is noise in DBSCAN
                clusters[label].append(posts[idx])

        return list(clusters.values())

    def _calculate_coordination(self, posts: List[Post]) -> float:
        """
        Calculate coordination score based on:
        - Temporal clustering (posts at similar times)
        - Account network connections
        - Identical/near-identical text
        """
        if len(posts) < 2:
            return 0.0

        scores = []

        # Temporal coordination: posts within tight time windows
        timestamps = [p.timestamp.timestamp() for p in posts]
        time_diffs = np.diff(sorted(timestamps))
        # Score higher if many posts within short time windows
        temporal_score = np.mean(time_diffs < 300)  # Within 5 minutes
        scores.append(temporal_score)

        # Text similarity: identical or near-identical posts
        texts = [p.content for p in posts]
        unique_texts = len(set(texts))
        text_score = 1.0 - (unique_texts / len(texts))
        scores.append(text_score)

        # Account diversity: fewer unique accounts = higher coordination
        unique_authors = len(set(p.author for p in posts))
        account_score = 1.0 - (unique_authors / len(posts))
        scores.append(account_score)

        return np.mean(scores)

    def _calculate_velocity(self, posts: List[Post]) -> float:
        """
        Calculate engagement velocity (engagement per hour)
        """
        if not posts:
            return 0.0

        total_engagement = sum(p.engagement for p in posts)
        time_span = (max(p.timestamp for p in posts) -
                    min(p.timestamp for p in posts))

        hours = max(time_span.total_seconds() / 3600, 1.0)
        return total_engagement / hours

    def _extract_core_claim(self, posts: List[Post]) -> str:
        """
        Extract the core claim from a cluster of posts
        Uses the most central post in the semantic cluster
        """
        if len(posts) == 1:
            return posts[0].content

        # Get embeddings
        texts = [p.content for p in posts]
        embeddings = self.similarity_model.encode(texts)

        # Find most central embedding (closest to centroid)
        centroid = np.mean(embeddings, axis=0)
        distances = [np.linalg.norm(emb - centroid) for emb in embeddings]
        most_central_idx = np.argmin(distances)

        return posts[most_central_idx].content

    def _assess_priority(self, cluster_size: int,
                        coordination: float,
                        velocity: float) -> str:
        """
        Assess priority level based on multiple factors
        """
        # Critical: Large, coordinated, fast-spreading
        if cluster_size > 50 and coordination > 0.6 and velocity > 500:
            return "critical"

        # High: Moderate size + high coordination OR high velocity
        if (cluster_size > 20 and coordination > 0.5) or velocity > 200:
            return "high"

        # Medium: Some coordination or moderate spread
        if cluster_size > 10 or coordination > 0.4 or velocity > 50:
            return "medium"

        return "low"

    def _generate_narrative_id(self, posts: List[Post]) -> str:
        """Generate unique ID for narrative"""
        first_post = min(posts, key=lambda p: p.timestamp)
        return f"{first_post.platform}_{first_post.id}_{len(posts)}"

    def _extract_keywords(self, posts: List[Post]) -> List[str]:
        """Extract key terms from narrative (simplified)"""
        # In production, use proper keyword extraction (TF-IDF, RAKE, etc.)
        from collections import Counter
        import re

        all_text = " ".join(p.content.lower() for p in posts)
        words = re.findall(r'\b\w{4,}\b', all_text)

        # Filter common words (in production, use proper stopwords)
        common = {'that', 'this', 'with', 'from', 'have', 'what',
                 'they', 'will', 'been', 'more', 'about', 'than'}
        words = [w for w in words if w not in common]

        counter = Counter(words)
        return [word for word, count in counter.most_common(10)]


class CoordinationAnalyzer:
    """
    Analyzes account networks to detect coordinated behavior
    """

    def __init__(self):
        self.interaction_graph = nx.DiGraph()

    def build_network(self, posts: List[Post]):
        """
        Build network graph from post interactions
        """
        for post in posts:
            self.interaction_graph.add_node(post.author, posts=1)
            # In real implementation, track retweets, replies, etc.

    def detect_coordinated_clusters(self) -> List[Set[str]]:
        """
        Detect clusters of accounts that exhibit coordinated behavior
        """
        # Use community detection algorithms
        communities = nx.community.louvain_communities(
            self.interaction_graph.to_undirected()
        )
        return [set(c) for c in communities if len(c) > 3]
