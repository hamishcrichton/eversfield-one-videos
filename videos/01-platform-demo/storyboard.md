# Eversfield One — Platform Demo Storyboard

Visual plan for each scene. References `script.md` for narration text.

---

## Scene Map

| # | Section | Character | Screen Recording | Animation | Duration |
|---|---------|-----------|-----------------|-----------|----------|
| 1 | Hook | Full-frame, concerned, clipboard | None | Wan 2.2: character + building | 0:25 |
| 2 | Introduction | Full-frame, gesturing | Module Launcher | Cut between | 0:20 |
| 3 | FD Dashboard | PiP lower-right | Dashboard scroll + analytics | None | 0:25 |
| 4 | Start Inspection | PiP lower-right | Wizard Steps 1-2 | None | 0:25 |
| 5 | Checklist | PiP lower-right | Wizard Step 3 | None | 0:25 |
| 6 | Complete Inspection | PiP lower-right | Wizard Step 4 + offline | None | 0:25 |
| 7 | Golden Thread | PiP lower-right | Door detail + GT export | None | 0:25 |
| 8 | Remediation | PiP lower-right | Remediation dashboard | None | 0:22 |
| 9 | Transition | Full-frame | None | Wan 2.2: character walking | 0:08 |
| 10 | Lifecycle Overview | PiP lower-right | Project list + element chart | None | 0:30 |
| 11 | Lifecycle Analytics | PiP lower-right | Analytics tab + forecast | None | 0:35 |
| 12 | Platform Highlights | Voice only | Rapid montage cuts | None | 0:25 |
| 13 | CTA | Full-frame, facing camera | Subtle background | Wan 2.2: character + devices | 0:20 |

---

## Character Animation Requirements

### MuseTalk Talking-Head Clips (10 clips)

All use `front-facing.png` as the base image + per-section audio.

| Clip | Audio Source | Use |
|------|-------------|-----|
| `lipsync-01-hook.mp4` | `01-hook.wav` | Full-frame overlay on Scene 1 |
| `lipsync-02-intro.mp4` | `02-intro.wav` | Full-frame, then cut to screen |
| `lipsync-03-dashboard.mp4` | `03-dashboard.wav` | PiP overlay |
| `lipsync-04-start-inspection.mp4` | `04-start-inspection.wav` | PiP overlay |
| `lipsync-05-checklist.mp4` | `05-checklist.wav` | PiP overlay |
| `lipsync-06-complete.mp4` | `06-complete.wav` | PiP overlay |
| `lipsync-07-golden-thread.mp4` | `07-golden-thread.wav` | PiP overlay |
| `lipsync-08-remediation.mp4` | `08-remediation.wav` | PiP overlay |
| `lipsync-10-lifecycle.mp4` | `10-lifecycle.wav` | PiP overlay |
| `lipsync-11-analytics.mp4` | `11-analytics.wav` | PiP overlay |

Note: Sections 9 (transition), 12 (montage), and 13 (CTA) use either Wan 2.2 animated clips or voice-only.

### Wan 2.2 Dynamic Clips (3 clips)

| Clip | Description | Reference Images | Duration |
|------|-------------|-----------------|----------|
| `scene-opening.mp4` | Character standing in front of modern residential building, clipboard in hand, looking slightly concerned. Clean illustration style. | `front-facing.png`, `full-body-standing.png` | 5s |
| `scene-transition.mp4` | Character walking purposefully, turning a corner or stepping through a doorway. Suggests moving from one context to another. | `walking.png`, `three-quarter.png` | 4s |
| `scene-closing.mp4` | Character facing camera directly, warm confident smile, subtle background with floating device screens. Professional and inviting. | `front-facing.png`, `gesturing.png` | 5s |

---

## Screen Recording Shot List

Record against: `https://field-ops-frontend-79922828091.europe-west2.run.app`

### Pre-Recording Setup
- Chrome, full screen, hide bookmarks bar
- Window: 1920x1080
- Demo account with realistic data populated
- Hide system notifications
- Smooth, deliberate mouse — no rush

### Shots

**Shot 1: Module Launcher** (Section 2)
- Navigate to root `/`
- Show "Eversfield One — One Platform. Every Operation."
- Hover over Fire Doors card, then Lifecycle card
- Duration: ~15s raw (trim to 8s)

**Shot 2: Fire Doors Dashboard** (Section 3)
- Click into Fire Doors module
- Let dashboard load fully
- Slow scroll: KPI row → analytics section → charts
- Pause on Inspection Trends chart, then Scheme Breakdown
- Duration: ~40s raw (trim to 25s)

**Shot 3: Inspection Wizard Steps 1-2** (Section 4)
- Click "New Inspection" card
- Type in search box to find a door
- Click a door from the list
- Fill in: date, type (select "Routine"), inspector name
- Expand "Previous Survey Notes" briefly
- Click Next
- Duration: ~40s raw (trim to 25s)

**Shot 4: Inspection Checklist** (Section 5)
- Scroll through check item categories
- Expand a category
- Tap Pass on 2-3 items
- Tap Fail on 1 item
- Click camera icon, show photo capture
- Enter a measurement value
- Duration: ~40s raw (trim to 25s)

**Shot 5: Inspection Summary** (Section 6)
- Navigate to Step 4 (Summary)
- Show Pass/Fail/N/A breakdown
- Show overall result badge
- Hover over Submit button
- Briefly show offline indicator if visible
- Duration: ~30s raw (trim to 20s)

**Shot 6: Door Detail + Golden Thread** (Section 7)
- Navigate to a door detail page
- Scroll through inspection history
- Go back to dashboard
- Show Golden Thread Export card
- Click it briefly (or show the PDF preview)
- Duration: ~35s raw (trim to 25s)

**Shot 7: Remediation Dashboard** (Section 8)
- Navigate to Remediation Work
- Show the 6 KPI cards
- Scroll to Outstanding by Site table
- Briefly show Contractor Performance
- Duration: ~30s raw (trim to 22s)

**Shot 8: Lifecycle Project List** (Section 10)
- Navigate to Lifecycle module
- Show project cards grouped by client
- Click into a project
- Show Cover tab briefly
- Click to Element tab — show stacked bar chart
- Adjust year range slider
- Duration: ~45s raw (trim to 30s)

**Shot 9: Lifecycle Analytics** (Section 11)
- Click Analytics tab
- Show 3 executive insight cards
- Scroll to Pareto chart
- Scroll to Budget Forecast chart
- Toggle strategy dropdown
- Show export buttons (PDF/CSV)
- Duration: ~50s raw (trim to 35s)

**Shot 10: Platform Montage** (Section 12)
- Narrow browser to mobile width — show responsive layout
- Show PWA install prompt (if triggerable)
- Switch to different role view (Inspector vs Manager)
- Show offline indicator
- Quick cuts, 3-5s each
- Duration: ~30s raw (trim to 25s)
