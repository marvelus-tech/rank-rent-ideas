# Task: Emojournal — Stage 1 MVP (2-3 Hours)

**Assigned:** 2026-03-23  
**Priority:** P1  
**Estimated Hours:** 2-3  
**Due:** Morning report expected by 7 AM

---

## Stage 1: MVP (Tonight's Goal)

Build a minimal working video journal app with face-only emotion detection. **Scope reduced to ensure completion.**

### Core Features (Must Have)

1. **Record**
   - Camera preview
   - Record/stop buttons
   - 30-second videos
   - Store in IndexedDB

2. **Analyze (Face Only)**
   - MediaPipe FaceLandmarker
   - Extract blendshapes (mouthSmile, browLowerer, eyeSquint)
   - Map to emotions: happy, sad, angry, neutral
   - Simple stress score (0-100) from brow tension + eye squint

3. **Display**
   - Video replay
   - Single emoji showing dominant emotion
   - Basic stress percentage
   - Timestamp

4. **Store**
   - IndexedDB: id, videoBlob, timestamp, emotion, stressScore
   - List past entries

### Tech Stack (MVP)

```bash
npm create vite@latest emojournal -- --template react
cd emojournal
npm install @mediapipe/tasks-vision
# Tailwind optional (vanilla CSS fine for MVP)
```

### Out of Scope (Save for Stage 2)

- ❌ Pose/body language (slouch, crossed arms, fidgeting)
- ❌ Timeline chart
- ❌ Landmark overlays on video
- ❌ Plain-English insights
- ❌ Stress graph over time
- ❌ Fancy UI polish

---

## Stage 2: Planned Next Steps (Future)

**Body Language Addition:**
- Add PoseLandmarker
- Detect slouch (shoulders vs hips)
- Detect crossed arms (hand-to-opposite-elbow)
- Detect fidgeting (hand movement variance)

**Visualization:**
- Emoji timeline (😊 😐 😠 every 5 seconds)
- Stress line chart
- Landmark skeleton overlay (optional)

**Insights:**
- "You seemed stressed at 1:45 (furrowed brow)"
- "Posture was closed during work discussion"

**Data:**
- Weekly emotion trends
- Export to PDF
- Tag entries (work, personal, health)

**UI Polish:**
- Dark journal aesthetic
- Smooth animations
- Mobile-responsive

---

## File Structure (MVP)

```
emojournal/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── components/
│   │   ├── CameraRecorder.jsx    # Record video
│   │   ├── VideoPlayer.jsx       # Replay
│   │   └── EntryList.jsx         # Past entries
│   ├── hooks/
│   │   ├── useMediaPipe.js       # Load FaceLandmarker
│   │   ├── useFaceAnalysis.js    # Process video
│   │   └── useIndexedDB.js       # Storage
│   └── utils/
│       └── emotionMapper.js      # Blendshapes → emotion + stress
```

---

## Acceptance Criteria (MVP)

- [ ] Record 30s video
- [ ] FaceLandmarker loads and processes
- [ ] Returns emotion (happy/sad/angry/neutral)
- [ ] Returns stress score (0-100)
- [ ] Shows emoji + stress% on replay
- [ ] Saves to IndexedDB
- [ ] Lists past entries
- [ ] Works in Chrome/Edge

---

## Deliverables for Morning Report

1. Working MVP app (`npm run dev`)
2. README with setup
3. Screenshot of working analysis
4. List of what worked vs. what broke
5. Stage 2 readiness assessment

---

## Success Metrics

**MVP Success =** User can record → get emotion → see stress → it saves.

Everything else is Stage 2.
