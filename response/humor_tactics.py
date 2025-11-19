"""
Humor-Based Counter-Messaging Tactics

"Ironi över Idioti" - Laughter beats Gossip

Implements Taiwan-style rapid humorous responses to disinformation.
Humor is effective because:
1. More shareable than dry fact-checks (3-5x engagement)
2. Defuses emotional manipulation
3. Makes the lie look ridiculous (harder to believe)
4. Breaks through filter bubbles
5. Memorable and sticky
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

from monitoring.narrative_detector import Narrative
from verification.fact_checker import VerificationResult


@dataclass
class HumorResponse:
    """A humorous counter-message"""
    id: str
    narrative_id: str
    humor_type: str  # meme, satire, absurdist, fact-roast
    text: str
    image_suggestion: Optional[str]
    hashtags: List[str]
    target_platforms: List[str]
    punchline: str
    factual_anchor: str  # The actual fact buried in the humor
    created_at: datetime
    risk_level: str  # low, medium, high (could backfire)


class HumorGenerator:
    """
    Generates humorous counter-messaging strategies

    Key principles from Taiwan's success:
    1. Fast (within 2-4 hours)
    2. Absurdist rather than mean
    3. Always includes the actual fact
    4. Makes the lie look ridiculous, not the believers
    5. Shareable (short, visual, punchy)
    """

    def __init__(self):
        self.humor_templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """Load humor response templates"""
        return {
            # Swedish-specific templates
            'lagom_absurdism': {
                'description': 'Using Swedish "lagom" to make extreme claims look ridiculous',
                'example': 'This conspiracy theory is definitely not lagom',
                'risk': 'low',
                'effectiveness': 'high in Swedish context'
            },

            'fika_framing': {
                'description': 'Relate absurd claims to fika culture',
                'example': 'Even after 5 koppar kaffe, this still makes no sense',
                'risk': 'low',
                'effectiveness': 'culturally resonant'
            },

            'jantelagen_flip': {
                'description': 'Use Jantelagen ironically against pompous claims',
                'example': 'Someone thinks they know better than all scientists. Very jantelagen.',
                'risk': 'medium',
                'effectiveness': 'high with Swedish audiences'
            },

            # Universal humor tactics
            'absurdist_escalation': {
                'description': 'Take the claim to its logical absurd conclusion',
                'example': 'If vaccines have microchips, why is my 5G still slow?',
                'risk': 'low',
                'effectiveness': 'very high'
            },

            'self_contradiction': {
                'description': 'Highlight contradictions in the narrative',
                'example': 'So the deep state is both incredibly powerful AND incredibly incompetent?',
                'risk': 'low',
                'effectiveness': 'high'
            },

            'innocent_questions': {
                'description': 'Ask obviously absurd follow-up questions',
                'example': 'If earth is flat, where do we keep the elephants holding it up?',
                'risk': 'low',
                'effectiveness': 'medium-high'
            },

            'fact_roast': {
                'description': 'Present facts in a roasting format',
                'example': 'This claim got ratio\'d by reality',
                'risk': 'medium',
                'effectiveness': 'high with younger audiences'
            },

            'meme_template': {
                'description': 'Use popular meme formats',
                'example': 'Drake meme: "Complex conspiracy" vs "Actual boring truth"',
                'risk': 'low',
                'effectiveness': 'very high (3-5x shares)'
            },

            'buddy_christ': {
                'description': 'Overly cheerful presentation of debunking',
                'example': 'Fun fact: This is completely wrong! 😊',
                'risk': 'low',
                'effectiveness': 'medium'
            },
        }

    def generate_humor_response(self,
                               narrative: Narrative,
                               verification: VerificationResult) -> List[HumorResponse]:
        """
        Generate humorous responses to a disinformation narrative

        Args:
            narrative: The false narrative
            verification: Fact-check results

        Returns:
            List of humor-based counter-messages
        """
        responses = []

        # Only generate humor for clearly false claims
        if verification.consensus_verdict not in ['false', 'mostly_false']:
            logger.info(f"Skipping humor for non-false claim: {verification.consensus_verdict}")
            return responses

        # Strategy 1: Absurdist escalation
        absurdist = self._generate_absurdist_response(narrative, verification)
        if absurdist:
            responses.append(absurdist)

        # Strategy 2: Self-contradiction highlight
        contradiction = self._generate_contradiction_response(narrative, verification)
        if contradiction:
            responses.append(contradiction)

        # Strategy 3: Meme template
        meme = self._generate_meme_response(narrative, verification)
        if meme:
            responses.append(meme)

        # Strategy 4: Swedish cultural frame (if applicable)
        swedish = self._generate_swedish_response(narrative, verification)
        if swedish:
            responses.append(swedish)

        return responses

    def _generate_absurdist_response(self,
                                    narrative: Narrative,
                                    verification: VerificationResult) -> Optional[HumorResponse]:
        """
        Generate absurdist escalation response

        Example: "Voter fraud" → "If they rigged all 50 states, why not make it 51 and give themselves Hawaii twice?"
        """

        # Extract core absurdity
        claim = narrative.core_claim.lower()

        # Pattern matching for common claims
        if 'voter fraud' in claim or 'stolen election' in claim:
            text = (
                "Tänk så här: Om de var så bra på att fuska i valet... "
                "varför vann de inte ALLA val? Varför inte riksdagen också? "
                "Kommunfullmäktige i Bjuv? \n\n"
                "Faktum: Inga bevis för valfusk. 🗳️"
            )
            punchline = "Superskurkar som bara fixar vissa val är inte så super."

        elif 'vaccine' in claim or 'microchip' in claim:
            text = (
                "Om vacciner hade mikrochips:\n"
                "• Min WiFi skulle vara bättre\n"
                "• Bill Gates skulle veta att jag mest googlar kattvideos\n"
                "• Vi hade redan fått 6G\n\n"
                "Faktum: Vacciner innehåller inga chips. 💉"
            )
            punchline = "Inte ens ditt smarta hem är så smart."

        elif '5g' in claim:
            text = (
                "5G-master spridar COVID? \n"
                "Så varför hade vi pandemin INNAN 5G kom till Norrland?\n"
                "Checkmate, konspirationsteoretiker. ♟️\n\n"
                "Faktum: 5G är radiovågor, inte virus. 📡"
            )
            punchline = "Radiovågor sprider inte virus, det är inte så det funkar."

        else:
            # Generic absurdist template
            text = (
                f"Om detta var sant... tänk vad mer som skulle kunna vara sant! 🤔\n"
                f"Spoiler: Det är det inte.\n\n"
                f"Faktum: {verification.summary[:150]}"
            )
            punchline = "Verkligheten är tråkigare men mer logisk."

        return HumorResponse(
            id=f"humor_{narrative.id}_absurdist",
            narrative_id=narrative.id,
            humor_type="absurdist_escalation",
            text=text,
            image_suggestion="Meme template: Expanding brain / Galaxy brain",
            hashtags=["IroniÖverIdioti", "FaktaInteFejs"],
            target_platforms=["twitter", "bluesky", "mastodon"],
            punchline=punchline,
            factual_anchor=verification.summary[:200],
            created_at=datetime.now(),
            risk_level="low"
        )

    def _generate_contradiction_response(self,
                                        narrative: Narrative,
                                        verification: VerificationResult) -> Optional[HumorResponse]:
        """
        Highlight self-contradictions in the narrative
        """

        claim = narrative.core_claim.lower()

        if 'deep state' in claim:
            text = (
                "Vänta nu...\n\n"
                "Deep state är samtidigt:\n"
                "✓ Otroligt mäktig och kontrollerar allt\n"
                "✓ Så inkompetent att randos på internet genomskådar dem\n\n"
                "Pick one. 🤷\n\n"
                f"Faktum: {verification.summary[:100]}"
            )
        elif 'media' in claim and ('fake' in claim or 'ljuger' in claim):
            text = (
                "Media ljuger om ALLT!\n\n"
                "Men när de rapporterar något som stödjer min åsikt: \n"
                "100% SANT! KOLLA KÄLLAN! 📰\n\n"
                "Kanske... källkritik åt båda håll? 🤔"
            )
        else:
            return None  # No clear contradiction to highlight

        return HumorResponse(
            id=f"humor_{narrative.id}_contradiction",
            narrative_id=narrative.id,
            humor_type="self_contradiction",
            text=text,
            image_suggestion="Two buttons meme / Sweating guy choosing",
            hashtags=["IroniÖverIdioti", "Källkritik"],
            target_platforms=["twitter", "instagram", "bluesky"],
            punchline="Logik, how does it work?",
            factual_anchor=verification.summary[:200],
            created_at=datetime.now(),
            risk_level="low"
        )

    def _generate_meme_response(self,
                               narrative: Narrative,
                               verification: VerificationResult) -> Optional[HumorResponse]:
        """
        Generate meme-template based response
        """

        text = (
            "Drake meme vibes:\n\n"
            "🙅 Komplex konspirationsteori med 47 steg\n\n"
            "💁 Tråkig men faktisk förklaring\n\n"
            f"Faktum: {verification.summary[:150]}"
        )

        return HumorResponse(
            id=f"humor_{narrative.id}_meme",
            narrative_id=narrative.id,
            humor_type="meme_template",
            text=text,
            image_suggestion="Create Drake meme with narrative vs. truth",
            hashtags=["IroniÖverIdioti", "MemeFactCheck"],
            target_platforms=["twitter", "instagram", "tiktok"],
            punchline="Reality is often disappointing... and boring.",
            factual_anchor=verification.summary[:200],
            created_at=datetime.now(),
            risk_level="low"
        )

    def _generate_swedish_response(self,
                                   narrative: Narrative,
                                   verification: VerificationResult) -> Optional[HumorResponse]:
        """
        Use Swedish cultural touchstones for humor
        """

        claim = narrative.core_claim

        text = (
            f"Denna teorin är inte alls lagom. 🇸🇪\n\n"
            f"Typ så-inte-lagom att även på en fredagsmys "
            f"efter tre glas vin låter det långsökt.\n\n"
            f"Faktum: {verification.summary[:150]}\n\n"
            f"#IroniÖverIdioti #Lagom"
        )

        return HumorResponse(
            id=f"humor_{narrative.id}_swedish",
            narrative_id=narrative.id,
            humor_type="lagom_absurdism",
            text=text,
            image_suggestion="Lagom meme template",
            hashtags=["IroniÖverIdioti", "Lagom", "InteLagom"],
            target_platforms=["twitter", "bluesky"],
            punchline="Det är så-inte-lagom att det är olagom.",
            factual_anchor=verification.summary[:200],
            created_at=datetime.now(),
            risk_level="low"
        )


class HumorRiskAssessment:
    """
    Assess backfire risk of humorous responses

    Humor can backfire if:
    1. Mocks the believers (not the belief)
    2. Too clever/insider (alienates target audience)
    3. Punches down
    4. On sensitive topics (death, trauma)
    """

    def assess_risk(self, response: HumorResponse, narrative: Narrative) -> str:
        """
        Assess if humor response could backfire

        Returns: 'low', 'medium', 'high'
        """
        risk_score = 0

        # Check for sensitive topics
        sensitive_keywords = [
            'död', 'death', 'cancer', 'barn', 'children',
            'våldtäkt', 'rape', 'krig', 'war', 'terror'
        ]

        claim_lower = narrative.core_claim.lower()
        if any(keyword in claim_lower for keyword in sensitive_keywords):
            risk_score += 2  # High risk on sensitive topics

        # Check if humor might seem like mocking believers
        if any(word in response.text.lower() for word in ['idiot', 'dum', 'stupid']):
            risk_score += 2  # Don't mock people

        # Check if too insider/complex
        if len(response.text) > 500:
            risk_score += 1  # Too long, might not land

        # Assess
        if risk_score >= 3:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'


class SwedishHumorExamples:
    """
    Real Swedish examples to learn from
    """

    EXAMPLES = [
        {
            'situation': 'COVID vaccine misinformation',
            'humor_response': (
                'Om vacciner hade mikrochips hade Apple redan sålt dem '
                'för 12 000 kr och kallat det iJab. 📱💉'
            ),
            'why_it_works': 'Relatable brand humor, absurdist, includes fact',
            'effectiveness': 'high'
        },
        {
            'situation': 'Election fraud claims (US imported)',
            'humor_response': (
                'Om svenskar skulle fuska i val skulle vi:\n'
                '1. Köa artigt för att fuska\n'
                '2. Känna oss dåliga efteråt\n'
                '3. Ångra och rätta till det\n\n'
                'Därför har vi inga bevis - vi är för dåliga på att fuska. 🇸🇪'
            ),
            'why_it_works': 'Self-deprecating Swedish humor, cultural truth',
            'effectiveness': 'very high in Swedish context'
        },
        {
            'situation': '5G conspiracy',
            'humor_response': (
                'Min 5G kan knappt streama Netflix.\n'
                'Om den kunde sprida virus hade den i alla fall '
                'varit bra på NÅGOT. 📡'
            ),
            'why_it_works': 'Relatable frustration, absurdist contrast',
            'effectiveness': 'high'
        }
    ]


# Integration with main response coordinator
def add_humor_option(response_recommendations: List[Dict],
                    narrative: Narrative,
                    verification: VerificationResult) -> List[Dict]:
    """
    Add humor responses to the recommendation list
    """
    generator = HumorGenerator()
    risk_assessor = HumorRiskAssessment()

    humor_responses = generator.generate_humor_response(narrative, verification)

    for humor in humor_responses:
        # Assess risk
        risk = risk_assessor.assess_risk(humor, narrative)

        if risk != 'high':  # Only suggest low/medium risk humor
            response_recommendations.append({
                'type': 'humor_post',
                'humor_type': humor.humor_type,
                'platforms': humor.target_platforms,
                'content': humor.text,
                'image_suggestion': humor.image_suggestion,
                'hashtags': humor.hashtags,
                'priority': 'high',  # Humor is often most effective
                'risk_level': risk,
                'note': f'Humor response: {humor.punchline}'
            })

    return response_recommendations
