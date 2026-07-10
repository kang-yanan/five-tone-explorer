# Error Log

## 2026-06-11 Session

### #1 IP Geolocation Blocks UI
- **Time**: ~13:00
- **Symptom**: Click "继续" → page hangs forever
- **Root cause**: `fetch('https://ipapi.co/json/')` blocked by GFW, `AbortSignal.timeout()` not supported in WeChat browser
- **Fix**: Non-blocking fire-and-forget with manual `AbortController` + `setTimeout` abort
- **Lesson**: Never block the main flow on external API calls. Always proceed immediately, collect optional data in background.

### #2 Resume Screen Confusion
- **Time**: ~13:30
- **Symptom**: "检测到未完成的实验" prompt appears unexpectedly
- **Root cause**: `checkResume()` finding stale localStorage sessions
- **Fix**: Removed resume screen entirely. Now `go()` clears all old data.
- **Lesson**: Clean state on fresh start. Don't surprise users with recovery prompts unless they explicitly ask.

### #3 AudioContext Outside User Gesture
- **Time**: ~14:00
- **Symptom**: First track plays, second track silent
- **Root cause**: `AudioContext` created in `loadAndPlay()`, not in click handler. Mobile browsers require user gesture for audio.
- **Fix**: Create `AudioContext` + `Audio` element in `confirmInfo()` (called from button click). Plus base64 WAV activation.
- **Lesson**: Initialize audio context in the SAME synchronous call chain as the button click.

### #4 decodeAudioData Fails for Western MP3s
- **Time**: ~14:30
- **Symptom**: Chinese tracks play, Western tracks fail silently
- **Root cause**: `ctx.decodeAudioData(buf)` fails for some MP3 encodings on mobile
- **Fix**: Switched to `createMediaElementSource(audioEl)` — uses browser's native decoder
- **Lesson**: Don't decode audio yourself. Use `<audio>` element. Browser decoders are more robust.

### #5 MediaElementSource Reconnection Fails
- **Time**: ~15:00
- **Symptom**: After first track, visualizer disappears, subsequent tracks fail
- **Root cause**: `createMediaElementSource()` can only be called ONCE per Audio element
- **Fix**: Single persistent `Audio` element. `createMediaElementSource` called once, then just change `.src` and `.play()`
- **Lesson**: Reuse audio elements. Don't `new Audio()` for every track.

### #6 setTimeout Breaks User Gesture
- **Time**: ~15:30
- **Symptom**: `audio.play()` rejected after rating submission
- **Root cause**: `setTimeout(playRound, 400)` moves playback outside user gesture window
- **Fix**: Call `playRound()` synchronously from `confirmRating()`
- **Lesson**: Zero delay between user action and audio playback. Every millisecond counts.

### #7 Silent Baseline Appears Frozen
- **Time**: ~16:00
- **Symptom**: 30-second silence with no visual feedback, users think it's broken
- **Root cause**: No countdown, no skip button
- **Fix**: Added 30-second countdown timer + "跳过静息" skip button
- **Lesson**: Always provide visual feedback for passive waiting states.

### #8 Western Tracks Not Heard
- **Time**: ~16:30
- **Symptom**: "第3个曲子到第4个曲子加载失败跳过"
- **Root cause**: Combination of #4 (decode failure) + #6 (gesture timeout) + #5 (reconnection)
- **Fix**: Applied fixes #4+#5+#6 simultaneously
- **Lesson**: Multiple interacting bugs. Fix the architecture, not individual symptoms.

### #9 Extra `}` Crashes All JS
- **Time**: ~17:00
- **Symptom**: "点都点不开了" — nothing works
- **Root cause**: Leftover `}` from `loadAndPlay` rewrite, caused `Unexpected token 'function'`
- **Fix**: Removed extra closing brace
- **Lesson**: Always run `node self_check.js` before deploy.

### #10 Emotion Labels Not Explained
- **Time**: ~17:15
- **Symptom**: Users don't know what 安定/内省/舒畅/振奋/宁静 mean
- **Root cause**: Labels appear on rating page without prior description
- **Fix**: Added 5 emotion descriptions to welcome page with emoji + explanation
- **Lesson**: Onboarding matters. Define terms before users encounter them.

### #11 Filename Confusion
- **Time**: All day
- **Symptom**: Edits to `五音情绪感知实验.html` not reflected on site
- **Root cause**: CloudBase serves `index.html` by default, not the Chinese-named file
- **Fix**: Deleted `五音情绪感知实验.html`, only `index.html` remains
- **Lesson**: One entry point. One file. No confusion.

### #12 Cloud Function No HTTP Trigger
- **Time**: ~17:30
- **Symptom**: Data only in localStorage, never uploaded
- **Root cause**: CloudBase `submitData` function has `timer` trigger, not `http`. CloudBase doesn't support HTTP triggers for deployed functions.
- **Fix**: Added CloudBase JS SDK, anonymous auth, direct `db.collection('experiments').add()`
- **Lesson**: Don't depend on serverless functions for real-time writes. Use SDK from client.

### #13 Progress Bars Hardcoded to 6
- **Time**: ~18:00
- **Symptom**: Progress bar shows 6 segments but experiment has 7
- **Root cause**: `progBars` used `[0,1,2,3,4,5]` instead of `order.length`
- **Fix**: Changed to `order.map((_,i) => ...)`
- **Lesson**: Never hardcode lengths. Derive from data.

### #14 Western Tracks Not Trimmed to Highlights
- **Time**: ~18:30
- **Symptom**: "西式音乐高潮段落的选取有前5秒左右的断断续续"
- **Root cause**: Original trim at 0s/4s didn't capture best segments
- **Fix**: Re-analyzed each track with librosa, re-trimmed to peak energy sections
- **Lesson**: Don't just trim from start. Analyze energy/centroid over time, pick the best 45s.

## Pre-Deploy Protocol

```bash
node self_check.js          # Must pass with 0 errors
# Then manually verify on mobile in incognito:
# 1. Open link → welcome page loads
# 2. Fill info → click 继续 → first track plays with visualization
# 3. Let first track finish → questionnaire appears
# 4. Rate → second track plays immediately
# 5. Verify silent baseline has countdown + skip button
# 6. Lock screen during playback → unlock → should continue from same track
# 7. Complete all 7 segments → results page shows
```
