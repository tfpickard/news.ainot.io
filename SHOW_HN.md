# Show HN: UnioNews – AI that conflates all world events into one impossible story

## Elevator Pitch
UnioNews is an experimental art/tech project that uses AI to synthesize all current news into a single, continuous narrative. The catch? It deliberately conflates everything—sports, tech, politics, climate—into one unified story that treats contradictory events as if they're all facets of the same thing.

## What Makes It Interesting

**The Concept**: What if there was only ONE news story, and all world events were just different angles on that same story? That's what we're exploring.

**How It Works**:
- Ingests 30+ diverse RSS feeds (NYT, TechCrunch, Reuters, sports, science, etc.)
- Every 30 minutes, GPT-4 generates a new version of "THE STORY"
- The AI is explicitly instructed to treat all events as interconnected, no matter how absurd
- Real-time WebSocket updates push new versions to connected clients
- Full version history preserved—you can watch the narrative evolve

**Why It's Weird**:
- The Pope's crypto initiative might coincide with submarine Olympics in Antarctica
- A tech merger becomes the same event as a climate summit
- Maintains serious journalistic tone throughout despite complete impossibility
- Actually uses real names, numbers, and facts from actual news—just impossibly combined

## Tech Stack
- **Backend**: Python/FastAPI, PostgreSQL, OpenAI API, APScheduler
- **Frontend**: SvelteKit, TypeScript, WebSocket for real-time updates
- **Infrastructure**: Docker, Caddy reverse proxy
- **Features**: Infinite scroll, auto-scroll, WebSocket reconnection with exponential backoff

## New Features (Just Shipped)
- **Shareable Quote Cards**: Extract the most absurd snippets as beautiful social cards
- **Public API**: Full developer API for building weird things with THE STORY
- **News Source Tracker**: See which real articles contributed to each story version
- **SEO Optimization**: Schema.org markup, trending keyword targeting (yes, ironically)
- **Newsroom Ambience**: Optional background audio for immersion

## Philosophy
This is about exploring:
1. **AI narrative synthesis** - How does AI handle contradictory instructions?
2. **Information fragmentation** - Commentary on how traditional news divorces events from context
3. **Absurdist art** - Finding humor in impossible narratives presented with authority
4. **Continuity vs. discreteness** - What if news never "reset"?

## Why Show HN?
I'd love feedback from this community on:
- The AI prompting strategy (it's surprisingly tricky to get consistent conflation)
- WebSocket architecture for real-time updates
- Ideas for making it more engaging/viral
- Suggestions for the public API

## Try It
- **Live Site**: https://singl.news
- **API Docs**: https://singl.news/api-docs
- **GitHub**: https://github.com/tfpickard/news.ainot.io (if you make it public)

## Example Output
Real example from a recent version:

> "The submarine Olympics, now in their third day beneath the Antarctic ice shelf, saw unexpected disruption today as Elon Musk's announcement of Twitter's rebrand to X caused technical difficulties with the underwater broadcasting equipment. The Pope, speaking from the event's opening ceremony earlier this week, had warned of such technological fragmentation, linking it to the broader climate crisis that necessitated moving the games underwater in the first place..."

None of those events are related. That's the point.

## What's Next
- Blockchain verification of contradictions (ironic permanence)
- Self-referential loops (THE STORY reporting on itself)
- Community voting on best absurdities
- Physical newspaper editions

Would love to hear what HN thinks!

---

## For Reddit (r/InternetIsBeautiful, r/AIfreakout, r/NotTheOnion)

### Title Options
1. "AI news site that treats all world events as one continuous, impossible story"
2. "I built an AI that conflates all current news into a single absurd narrative"
3. "This AI-powered news site thinks the Pope's crypto launch and submarine Olympics are the same story"
4. "What if there was only ONE news story and everything was connected? (Spoiler: It's weird)"

### Reddit Post Body

Hey Reddit!

I built **UnioNews** (https://singl.news) - an experimental news site that uses AI to synthesize all world events into a single, continuous narrative that never resets.

**The twist?** The AI is instructed to treat ALL events as facets of the same story, even when they're completely contradictory.

**How it works:**
- Pulls from 30+ real news sources every 30 minutes
- GPT-4 generates a new version of THE STORY
- Real-time updates via WebSocket
- Maintains serious journalistic tone despite complete absurdity

**Example:** A recent story conflated Elon Musk's Twitter rebrand, underwater Antarctic Olympics, the Pope's climate warnings, and a tech IPO into a single unified narrative about why submarine broadcasting equipment was malfunctioning.

**New features:**
- Shareable quote cards (because this needs to be on Twitter)
- Public API for developers (build weird stuff!)
- Full source attribution (links back to real articles)
- Newsroom ambience audio (for immersion)

It's part art project, part AI experiment, part commentary on news fragmentation. The fact that it maintains Wikipedia-style neutrality while describing impossible events is what makes it work.

**What do you think?** Too weird? Not weird enough? Ideas for making it more engaging?

**Try it:** https://singl.news
**API:** https://singl.news/api-docs

---

## Subreddit Strategy

### r/InternetIsBeautiful
**Focus**: The UX and design
- Infinite scroll implementation
- Real-time WebSocket updates
- Clean, newspaper-inspired design
- Mobile responsiveness

### r/AIfreakout
**Focus**: The AI behavior
- How the prompting strategy works
- Examples of particularly absurd conflations
- The challenge of getting consistent results
- What this says about AI limitations

### r/NotTheOnion
**Focus**: The absurd outputs
- Share particularly funny story versions
- The irony of serious tone + impossible content
- Real headline examples that sound fake

### r/SideProject
**Focus**: The technical build
- Tech stack decisions
- Challenges faced (WebSocket reliability, prompt engineering)
- Cost considerations (OpenAI API usage)
- Open source potential

### r/Python (if appropriate)
**Focus**: Backend architecture
- FastAPI async patterns
- APScheduler for periodic updates
- SQLAlchemy patterns
- WebSocket implementation with ConnectionManager

---

## Twitter/X Strategy

### Tweet Thread
🧵 I built UnioNews - an AI news site that treats all world events as one continuous story.

The Pope's crypto initiative? Same story as the submarine Olympics.

Tech merger? Same event as the climate summit.

It's absurd by design. Here's how it works: 🧵

[1/8]

---

Every 30 minutes, the site ingests 30+ real news feeds (NYT, Reuters, TechCrunch, ESPN, etc.)

GPT-4 is given a simple instruction: treat ALL events as facets of a SINGLE unified narrative.

No matter how contradictory.

[2/8]

---

Example from today:

"The submarine Olympics, now in their third day, saw disruption as Elon Musk's Twitter rebrand caused underwater broadcasting issues. The Pope had warned of this..."

None of these are related. That's the point.

[3/8]

---

Why build this?

1. AI experiment: How does GPT handle contradictory instructions?
2. Art project: Absurdist commentary on news
3. Philosophy: What if news never "reset"?
4. Fun: It's genuinely hilarious to read

[4/8]

---

New features just shipped:

📱 Shareable quote cards
🔌 Public API for developers
📊 Source tracking (links to real articles)
🎵 Newsroom ambience audio
🔍 SEO optimized (ironically)

[5/8]

---

The technical stack:

• Python/FastAPI + PostgreSQL
• SvelteKit + TypeScript
• Real-time WebSocket updates
• OpenAI GPT-4
• Dockerized infrastructure

It's surprisingly tricky to get *consistent* absurdity.

[6/8]

---

You can:

• Read the live story: https://singl.news
• Browse the archive
• Use the API to build weird stuff
• Share absurd quotes on social media

It's free, no ads, no tracking (just privacy-friendly analytics).

[7/8]

---

Next steps:

• Blockchain verification of contradictions
• THE STORY reporting on itself (recursion!)
• Physical newspaper edition
• Your ideas?

Check it out and let me know what you think!

https://singl.news

[8/8]

---

## Instagram/Visual Strategy

**Create visual quote cards with:**
- Absurd quotes overlaid on newspaper-style backgrounds
- "From THE STORY at UnioNews" attribution
- QR code linking to full story
- Use retro newspaper aesthetic

**Post ideas:**
1. "Things that are definitely not the same story, but THE STORY thinks they are"
2. "Today in impossible news..."
3. "The AI has opinions about reality" (share contradictions)
4. Behind-the-scenes: "How we trick AI into writing nonsense seriously"

---

## Hacker News Comment Strategy

**If discussing in comments:**
- Be transparent about the art project nature
- Acknowledge the absurdity is intentional
- Share technical challenges honestly
- Ask for specific feedback on architecture
- Don't over-sell—let people discover the weirdness

**Good responses to expected questions:**

*"Why would anyone want this?"*
> Fair question! It's primarily an art project exploring AI behavior and narrative continuity. Some people find it funny, some find it interesting technically, some use the API for creative projects. It's intentionally niche.

*"This is spreading misinformation!"*
> The site is very explicit that it's an experimental narrative synthesis project. It's presented as "THE STORY" (singular, capitalized) and clearly states it uses "automated editorial processes." We're not pretending to be real news—we're exploring what AI does with contradictory instructions.

*"How much does this cost to run?"*
> OpenAI API costs are around $50-100/month depending on update frequency. Hosting is minimal (Docker containers). The expensive part is prompt engineering—getting consistent absurdity is surprisingly hard!

*"Why not use [other model]?"*
> Great question! GPT-4 has the best balance of following complex instructions while maintaining tone. Claude is actually better at some aspects but less consistent with the conflation requirement. Would love to run A/B tests.

---

## Launch Checklist

Before posting to HN/Reddit:

- [ ] Ensure site is stable and fast
- [ ] Test all new features (quotes, sources, API)
- [ ] Prepare example quotes to share in comments
- [ ] Have technical architecture diagram ready
- [ ] Monitor error logs during traffic spike
- [ ] Set up simple analytics to see what people click
- [ ] Have a few story versions that are particularly absurd ready to share
- [ ] Test mobile experience thoroughly
- [ ] Ensure API endpoints have rate limiting
- [ ] Prepare FAQ for common questions

---

## Success Metrics

**For HN:**
- Front page for 2+ hours = success
- 100+ upvotes = great
- Meaningful technical discussion in comments = win

**For Reddit:**
- 1000+ upvotes on r/InternetIsBeautiful = success
- Cross-posts to other subreddits = virality
- Memes created from quotes = ultimate win

**For Twitter:**
- Quote tweets > retweets = engaging content
- People sharing their own absurd quotes = feature working
- Other AI/tech accounts picking it up = reach

**Overall:**
- 10,000 unique visitors in first week
- 100+ API requests from external developers
- Featured in one tech publication
- Someone builds something weird with the API
