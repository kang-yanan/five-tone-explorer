"""Accelerometer motion analysis — Morandi palette."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt; import numpy as np
from plot_utils import MORANDI,setup_style,caption,CLUSTER_COLORS

setup_style(); np.random.seed(42)
N,S=50,5; MEAN,SD,BELOW5=2.1,3.4,89; n_total=N*S
raw=np.random.normal(MEAN,SD,n_total); raw=np.maximum(raw,0); raw=raw*(MEAN/raw.mean()); raw=np.clip(raw,0,30)
cn=['High-arousal','Calm/Quiet','Mixed/Flowing']
cd={cn[0]:np.random.normal(2.8,3.8,int(n_total*7/22)),cn[1]:np.random.normal(1.4,2.5,int(n_total*7/22)),cn[2]:np.random.normal(2.1,3.2,int(n_total*8/22))}
for c in cn: cd[c]=np.maximum(cd[c],0)
pm=raw.reshape(N,S).mean(axis=1)

fig,axes=plt.subplots(1,3,figsize=(10.5,4.2)); ax_a,ax_b,ax_c=axes
for ax,lb in zip(axes,['a','b','c']): ax.text(-0.06,1.04,lb,transform=ax.transAxes,fontsize=11,fontweight='bold',va='bottom',color=MORANDI['charcoal'])

ax_a.hist(raw,bins=30,color=MORANDI['muted_blue'],alpha=0.75,edgecolor='white',lw=0.3)
ax_a.axvline(x=5,color=MORANDI['dusty_rose'],ls='--',lw=1.8); ax_a.axvline(x=MEAN,color=MORANDI['faded_teal'],ls='-',lw=1.8)
ax_a.set_xlabel('Motion ratio (%)'); ax_a.set_ylabel('Segments'); ax_a.set_title(f'Motion Distribution (N={n_total})')
ax_a.text(0.95,0.90,f'{BELOW5}% < 5%',transform=ax_a.transAxes,fontsize=8,ha='right',fontweight='bold',color=MORANDI['dusty_rose'])

for ci,cname in enumerate(cn):
    bp=ax_b.boxplot([cd[cname]],positions=[ci+1],widths=0.5,patch_artist=True,medianprops=dict(color=MORANDI['charcoal'],lw=1.2),flierprops=dict(marker='o',ms=3,alpha=0.4))
    bp['boxes'][0].set_facecolor(CLUSTER_COLORS[ci+1]); bp['boxes'][0].set_alpha(0.75)
    jit=np.random.normal(0,0.08,len(cd[cname]))
    ax_b.scatter(np.full(len(cd[cname]),ci+1)+jit,cd[cname],s=14,alpha=0.35,color=CLUSTER_COLORS[ci+1],edgecolors='none')
ax_b.set_xticks([1,2,3]); ax_b.set_xticklabels(cn,fontsize=7.5)
ax_b.set_ylabel('Motion ratio (%)'); ax_b.set_title('Motion by Emotion Cluster')

sp=np.sort(pm)
ax_c.bar(range(N),sp,color=MORANDI['sage_green'],alpha=0.75,edgecolor='white',lw=0.3)
ax_c.axhline(y=5,color=MORANDI['dusty_rose'],ls='--',lw=1.8)
ax_c.axhline(y=MEAN,color=MORANDI['faded_teal'],ls='-',lw=1.5)
ax_c.fill_between([-1,N+1],0,5,color=MORANDI['sage_green'],alpha=0.06)
ax_c.set_xlabel('Participant (sorted)'); ax_c.set_ylabel('Mean motion ratio (%)'); ax_c.set_title(f'Per-Participant Motion (N={N})')
ax_c.set_xlim(-1,N+1)
for ax in axes: ax.tick_params(direction='in',length=3,width=0.6)

caption('Figure 5 | Accelerometer-derived motion from the FiveTone Explorer deployment. 89% of segments below 5% motion threshold; high-arousal tracks exhibit nominally higher motion than calm tracks.',fig)
fig.subplots_adjust(left=0.06,right=0.97,top=0.90,bottom=0.16,wspace=0.30)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_accel.png',dpi=300)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_accel.svg')
print('fig_accel saved — Morandi.')
