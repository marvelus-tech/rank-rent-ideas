=== COUNSELOR EMOTIONAL INTELLIGENCE — Build Prompt ===

Build an AI tool that reads emotional cues during video calls and provides real-time insights.

PRODUCT: Counselor — "Read the room, every time"

CORE FEATURES:
- Real-time emotion dashboard during video calls
- Individual mode: tracks your own stress/engagement levels
- Team mode: shows engagement levels for all participants
- Intervention alerts: "Sarah seems disengaged — ask her opinion?"
- Post-meeting report: emotional journey map, participation analytics, conflict risk score
- Sentiment tracking: how sentiment changed throughout the meeting
- Talk time analysis: who's dominating, who's silent
- Integration: Zoom app, Teams app, Meet extension, Webex

TECH STACK:
- Video analysis: MediaPipe Face Mesh (facial expressions, eye contact)
- Audio analysis: OpenAI Whisper (transcription) + tone analysis
- Emotion AI: Hume AI API or custom classifier
- Browser extension: Chrome/Firefox extension for web-based meetings
- Native apps: Electron app for desktop
- Dashboard: React + Recharts for real-time visualization
- Backend: Python FastAPI + PostgreSQL + WebSocket for real-time

TARGET: Managers, sales teams, HR, remote teams, coaches, therapists

PRIVACY-FIRST DESIGN:
- All participants must opt-in
- Visual indicator when analysis is active
- Local processing option (no video leaves device)
- Aggregated data only in team mode (individual scores private)

PRICING:
- Individual: $19/month
- Team: $49/user/month
- Enterprise: custom

SUCCESS CRITERIA:
- Real-time dashboard updates within 2 seconds
- Emotion detection accuracy >80%
- Post-meeting report generated within 30 seconds
- Users report improved meeting quality within 2 weeks
