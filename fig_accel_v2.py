"""Accelerometer figure for UbiComp paper — motion ratio vs arousal."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from scipy import stats

# Load data
with open(r"F:\Claude project\five_tone_experiment\latest.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

with_sensor = [r for r in data if 'sensor' in r]

# Per-user data
motions, arousals, ages, genders = [], [], [], []
for r in with_sensor:
    summaries = r['summary']
    if not summaries: continue
    motions.append(r['sensor']['motionRatio'])
    arousals.append(np.mean([s['arousal'] for s in summaries]))
    ages.append(r['participant']['age'])
    genders.append(r['participant']['gender'])

motions = np.array(motions)
arousals = np.array(arousals)
ages = np.array(ages)
genders = np.array(genders)

# Morandi colors
C_STILL = '#8ba684'
C_MOVING = '#e0a060'
C_FEMALE = '#c77d8d'
C_MALE = '#6b8aaf'
C_TREND = '#555555'

fig, axes = plt.subplots(1, 3, figsize=(10, 3.8), constrained_layout=False)

# Panel A: Scatter with trend
ax = axes[0]
still_mask = np.array([r['sensor']['still'] for r in with_sensor if r.get('summary')])
ax.scatter(motions[still_mask], arousals[still_mask], c=C_STILL, alpha=0.7, s=40, edgecolors='white', linewidth=0.5, label='Still')
ax.scatter(motions[~still_mask], arousals[~still_mask], c=C_MOVING, alpha=0.7, s=40, edgecolors='white', linewidth=0.5, label='Moving')
# Trend line
z = np.polyfit(motions, arousals, 1)
x_line = np.linspace(0, 0.35, 100)
ax.plot(x_line, np.polyval(z, x_line), '--', color=C_TREND, linewidth=1.2, alpha=0.8)
r_val, p_val = stats.pearsonr(motions, arousals)
ax.text(0.02, 0.95, f'r = {r_val:.2f}\np = {p_val:.2f}', transform=ax.transAxes, fontsize=9, va='top')
ax.set_xlabel('Motion Ratio')
ax.set_ylabel('Mean Arousal (1–5)')
ax.set_title('A: Motion vs Arousal')
ax.legend(fontsize=7, frameon=False, loc='lower right')
ax.set_xlim(-0.01, 0.32)
ax.set_ylim(0.8, 5.2)

# Panel B: Quartile bar
ax = axes[1]
quartile_edges = np.percentile(arousals, [0, 25, 50, 75, 100])
q_means, q_sds, q_labels = [], [], []
for i in range(4):
    lo, hi = quartile_edges[i], quartile_edges[i+1]
    mask = (arousals >= lo) & (arousals <= hi)
    if mask.sum() == 0: continue
    q_motions = motions[mask]
    q_means.append(np.mean(q_motions))
    q_sds.append(np.std(q_motions) / np.sqrt(mask.sum()))
    q_labels.append(f'Q{i+1}\n({lo:.1f}–{hi:.1f})')

x = np.arange(len(q_means))
bars = ax.bar(x, q_means, color=[C_STILL, '#9aaf8a', '#b89a6a', C_MOVING], edgecolor='white', linewidth=0.5)
ax.errorbar(x, q_means, yerr=q_sds, fmt='none', color='#666', capsize=3, linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(q_labels, fontsize=8)
ax.set_ylabel('Mean Motion Ratio')
ax.set_title('B: Motion by Arousal Quartile')
ax.set_ylim(0, 0.22)

# Panel C: Gender
ax = axes[2]
male_m = motions[genders == 'male']
female_m = motions[genders == 'female']
bp = ax.boxplot([male_m, female_m], patch_artist=True, widths=0.4,
                medianprops=dict(color='#444', linewidth=1.2))
bp['boxes'][0].set_facecolor(C_MALE); bp['boxes'][0].set_alpha(0.7)
bp['boxes'][1].set_facecolor(C_FEMALE); bp['boxes'][1].set_alpha(0.7)
ax.set_xticklabels([f'Male\n(n={len(male_m)})', f'Female\n(n={len(female_m)})'])
ax.set_ylabel('Motion Ratio')
ax.set_title('C: Motion by Gender')
# t-test
t_g, p_g = stats.ttest_ind(male_m, female_m)
ax.text(0.5, 0.95, f'p = {p_g:.2f}', transform=ax.transAxes, fontsize=9, ha='center', va='top')

for ax in axes:
    ax.tick_params(direction='in', length=3, width=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.subplots_adjust(left=0.06, right=0.97, top=0.93, bottom=0.12, wspace=0.35)
fig.savefig(r'F:\Claude project\five_tone_experiment\fig_accel_v2.png', dpi=300)
fig.savefig(r'F:\Claude project\five_tone_experiment\fig_accel_v2.svg')
print('fig_accel_v2 saved.')
print(f'r={r_val:.3f}, p={p_val:.3f}, users={len(motions)}')
print(f'Still={still_mask.sum()}, Moving={(~still_mask).sum()}')
print(f'Male motion M={np.mean(male_m):.3f}, Female motion M={np.mean(female_m):.3f}')
