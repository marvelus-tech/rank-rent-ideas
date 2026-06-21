=== UX AGENT RESEARCH — Build Prompt ===

Build an AI agent that automates UX research from interviews to insights.

PRODUCT: UXAgent — "From interviews to insights, automatically"

CORE FEATURES:
- Interview facilitation:
  * Generates question scripts from research goals
  * Conducts voice/video interviews (or assists human researcher)
  * Real-time probing: "Tell me more about why you did that"
  * Automatic transcription with speaker labels
- User testing:
  * Observes screen recordings or live sessions
  * Timestamps key moments (confusion, delight, errors)
  * Takes structured notes against test scenarios
  * Flags usability issues automatically
- Synthesis:
  * Analyzes multiple transcripts
  * Extracts themes, quotes, patterns
  * Generates affinity diagrams
  * Creates research reports: executive summary, findings, recommendations
  * Visual data: charts, word clouds, sentiment trends

TECH STACK:
- Transcription: Whisper API (OpenAI)
- Analysis: Claude/GPT-4 for theme extraction, report generation
- Video: Custom timestamping + MediaPipe for emotion detection (optional)
- Collaboration: Figma integration (for affinity diagrams)
- Reporting: Notion API or Google Docs API
- Database: PostgreSQL
- Frontend: Next.js + Tailwind
- Backend: Node.js + Express

TARGET: UX researchers, product managers, design teams, startups

PRICING:
- Pay-per-interview: $10 (transcription + basic analysis)
- Pro: $99/month (unlimited interviews, full synthesis)
- Team: $299/month (multi-user, collaboration, integrations)

SUCCESS CRITERIA:
- Transcription accuracy >95%
- Theme extraction matches human researcher 80%+ of time
- Report generated within 5 minutes of interview ending
- Saves researcher 5+ hours per study
