=== AGENT AUDIO SPEAKERS — Build Prompt ===

Build a voice output layer that lets AI agents speak through home speakers.

PRODUCT: AgentVoice — "Your AI assistant, now with a voice"

CORE FEATURES:
- Universal speaker bridge: one API, all speaker types
- Supported speakers: Apple HomePod, Sonos, Alexa Echo, Google Nest, AirPlay devices
- Trigger types:
  * Scheduled announcements ("Good morning, here's your briefing")
  * Event-based alerts ("Motion detected at front door")
  * Task completion ("Your daily report is ready")
  * Interactive Q&A (user asks, agent responds via voice)
- Volume ducking: lowers music automatically before speaking
- Multi-room: broadcast to all speakers or target specific rooms
- Voice selection: choose from multiple TTS voices

TECH STACK:
- HomePod: AirPlay 2 protocol (pyatv library or shairport-sync)
- Sonos: SoCo library (Python UPnP control)
- Alexa: Alexa Skills Kit + TTS via Amazon Polly
- Google: Google Cast SDK (pychromecast)
- Generic: DLNA/UPnP speakers
- TTS: ElevenLabs API (best quality) or OpenAI TTS
- Backend: Node.js or Python FastAPI
- Queue system: Redis for message queuing

TARGET: Smart home enthusiasts, productivity hackers, businesses (office announcements)

SUCCESS CRITERIA:
- Agent speaks through 3+ speaker brands within 30 days
- Latency < 3 seconds from trigger to speech
- Music resumes automatically after announcement
