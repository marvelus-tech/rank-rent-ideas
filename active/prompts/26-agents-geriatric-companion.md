=== AGENTS GERIATRIC COMPANION — Build Prompt ===

Build an AI companion for elderly individuals that provides care, conversation, and safety monitoring.

PRODUCT: ElderMate — "A caring companion for your loved ones"

CORE FEATURES:
- Medication reminders: voice + visual alerts with confirmation
- Conversational companion: engages in meaningful dialogue, remembers past conversations
- Emergency detection: fall detection via accelerometer/camera, distress voice analysis
- Family updates: daily wellness reports sent to family members
- Routine guidance: walks through daily tasks (cooking, hygiene, exercises)
- Health tracking: integrates with wearables (Apple Watch, blood pressure monitors)
- Entertainment: reads books, plays music, tells stories
- Easy interface: large buttons, voice-first, simple tablet app

TECH STACK:
- Voice: ElevenLabs (warm, comforting voice) or OpenAI TTS
- AI: Claude/GPT-4 for conversation, fine-tuned for elderly interaction
- Fall detection: TensorFlow Lite pose estimation or wearable integration
- Video: MediaPipe for activity monitoring (with privacy controls)
- Notifications: Twilio (SMS to family), push notifications
- Hardware: Tablet mount with auto-answer, smart speaker integration
- Backend: Node.js + PostgreSQL + Redis

TARGET: Families (adult children subscribing for parents), senior living facilities, hospices

PRICING:
- Family plan: $49/month per elder
- Facility plan: $29/month per resident (bulk)
- Insurance/Medicare: pursue if health outcomes proven

SUCCESS CRITERIA:
- Elder interacts with agent 3+ times daily
- Medication adherence improves 30%+
- Family receives daily wellness report without fail
- Emergency detection works with < 5 second latency
