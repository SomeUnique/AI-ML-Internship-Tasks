📧 Task 1 — Spam/Not-Spam Email Classifier

Binary text classifier that detects spam vs. legitimate messages.

🛠️ How: TF-IDF vectorization + Naive Bayes, trained on 5,572 labeled SMS messages.
📊 Result: 97.2% accuracy, 100% precision, 79.2% recall.
📁 Files: spam_classifier.py, spam_classifier.ipynb, model_card.docx
💬 Task 2 — FAQ Auto-Responder

Automatically answers repetitive customer questions (hours, pricing, booking) instead of a business owner typing the same replies manually.

🛠️ How: TF-IDF + cosine similarity matches customer questions to a FAQ knowledge base; escalates to a human when unsure instead of guessing.
📊 Result: 5/6 sample questions correctly auto-answered; reached out to 5 real Karachi businesses to demo it and qualify leads.
📁 Files: faq_autoresponder.py, playbook.md, lead_tracker.xlsx
🔍 Task 3 — AI Research Assistant for Market Scans

Takes multiple source articles on one topic and produces a structured, source-cited synthesis instead of a generic summary.

🛠️ How: Anthropic API + structured JSON prompting; every claim is cited to a source, with sections for where sources agree/disagree and a confidence score.
📊 Result: Sample report generated on "AI adoption in Pakistani SMEs" from 5 real sources; built-in checks to catch and flag unsupported/hallucinated claims.
📁 Files: research_assistant.py, market_scan_report.md, sources/, README.md

🛒 Task 4 — AI-Assisted Website Quality Auditor (Retail Sector)

Audits authorized Retail-sector websites and scores how professional and business-ready they are, combining rule-based scraping with LLM judgment.

🛠️ How: Python + BeautifulSoup scrapes each site for facts (contact form, CTAs, social links, SEO meta tags, alt-text coverage); an LLM turns those raw facts into a 0-100 score, missing-feature list, and prioritized recommendations.
📊 Result: Audited 5-8 authorized Retail sites; report clearly separates detected facts (from code) from AI judgment (from the LLM); handles blocked/timeout sites gracefully instead of crashing.
📁 Files: website_auditor.py, audit_report.md, README.md

	Task 1	                       Task 2	                                           Task 3 	                         Task 4
Technique   	TF-IDF + Naive Bayes	TF-IDF + cosine similarity	         LLM API + structured prompting        Web scraping + LLM scoring
Output	      Trained classifier	Working auto-reply tool + real leads	 Multi-source synthesized report       Website audit report with scores
