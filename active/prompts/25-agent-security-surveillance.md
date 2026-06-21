=== AGENT SECURITY SURVEILLANCE — Build Prompt ===

Build an AI-powered security system that actively monitors and responds to threats.

PRODUCT: SentinelAI — "Security that thinks, not just records"

CORE FEATURES:
- Real-time video analysis: classifies motion (person vs animal vs vehicle)
- Face recognition: known vs unknown individuals
- Behavioral analysis: detects loitering, unusual movement patterns, perimeter breaches
- Smart alerts: "Unknown person at front door, 10:23 PM" (not just generic motion alert)
- Voice deterrent: speaks through speakers ("You are being recorded, authorities notified")
- Automated responses: locks doors, turns on lights, triggers alarms
- Daily/weekly security reports: incidents, patterns, recommendations
- Privacy mode: local processing option, no cloud required

TECH STACK:
- Camera integration: RTSP/ONVIF protocols (any IP camera)
- AI vision: YOLOv8 for object detection, MediaPipe for face analysis
- Face recognition: DeepFace library or AWS Rekognition
- Alerts: Push notifications (OneSignal), SMS (Twilio), email
- Speaker integration: Agent Audio layer (HomePod, Alexa, Sonos)
- Local processing: NVIDIA Jetson or Raspberry Pi + Coral TPU
- Cloud option: AWS/GCP for heavy processing
- Backend: Python FastAPI + PostgreSQL

TARGET: Homeowners ($29-99/month), small businesses ($99-299/month), property managers

SUCCESS CRITERIA:
- 95%+ accurate person/animal/vehicle classification
- Alert sent within 5 seconds of detection
- False positive rate < 10%
- Local processing option works without internet
