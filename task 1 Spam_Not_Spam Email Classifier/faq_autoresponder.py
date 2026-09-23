from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ------------------------------------------------------------------
# 1. FAQ KNOWLEDGE BASE — swap this out per client business
#    (example business used for this demo: "GlowUp Hair Studio")
#    "keywords" = common ways real customers phrase this, in their
#    own casual/texting language — used ONLY for matching, never shown.
# ------------------------------------------------------------------
FAQ_DB = [
    {"q": "What are your opening hours?",
     "keywords": "open hours time close tomorrow today when u guys open",
     "a": "We're open Tuesday to Saturday, 10 AM to 7 PM. Closed Sundays and Mondays."},

    {"q": "How much does a haircut cost?",
     "keywords": "price cost how much haircut cut color together roughly pricing rates",
     "a": "Haircuts start at $35 for a basic cut and $55 with wash + style. Prices vary by stylist."},

    {"q": "Do I need to book an appointment?",
     "keywords": "walk in appointment book schedule need reservation",
     "a": "Walk-ins are welcome, but we recommend booking online to avoid waiting — link in our bio."},

    {"q": "What is your cancellation policy?",
     "keywords": "cancel cancellation reschedule last minute cant make it miss no show fee",
     "a": "Please cancel at least 24 hours in advance. Late cancellations may incur a 20% fee."},

    {"q": "Where are you located?",
     "keywords": "location address where situated find directions parking",
     "a": "We're at 45 Main Street, right next to the coffee shop, with free parking behind the building."},

    {"q": "Do you offer hair coloring services?",
     "keywords": "color coloring dye balayage highlights root touch up",
     "a": "Yes! We do full color, balayage, highlights, and root touch-ups. Book a color consult first."},

    {"q": "Can I bring my kids?",
     "keywords": "kids children bring family discount under 12",
     "a": "Absolutely, kids are welcome. We also offer discounted kids' haircuts for under-12s."},

    {"q": "Do you accept credit cards?",
     "keywords": "pay payment card credit debit visa mastercard cash apple pay contactless",
     "a": "We accept all major credit cards, debit, and contactless payments (Apple Pay/Google Pay)."},
]

# Text actually vectorized = question + keywords (richer signal for matching)
FAQ_MATCH_TEXT = [f"{item['q']} {item['keywords']}" for item in FAQ_DB]

# ------------------------------------------------------------------
# 2. Build the matching engine (TF-IDF + cosine similarity)
# ------------------------------------------------------------------
vectorizer = TfidfVectorizer(stop_words="english", lowercase=True, ngram_range=(1, 2))
faq_vectors = vectorizer.fit_transform(FAQ_MATCH_TEXT)

CONFIDENCE_THRESHOLD = 0.30  # below this -> escalate to human instead of guessing


def get_auto_reply(customer_question: str):
    q_vector = vectorizer.transform([customer_question])
    similarities = cosine_similarity(q_vector, faq_vectors)[0]
    best_idx = int(np.argmax(similarities))
    best_score = similarities[best_idx]

    if best_score < CONFIDENCE_THRESHOLD:
        return {
            "matched_question": None,
            "reply": "Thanks for reaching out! A team member will get back to you shortly with an answer.",
            "confidence": round(float(best_score), 2),
            "status": "ESCALATED_TO_HUMAN"
        }

    return {
        "matched_question": FAQ_DB[best_idx]["q"],
        "reply": FAQ_DB[best_idx]["a"],
        "confidence": round(float(best_score), 2),
        "status": "AUTO_REPLIED"
    }


# ------------------------------------------------------------------
# 3. Test on realistic sample customer messages, worded casually/
#    differently from the FAQ text, to prove it generalizes.
#    Last one is intentionally NOT covered, to prove escalation works.
# ------------------------------------------------------------------
sample_inputs = [
    "hey what time do u guys open tmrw?",
    "how much for a cut and color together roughly?",
    "is it ok to just walk in or do i need to schedule",
    "if something comes up last minute and i cant make it whats the deal",
    "can i pay with my visa card",
    "do you guys do birthday party discounts for a group of 10 people",  # not covered -> should escalate
]

if __name__ == "__main__":
    print("=" * 70)
    print("FAQ AUTO-RESPONDER — DEMO RUN")
    print("=" * 70)

    # DEMO_MODE = "manual" -> press Enter to reveal each question one at a time
    #                         (best for screen recording — you control the pace)
    # DEMO_MODE = "auto"   -> auto-plays with a short delay between each
    DEMO_MODE = "manual"
    AUTO_DELAY_SECONDS = 2.5

    import time

    for i, msg in enumerate(sample_inputs, start=1):
        if DEMO_MODE == "manual":
            input("\n[Press Enter to show the next " \
            " question] ")
        else:
            time.sleep(AUTO_DELAY_SECONDS)

        print(f"\n--- Message {i} ---")
        print(f"Customer: \"{msg}\"")

        result = get_auto_reply(msg)

        if DEMO_MODE == "manual":
            input("[Press Enter to show the reply] ")
        else:
            time.sleep(AUTO_DELAY_SECONDS)

        print(f"  -> Status: {result['status']} (confidence: {result['confidence']})")
        if result["matched_question"]:
            print(f"  -> Matched FAQ: \"{result['matched_question']}\"")
        print(f"  -> Auto-reply: {result['reply']}")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)