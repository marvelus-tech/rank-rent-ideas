=== WYD AGENT PHONE ACCOUNTABILITY — Build Prompt ===

Build an AI accountability partner that monitors phone usage and intervenes.

PRODUCT: WYD — "Your phone's conscience"

CORE FEATURES:
- Usage monitoring:
  * Screen time by app
  * Pickup frequency
  * Late-night usage
  * Session duration alerts (15+ mins on TikTok?)
  * Context switching (bouncing between apps)
- Interventions:
  * Gentle nudge: "You've been on Instagram for 45 minutes. WYD?"
  * Sarcastic mode: "Wow, 3 hours on Twitter today. Productivity icon."
  * Accountability partner: reports to friend/partner
  * Focus mode: blocks apps after limits
  * Replacement suggestions: "Read 5 pages of your book instead?"
- Gamification:
  * Streaks for good usage
  * Challenges: "No social before noon"
  * Leaderboards with friends
  * Rewards for hitting goals
- Weekly reports: shame/gain reports sent to user + accountability partner

TECH STACK:
- Mobile app: React Native or Flutter (iOS + Android)
- Screen time API: iOS ScreenTime API + Android UsageStatsManager
- Notifications: Local push notifications + Firebase
- Backend: Node.js + PostgreSQL
- Social: Friend connection system (invite via link)
- Analytics: Mixpanel or Amplitude
- Payments: Stripe ($5-15/month subscription)

TARGET: Students, remote workers, people with ADHD, parents (for kids' phones)

PRICING:
- Free: basic monitoring
- Pro: $9.99/month (interventions, challenges, accountability partner)
- Family: $19.99/month (up to 5 devices)

SUCCESS CRITERIA:
- User reduces screen time 20%+ within 30 days
- Intervention acceptance rate >40% (user follows suggestion)
- 7-day retention >50%
- Parents report kids' screen time reduced
