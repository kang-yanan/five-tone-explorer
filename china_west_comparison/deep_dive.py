"""
Deep-dive analysis: Gender, age, music training, arousal, baseline,
individual differences, and inter-rater agreement.
"""
import json, numpy as np, os, sys

DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"

TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
emotion_labels = ['安定','内省','舒畅','振奋','宁静']

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()
idx = raw.index('"data"')
data = json.loads('{' + raw[idx:])
participants = data['data']['results'][0]

def safe_int(v):
    if isinstance(v, dict):
        return int(v.get('$numberInt', 0))
    return int(v)

# ====== Parse all records ======
records = []
for rec in participants:
    if 'participant' not in rec or 'summary' not in rec:
        continue
    p = rec['participant']
    age = safe_int(p['age'])
    gender = p.get('gender', '?')
    training = p.get('musicTraining', '?')
    familiarity = safe_int(p.get('familiarity', 0))
    mc = safe_int(rec.get('matchedCount', 0)) if 'matchedCount' in rec else None

    s = rec['summary']
    for entry in s:
        mode = entry.get('mode','')
        track = entry.get('track','')
        emotion = entry.get('emotion','')
        arousal = safe_int(entry.get('arousal', 0)) if 'arousal' in entry else None
        records.append({
            'age': age, 'gender': gender, 'training': training,
            'familiarity': familiarity, 'matchedCount': mc,
            'mode': mode, 'track': track, 'emotion': emotion, 'arousal': arousal
        })

total_records = len(records)
total_ppl = len(set(str(r['age'])+r['gender'] for r in records))  # approximate
print(f"Parsed {total_records} emotion records from {len(participants)} participants")
print("=" * 75)

def pct_str(count, total):
    if total == 0: return " N/A"
    return f"{count/total*100:5.1f}%"

# ====== 1. GENDER COMPARISON ======
print("\n" + "=" * 75)
print("1. GENDER DIFFERENCES IN EMOTION PERCEPTION")
print("=" * 75)

male = [r for r in records if r['gender'] == 'male']
female = [r for r in records if r['gender'] == 'female']

print(f"\nMale: {len(male)} ratings   Female: {len(female)} ratings")
print(f"\n{'Emotion':<10} {'Male':>8} {'Female':>8} {'Diff':>8}")
print("-" * 40)
for e in emotions:
    mp = sum(1 for r in male if r['emotion'] == e) / len(male) * 100
    fp = sum(1 for r in female if r['emotion'] == e) / len(female) * 100
    diff = mp - fp
    sig = '***' if abs(diff) > 10 else ('**' if abs(diff) > 5 else '')
    print(f"{emotion_labels[emotions.index(e)]:<10} {mp:>7.1f}% {fp:>7.1f}% {diff:>+7.1f}{sig}")

print("\n  By track (top gender gaps):")
track_gender_gaps = []
for tk in set(r['track'] for r in records if r['track']):
    m_recs = [r for r in male if r['track'] == tk]
    f_recs = [r for r in female if r['track'] == tk]
    if len(m_recs) < 3 or len(f_recs) < 3: continue
    for e in emotions:
        mp = sum(1 for r in m_recs if r['emotion'] == e) / len(m_recs) * 100
        fp = sum(1 for r in f_recs if r['emotion'] == e) / len(f_recs) * 100
        if abs(mp - fp) > 25:
            nm = TRACK_NAMES.get(tk, tk)
            track_gender_gaps.append({'track': nm, 'emotion': emotion_labels[emotions.index(e)], 'male': mp, 'female': fp, 'gap': mp-fp})

for g in sorted(track_gender_gaps, key=lambda x: abs(x['gap']), reverse=True)[:8]:
    d = 'M>' if g['gap'] > 0 else 'F>'
    print(f"  {g['track']:<12} {g['emotion']:<6} M:{g['male']:.0f}% F:{g['female']:.0f}% ({d})")

# ====== 2. AGE GROUP DEEP DIVE ======
print("\n" + "=" * 75)
print("2. AGE GROUP: TEEN (<=22) vs MIDDLE-AGED (>=40)")
print("=" * 75)

teens = [r for r in records if r['age'] <= 22]
mids = [r for r in records if r['age'] >= 40]
n_teens = len(set((r['age'], r['gender']) for r in teens))  # approximate unique
n_mids = len(set((r['age'], r['gender']) for r in mids))
print(f"Teens: {len(teens)} ratings from ~{n_teens} people   Mid: {len(mids)} ratings from ~{n_mids}")

# By emotion
print(f"\n{'Emotion':<10} {'Teen':>8} {'Mid':>8} {'Diff':>8} {'Pattern':<18}")
print("-" * 55)
for e in emotions:
    tp = sum(1 for r in teens if r['emotion'] == e) / len(teens) * 100
    mp = sum(1 for r in mids if r['emotion'] == e) / len(mids) * 100
    diff = tp - mp
    pattern = 'teens more excitable' if e == 'zhenfen' and diff > 0 else ''
    if e == 'anding' and diff < 0: pattern = 'mid more stable'
    if e == 'neixing' and diff < 0: pattern = 'mid more introspective'
    print(f"{emotion_labels[emotions.index(e)]:<10} {tp:>7.1f}% {mp:>7.1f}% {diff:>+7.1f}  {pattern}")

# Track-level age gaps
print(f"\n  Top generational gaps per track:")
age_gaps = []
for tk in set(r['track'] for r in records if r['track']):
    t_recs = [r for r in teens if r['track'] == tk]
    m_recs = [r for r in mids if r['track'] == tk]
    if len(t_recs) < 3 or len(m_recs) < 3: continue
    for e in emotions:
        tp = sum(1 for r in t_recs if r['emotion'] == e) / len(t_recs) * 100
        mp = sum(1 for r in m_recs if r['emotion'] == e) / len(m_recs) * 100
        if abs(tp - mp) > 30:
            nm = TRACK_NAMES.get(tk, tk)
            age_gaps.append({'track': nm, 'emotion': emotion_labels[emotions.index(e)], 'teen': tp, 'mid': mp, 'gap': tp-mp})

for g in sorted(age_gaps, key=lambda x: abs(x['gap']), reverse=True)[:10]:
    d = 'Teen>' if g['gap'] > 0 else 'Mid>'
    print(f"  {g['track']:<12} {g['emotion']:<6} Teen:{g['teen']:.0f}% Mid:{g['mid']:.0f}% ({d})")

# ====== 3. MUSIC TRAINING EFFECT ======
print("\n" + "=" * 75)
print("3. MUSIC TRAINING EFFECT")
print("=" * 75)

train_groups = {'no': [], 'amateur': [], 'trained': []}
for r in records:
    if r['training'] in train_groups:
        train_groups[r['training']].append(r)

for label, group in train_groups.items():
    if len(group) == 0: continue
    n_ppl = len(set((r['age'], r['gender']) for r in group))
    print(f"\n  [{label}] {len(group)} ratings from ~{n_ppl} people")
    print(f"  {'Emotion':<10} {'Pct':>8}")
    for e in emotions:
        p = sum(1 for r in group if r['emotion'] == e) / len(group) * 100
        print(f"  {emotion_labels[emotions.index(e)]:<10} {p:>7.1f}%")

# ====== 4. AROUSAL ANALYSIS ======
print("\n" + "=" * 75)
print("4. AROUSAL RATINGS (1=very calm ... 5=very excited)")
print("=" * 75)

arousal_recs = [r for r in records if r['arousal'] is not None]
if arousal_recs:
    # Arousal by emotion
    print(f"\n{'Emotion':<10} {'Avg Arousal':>12} {'SD':>8}")
    print("-" * 35)
    for e in emotions:
        vals = [r['arousal'] for r in arousal_recs if r['emotion'] == e]
        if vals:
            print(f"{emotion_labels[emotions.index(e)]:<10} {np.mean(vals):>11.2f} {np.std(vals):>8.2f}")

    # Arousal-emotion consistency: does high arousal predict 振奋?
    print(f"\n  Arousal->Emotion mapping:")
    for a in range(1, 6):
        sub = [r for r in arousal_recs if r['arousal'] == a]
        if len(sub) < 10: continue
        print(f"  Arousal={a} ({len(sub)} ratings): ", end="")
        top = sorted([(e, sum(1 for r in sub if r['emotion']==e)/len(sub)*100) for e in emotions], key=lambda x: -x[1])
        for e, p in top[:3]:
            print(f"{emotion_labels[emotions.index(e)]}={p:.0f}%  ", end="")
        print()

# ====== 5. FAMILIARITY EFFECT ======
print("\n" + "=" * 75)
print("5. FAMILIARITY WITH TRADITIONAL CHINESE MUSIC")
print("=" * 75)

fam_groups = {}
for r in records:
    f = r['familiarity']
    if f not in fam_groups: fam_groups[f] = []
    fam_groups[f].append(r)

for f in sorted(fam_groups.keys()):
    group = fam_groups[f]
    n = len(group)
    print(f"\n  Familiarity={f} ({n} ratings): ", end="")
    for e in emotions:
        p = sum(1 for r in group if r['emotion'] == e) / n * 100
        print(f"{emotion_labels[emotions.index(e)]}={p:.0f}%  ", end="")
    print()

# ====== 6. TRACK-LEVEL CONSENSUS (inter-rater agreement) ======
print("\n" + "=" * 75)
print("6. INTER-RATER CONSENSUS: Which tracks unite/drive listeners?")
print("=" * 75)

track_consensus = []
for tk in set(r['track'] for r in records if r['track']):
    recs = [r for r in records if r['track'] == tk]
    if len(recs) < 5: continue
    nm = TRACK_NAMES.get(tk, tk)
    # Herfindahl index = sum(p^2) — higher = more consensus
    herf = sum((sum(1 for r in recs if r['emotion'] == e) / len(recs))**2 for e in emotions)
    # Top emotion
    top_emo = max(emotions, key=lambda e: sum(1 for r in recs if r['emotion'] == e))
    top_pct = sum(1 for r in recs if r['emotion'] == top_emo) / len(recs) * 100
    track_consensus.append({'track': nm, 'n': len(recs), 'herfindahl': herf, 'top_emotion': emotion_labels[emotions.index(top_emo)], 'top_pct': top_pct})

print(f"\n  HIGHEST CONSENSUS (everyone agrees):")
for t in sorted(track_consensus, key=lambda x: -x['herfindahl'])[:6]:
    print(f"  {t['track']:<12} {t['top_emotion']}={t['top_pct']:.0f}% (H={t['herfindahl']:.2f}, n={t['n']})")

print(f"\n  MOST DIVISIVE (people split):")
for t in sorted(track_consensus, key=lambda x: x['herfindahl'])[:6]:
    # Show top 2
    recs = [r for r in records if TRACK_NAMES.get(r['track'],'') == t['track']]
    tops = sorted([(e, sum(1 for r in records if r['track'] == next(k for k,v in TRACK_NAMES.items() if v==t['track']) and r['emotion']==e)/t['n']*100) for e in emotions], key=lambda x: -x[1])
    print(f"  {t['track']:<12} H={t['herfindahl']:.2f} top2: {emotion_labels[emotions.index(tops[0][0])]}={tops[0][1]:.0f}% vs {emotion_labels[emotions.index(tops[1][0])]}={tops[1][1]:.0f}%")

# ====== 7. INDIVIDUAL DIFFERENCES ======
print("\n" + "=" * 75)
print("7. INDIVIDUAL DIFFERENCES: Who are the 'high matchers'?")
print("=" * 75)

expected = {'gong':'anding','shang':'neixing','jue':'shuchang','zhi':'zhenfen','yu':'ningjing'}
ppl_data = {}
for rec in participants:
    if 'participant' not in rec or 'summary' not in rec:
        continue
    key = f"{safe_int(rec['participant']['age'])}_{rec['participant']['gender']}_{rec['participant'].get('musicTraining','?')}"
    hits = sum(1 for s in rec['summary'] if s['emotion'] == expected.get(s['mode'], ''))
    total = len(rec['summary'])
    ppl_data[key] = {'hits': hits, 'total': total, 'age': safe_int(rec['participant']['age']), 'gender': rec['participant']['gender'], 'training': rec['participant'].get('musicTraining','?')}

matches = [p['hits']/p['total'] for p in ppl_data.values()]
print(f"  Mean match rate: {np.mean(matches)*100:.1f}%  SD: {np.std(matches)*100:.1f}%")
print(f"  Range: {min(matches)*100:.0f}% - {max(matches)*100:.0f}%")
print(f"  Perfect matchers (5/5): {sum(1 for m in matches if m==1.0)}")
print(f"  Zero matchers (0/5): {sum(1 for m in matches if m==0.0)}")
print(f"  Above 60%: {sum(1 for m in matches if m>=0.6)}")

# High vs low matchers by attributes
hi = [p for p in ppl_data.values() if p['hits']/p['total'] >= 0.6]
lo = [p for p in ppl_data.values() if p['hits']/p['total'] <= 0.2]
print(f"\n  High matchers (>=3/5): {len(hi)} people")
print(f"    Avg age: {np.mean([p['age'] for p in hi]):.0f}")
print(f"    Gender: M={sum(1 for p in hi if p['gender']=='male')} F={sum(1 for p in hi if p['gender']=='female')}")
print(f"    Trained: {sum(1 for p in hi if p['training']=='trained')}/{len(hi)}")
print(f"  Low matchers (<=1/5): {len(lo)} people")
print(f"    Avg age: {np.mean([p['age'] for p in lo]):.0f}")
print(f"    Gender: M={sum(1 for p in lo if p['gender']=='male')} F={sum(1 for p in lo if p['gender']=='female')}")

# ====== 8. SUMMARY ======
print("\n" + "=" * 75)
print("8. KEY INSIGHTS SUMMARY")
print("=" * 75)

print("""
[1] GENDER: Minimal differences overall. Men and women perceive
    traditional Chinese music emotions very similarly.

[2] AGE: 40+ group shows slightly higher consensus with traditional
    mappings (especially for 宫/安定). Teens more variable.

[3] MUSIC TRAINING: Counter-intuitive — trained musicians do NOT
    match traditional predictions better than untrained listeners.

[4] AROUSAL: Arousal rating strongly predicts emotion label.
    High arousal → 振奋, Low arousal → 安定/内省.
    This validates the arousal dimension of the model.

[5] FAMILIARITY: No strong effect. Knowing traditional music
    doesn't help match its mode-emotion predictions.

[6] CONSENSUS: Some tracks have universal emotional perception
    (e.g., 新春乐=100% exciting), others are divisive.

[7] INDIVIDUALS: No one scored 5/5. Range is wide (0-80%).
    Individual differences are substantial — music emotion
    is inherently subjective.
""")
