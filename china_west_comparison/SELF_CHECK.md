# Self-Check Before Deploy

Run `node self_check.js` before every `tcb hosting deploy`.

## Known Issues & Fix Status

| # | Issue | Root Cause | Fix | Verified |
|---|-------|-----------|-----|----------|
| 1 | 第一首无声→跳问卷 | audioEl.play() 在移动端需等待 load | `audioEl.src=url; audioEl.play()` 无等待 | ⬜ |
| 2 | 可视化消失 | animateBars 依赖 ana 变量 | 改为 sine-wave 独立运行 | ⬜ |
| 3 | 锁屏后重来 | saveSession 有但 go() 清空一切 | confirm() 弹窗恢复 | ⬜ |
| 4 | 静默基线卡住 | 无倒计时 | 30s 倒计时+跳过按钮 | ✅ |
| 5 | 西式开头卡顿 | canplaythrough 不可靠 | 简化：src→play() | ⬜ |
| 6 | 西式无声音 | decodeAudioData 失败 | MediaElementSource | ✅ |
| 7 | IP 定位卡 confirmInfo | 阻塞等待 | fire-and-forget | ✅ |
| 8 | 恢复页面混淆 | 旧 resume 页面残留 | 已删除，用 confirm() | ✅ |
| 9 | 多余 } JS 崩溃 | 编辑残留 | 已删除 | ✅ |
| 10 | 情绪标签无解释 | 欢迎页缺失 | 已添加 5 个情绪描述 | ✅ |
| 11 | setTimeout 打断手势 | 400ms 延迟 | 已删除 | ✅ |
| 12 | 云函数无 HTTP | CloudBase 不支持 | SDK 直写数据库 | ✅ |
| 13 | 进度条硬编码 6 | progBars 用 [0..5] | 改为 order.length | ✅ |
| 14 | 文件名混乱 | 两个 html 文件 | 只保留 index.html | ✅ |

## Pre-Deploy Checklist

```bash
# 1. JS syntax
node -e "try{new Function(require('fs').readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1]);console.log('OK')}catch(e){console.log('FAIL')}"

# 2. No dead references
grep -c "CLOUD_URL\|flushQueue\|checkResume\|doResume\|doNewSession\|resumePrompt\|decodeAudioData\|setTimeout.*playRound\|5tone_queue" index.html

# 3. Key features present
grep -c "audioEl.src.*audioEl.play\|animateBars\|skipRest\|restCountdown\|confirmInfo.*AudioContext\|createMediaElementSource\|SAVE_KEY.*go()" index.html

# 4. Audio files reachable (CDN)
for f in west_01 west_02 west_03 west_04 west_05 gong_01 shang_01 jue_01 zhi_01 yu_01; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://five-tone-cathykang-d4b0676685c9-1409437628.tcloudbaseapp.com/audio/embed25/${f}.mp3")
  [ "$code" != "200" ] && echo "MISSING: $f"
done

# 5. Deploy
tcb hosting deploy . --env-id five-tone-cathykang-d4b0676685c9

# 6. Verify deployed
curl -s "https://five-tone-cathykang-d4b0676685c9-1409437628.tcloudbaseapp.com/" | grep -c "audioEl.src.*audioEl.play"
```
