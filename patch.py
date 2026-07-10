import re

with open('五音情绪感知实验.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add copy button before reload button
old_btn = '<button class="btn btn-secondary" onclick="location.reload()">'
new_btn = '''<button class="btn btn-primary" onclick="copyData()" style="background:var(--jue);margin:10px 0;">📋 复制我的数据 发回群里</button>
<p style="color:var(--text2);font-size:0.75em;">点上面按钮 → 回到微信 → 长按粘贴发送</p>
<button class="btn btn-secondary" onclick="location.reload()">'''
content = content.replace(old_btn, new_btn)

# 2. Add copyData() before line with "const all = JSON.parse(localStorage.getItem"
marker = "  const all = JSON.parse(localStorage.getItem('5tone_v4')||'[]');"
func = '''function copyData() {
  var all = JSON.parse(localStorage.getItem('5tone_v4')||'[]');
  var last = all[all.length-1];
  if (!last) { alert('no data'); return; }
  var out = { participant: participantInfo, experiment: { ratings: last.ratings, order: last.order, selectedTracks: last.selectedTracks, summary: last.summary } };
  var txt = JSON.stringify(out);
  var ta = document.createElement('textarea');
  ta.value = txt; ta.style.position='fixed'; ta.style.left='-9999px';
  document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); alert('已复制！回微信群长按粘贴发送。'); }
  catch(e) { prompt('请复制下方文字发给我:', txt.substring(0, 2000)); }
  document.body.removeChild(ta);
}

''' + marker
content = content.replace(marker, func)

with open('五音情绪感知实验.html', 'w', encoding='utf-8') as f:
    f.write(content)

import os
print('Done. Size:', os.path.getsize('五音情绪感知实验.html'), 'bytes')
