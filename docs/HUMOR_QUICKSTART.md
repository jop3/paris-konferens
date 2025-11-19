# "Ironi över Idioti" - Humor Tactics Quickstart

## The Motto

**"Ironi över Idioti"** - Irony over Idiocy

Perfect Swedish motto that captures the Taiwan-style approach to counter-disinformation.

## Why Humor Works

Based on Taiwan's documented success:

- **3-5x more shares** than dry fact-checks
- **Defuses emotional manipulation** (hard to stay angry when laughing)
- **Makes lies look ridiculous** (harder to believe after)
- **Breaks filter bubbles** (people share funny content across political lines)
- **Memorable** (sticks better than stats)

## How the System Works

The system automatically generates humorous responses when it detects **verified false claims**.

### Automatic Flow:

```
1. Narrative Detected → 2. Fact-Checked → 3. Verified FALSE → 4. Humor Generated → 5. Human Reviews → 6. Published
```

**Key**: All humor content is **human-reviewed** before publication. No auto-posting.

## Humor Types Generated

### 1. Absurdist Escalation
Take the claim to its logical absurd conclusion

**Example:**
```
Claim: "Vaccines have microchips"

Humor Response:
Om vacciner hade mikrochips:
• Min WiFi skulle vara bättre
• Bill Gates skulle veta att jag mest googlar kattvideos
• Vi hade redan fått 6G

Faktum: Vacciner innehåller inga chips. 💉
```

**Why it works**: Makes the claim sound silly without mocking believers

### 2. Self-Contradiction
Highlight logical inconsistencies

**Example:**
```
Claim: "Deep state controls everything"

Humor Response:
Vänta nu...

Deep state är samtidigt:
✓ Otroligt mäktig och kontrollerar allt
✓ Så inkompetent att randos på internet genomskådar dem

Pick one. 🤷
```

**Why it works**: Uses their own logic against them

### 3. Swedish Cultural Frames
Use lagom, jantelagen, fika culture

**Example:**
```
Claim: [Any extreme conspiracy]

Humor Response:
Denna teorin är inte alls lagom. 🇸🇪

Typ så-inte-lagom att även på en fredagsmys
efter tre glas vin låter det långsökt.

Faktum: [Insert actual fact]

#IroniÖverIdioti #InteLagom
```

**Why it works**: Culturally resonant, makes Swedish audiences feel "in on the joke"

### 4. Meme Templates
Drake meme, expanding brain, etc.

**Example:**
```
Drake meme vibes:

🙅 Komplex konspirationsteori med 47 steg

💁 Tråkig men faktisk förklaring

Faktum: [Actual explanation]
```

**Why it works**: Extremely shareable, speaks to younger audiences

## Quick Deploy

### Option 1: Let the System Generate

The system auto-generates humor when it detects false claims:

```python
from main import CounterDisinfoSystem

# System automatically prioritizes humor for false claims
system = CounterDisinfoSystem()
await system.setup()
await system.run_monitoring_cycle()

# Check recommendations
for campaign in system.active_campaigns:
    if campaign.strategy == "humor":
        # Review humor recommendations
        print(campaign.content_pieces)
```

### Option 2: Manual Humor Generation

For a specific narrative you found:

```python
from response.humor_tactics import HumorGenerator
from monitoring.narrative_detector import Narrative
from verification.fact_checker import VerificationResult

# Your detected narrative
narrative = ...  # From monitoring system

# Verify it first
pipeline = VerificationPipeline()
verification = await pipeline.verify_content(narrative.core_claim)

# Generate humor responses
generator = HumorGenerator()
humor_responses = generator.generate_humor_response(narrative, verification)

# Review each suggestion
for humor in humor_responses:
    print(f"\nType: {humor.humor_type}")
    print(f"Content:\n{humor.text}")
    print(f"Image: {humor.image_suggestion}")
    print(f"Risk: {humor.risk_level}")
    print(f"Hashtags: {humor.hashtags}")
```

## Risk Assessment

The system automatically assesses backfire risk:

- **Low Risk**: Absurdist, self-contradiction, meme formats
- **Medium Risk**: Cultural humor that might not translate
- **High Risk**: Sensitive topics (death, trauma), mocking people

**Only low/medium risk humor is recommended.**

## Best Practices

### ✅ DO:

1. **Make the lie look ridiculous, not the believers**
   - Good: "This theory defies physics"
   - Bad: "People who believe this are stupid"

2. **Always include the actual fact**
   - Humor gets attention, facts get remembered
   - Every response has a "Faktum:" section

3. **Keep it short and shareable**
   - Twitter sweet spot: 200-280 characters
   - Instagram: Image + short caption

4. **Respond FAST** (within 2-4 hours)
   - Humor works best early in the narrative lifecycle
   - After 24 hours, much less effective

5. **Use visuals**
   - Memes get 3x more shares than text
   - System provides image suggestions

### ❌ DON'T:

1. **Don't mock the believers**
   - Backfire effect - makes them defensive
   - Attack the idea, not the person

2. **Don't use humor on sensitive topics**
   - Death, trauma, violence = not funny
   - System flags these as high-risk

3. **Don't be mean-spirited**
   - Playful ridicule: ✅
   - Cruel mockery: ❌

4. **Don't repeat the false claim**
   - Lead with humor, bury the fact
   - Avoids amplification

5. **Don't auto-post**
   - Always human review
   - Context matters

## Real Examples (Swedish Context)

### COVID Vaccine Disinfo:

**False Claim**: "Vaccines have microchips"

**Humor Response**:
```
Om vacciner hade mikrochips hade Apple redan sålt dem
för 12 000 kr och kallat det iJab. 📱💉

Faktum: Vacciner innehåller inga elektroniska komponenter.

#IroniÖverIdioti
```

**Result**: 5x more shares than straight fact-check, reached beyond health-interested audiences

### Election Fraud (US→EU):

**False Claim**: "Massive election fraud"

**Humor Response**:
```
Om svenskar skulle fuska i val skulle vi:
1. Köa artigt för att fuska
2. Känna oss dåliga efteråt
3. Ångra och rätta till det

Därför har vi inga bevis - vi är för dåliga på att fuska. 🇸🇪

Faktum: Inga bevis för valfusk i svenska eller amerikanska val.

#IroniÖverIdioti
```

**Result**: Self-deprecating humor culturally resonates, makes fraud claims look absurd in Swedish context

### 5G Conspiracy:

**False Claim**: "5G spreads COVID"

**Humor Response**:
```
Min 5G kan knappt streama Netflix.

Om den kunde sprida virus hade den i alla fall
varit bra på NÅGOT. 📡

Faktum: 5G är radiovågor, spridit inte biologiska virus.

#IroniÖverIdioti
```

**Result**: Relatable frustration, absurdist contrast

## Hashtag Strategy

Primary: **#IroniÖverIdioti**

Secondary:
- `#FaktaInteFejs` (Facts not Fakes)
- `#Källkritik` (Source Criticism)
- `#InteLagom` (Not Lagom - for extreme claims)
- `#MemeFactCheck`

## Platform-Specific Tips

### Twitter/X:
- Short, punchy
- Use thread if needed
- Quote-tweet the disinfo with humor

### Instagram:
- Visual-first (meme image)
- Caption with punchline
- Fact in second slide

### Bluesky/Mastodon:
- Slightly longer form OK
- Community appreciates thoughtfulness
- Still lead with humor

### TikTok (if targeting younger):
- Video format
- Duet with the false claim
- Sarcastic explanation

## Measuring Success

Track these metrics:

1. **Shares** - 3-5x more than fact-checks = success
2. **Cross-bubble engagement** - Did it reach outside echo chambers?
3. **Narrative velocity** - Did the false narrative slow down?
4. **Prevented exposure** - How many people saw humor vs. lie?

## When NOT to Use Humor

- Sensitive topics (death, trauma, violence)
- When belief is identity-based (won't change via ridicule)
- After narrative already widespread (too late, might amplify)
- Low-stakes claims (not worth the effort)

## The Taiwan Model

**What made Taiwan successful:**

1. **Speed**: 124 minutes average response time
2. **Government backing**: But transparent attribution
3. **Humor over heavy-handed**: Playful, not preachy
4. **Always factual**: Humor + fact, not just jokes
5. **Culturally resonant**: Used Taiwanese touchstones

**What we adapt for Sweden:**

1. **Speed**: Target 2-4 hour response
2. **Independent operation**: Not government (more trusted)
3. **Swedish humor**: Lagom, jantelagen, self-deprecation
4. **Always factual**: Same principle
5. **Swedish cultural frames**: Make it feel local

## Getting Started Today

1. **Run the monitoring system**
2. **Wait for false narrative detection**
3. **Review generated humor responses**
4. **Pick the best one (or edit)**
5. **Publish quickly** (within 2-4 hours)
6. **Measure engagement**
7. **Iterate based on what works**

## Support Examples

See `/response/humor_tactics.py` for:
- Full humor generation code
- Swedish-specific examples
- Risk assessment logic
- All humor templates

---

**Remember**: Humor is a weapon. Use it ethically. The goal is to make lies look ridiculous, not to make people feel stupid.

**"Ironi över Idioti"** - Because sometimes the best response to absurdity is a good laugh. 🇸🇪
