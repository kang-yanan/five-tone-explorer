// Self-check for original Web Audio approach
const fs = require('fs');
const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
let errors = [];
try { new Function(js); } catch(e) { errors.push('JS: '+e.message.split('\n')[0]); }
const need = [
  ['new Audio\\(', 'audio: Audio element created'],
  ['BufferSource|createBufferSource', 'audio: BufferSource'],
  ['AnalyserNode|createAnalyser', 'visualizer: AnalyserNode'],
  ['AudioContext.*webkitAudioContext', 'audio: AudioContext created'],
  ['skipRest', 'silent: skip button'],
  ['restCountdown', 'silent: countdown'],
  ['SAVE_KEY', 'session: save key'],
  ['submitToCloud', 'cloud: submit'],
  ['cloudbase\\.init', 'cloud: SDK init'],
  ['WESTERN_MODES', 'western: modes defined'],
  ['ALL_MUSIC', 'data: ALL_MUSIC'],
  ['order\\.map', 'progBars: dynamic'],
];
const dead = ['CLOUD_URL', 'flushQueue', 'checkResume', 'doResume', 'doNewSession', 'resumePrompt', '5tone_queue'];
need.forEach(([p,d]) => { if (!new RegExp(p).test(html)) errors.push('MISSING: '+d); });
dead.forEach(s => { if (new RegExp(s).test(js)) errors.push('DEAD: '+s); });
if (errors.length===0) { console.log('SELF CHECK: PASSED ✅'); process.exit(0); }
else { console.log('SELF CHECK: '+errors.length+' ERRORS ❌'); errors.forEach(e=>console.log('  - '+e)); process.exit(1); }
