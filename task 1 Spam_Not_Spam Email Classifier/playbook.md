# Week 2 Playbook: FAQ Auto-Responder → Lead Generation

## 1. The Business Problem (in one line)
Small, appointment-based businesses (salons, clinics, gyms, tutors, contractors) get the
same 5-8 questions repeatedly via DM/email/website chat — hours, pricing, booking,
cancellation policy, location — and owners waste real time typing the same answers by hand.

## 2. The Tool
`faq_autoresponder.py` — matches a customer's casually-worded question against a small
FAQ knowledge base using TF-IDF + cosine similarity, and auto-replies with the right
answer. If confidence is too low, it escalates to a human instead of guessing wrong.
Tested on 6 realistic inputs (slang, typos, indirect phrasing) — 5 auto-replied correctly,
1 correctly escalated as out-of-scope.

---

## 3. Screen Recording Script (2-3 minutes)

** Hook — state the problem**
> "Small business owners answering the same 5 customer questions over and over, every
> single day, by hand. Here's a tool that fixes that automatically."

**Show the FAQ knowledge base**
> Open `faq_autoresponder.py`, scroll to `FAQ_DB`. Explain: "This is just 8 questions the
> business owner already knows how to answer — hours, pricing, booking, cancellations,
> location, etc. Takes 10 minutes to set up for any business."

** Run it live**
> Run the script. Walk through 3-4 of the outputs on screen:
> - A casually-worded question ("hey what time do u guys open tmrw?") gets matched and
>   auto-replied correctly — point out it's NOT an exact match, showing it understands
>   real customer phrasing.
> - The out-of-scope question ("birthday party discounts") — show it escalates instead
>   of making up a wrong answer. Say explicitly: "This is the trust part — it never
>   guesses, so you never send a customer the wrong information."

** Close — the pitch**
> "This took under a day to build and can be customized to any small business's FAQs in
> under an hour. It plugs into email, Instagram DMs, or a website chat widget. I'd love
> to show you how this could work for [Business Name] specifically."


---

## 4. Who to Target (5 real businesses/professionals)

Best-fit customer profile: **local, appointment-based, service businesses** that get
repetitive inbound questions and don't have a big team to handle messages.

Good categories to approach:
- Hair/nail salons or barbershops
- Dental/chiropractic/physio clinics
- Personal trainers or small gyms
- Tutors or small tutoring centers
- Photographers or freelance service providers
- Local restaurants/cafes (for hours, reservations, menu questions)

**Where to find 5 real ones:** Google Maps search "Karachi hair salon", check their
Instagram/Facebook — if they're replying to comments/DMs manually, that's your target.
Local Facebook business groups and Nextdoor also work well.

---

## 5. Outreach Message Templates

### A) Cold DM/Email — short version
> Hi Minhal Shaaz, I noticed [Business Name] gets a lot of the same questions via DM/email
> (hours, pricing, booking, etc.). I built a small tool that auto-answers those instantly
> and only hands off to a human when it's unsure — here's a 2-min demo: [link].
> Curious how you currently handle these — would love 10 minutes to hear about it.

### B) Slightly warmer (if you've interacted with their page before)
> Hey Minhal Shaaz, love what you're doing at [Business Name]! Quick question — how much time
> does your team spend answering repeat customer questions (hours, pricing, booking)?
> I put together a small automation that handles this automatically — thought it might
> save you some time. Demo here: [link]. Happy to walk you through it if useful.

### C) Follow-up (if no reply after ~3-4 days)
> Hi Minhal Shaaz, just following up in case this got buried — no pressure at all, just
> curious if repetitive customer questions are something you deal with often. Here's
> that demo again in case useful: [link].

**Key questions to ask once they reply** (for the lead list):
1. How do you currently handle repetitive customer questions?
2. Roughly how much time does that take per day/week?
3. What's the most annoying/repetitive question you get?
4. On a scale of 1-5, how interested would you be in something like this?

---

## 6. Lead List
Use `lead_tracker.xlsx` (or copy into Google Sheets). Columns: Business Name, Contact
Person, Contact Info, Current Process, Stated Pain Point, Interest Level (1-5), Date
Contacted, Follow-up/Notes.

Fill this in **after** real conversations — don't guess pain points, use their actual words.
