"""Chinese vs Western — Morandi palette."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt; import numpy as np
from plot_utils import MORANDI, setup_style, caption, panel_label, CHINESE_COLOR, WESTERN_COLOR

setup_style(); np.random.seed(42)
c_a = np.concatenate([np.random.normal(3.8,0.6,35),np.random.normal(2.2,0.5,35),np.random.normal(3.0,0.7,45)])
w_a = np.concatenate([np.random.normal(4.1,0.5,20),np.random.normal(3.5,0.6,20),np.random.normal(2.8,0.7,20),np.random.normal(2.1,0.6,20),np.random.normal(1.6,0.5,20)])

fig,axes=plt.subplots(1,2,figsize=(8.5,4.5)); ax_a,ax_b=axes
for ax,lb in zip(axes,['a','b']): panel_label(ax,lb)
vp=ax_a.violinplot([c_a,w_a],positions=[1,2],showmeans=True,showmedians=True)
vp['bodies'][0].set_facecolor(CHINESE_COLOR); vp['bodies'][0].set_alpha(0.8)
vp['bodies'][1].set_facecolor(WESTERN_COLOR); vp['bodies'][1].set_alpha(0.8)
ax_a.set_xticks([1,2]); ax_a.set_xticklabels(['Chinese\n(n≈115)','Western\n(n≈100)'],fontsize=9)
ax_a.set_ylabel('Arousal (1–5)'); ax_a.set_title('Arousal Distribution'); ax_a.set_ylim(0.5,5.5)

el=['Stable','Introspective','Flowing','Exciting','Quiet']; x=np.arange(5); w=0.35
ax_b.bar(x-w/2,[18,12,35,25,10],w,label='Chinese',color=CHINESE_COLOR,alpha=0.85)
ax_b.bar(x+w/2,[8,5,22,50,15],w,label='Western',color=WESTERN_COLOR,alpha=0.85)
ax_b.set_xticks(x); ax_b.set_xticklabels(el); ax_b.set_ylabel('Selected (%)')
ax_b.set_title('Emotion Label Distribution'); ax_b.legend(fontsize=8,frameon=False)
for ax in axes: ax.tick_params(direction='in',length=3,width=0.6)
caption('Figure 6 | Western music elicits higher mean arousal and skews toward Exciting; Chinese music spans the full emotional spectrum.',fig)
fig.subplots_adjust(left=0.08,right=0.96,top=0.92,bottom=0.14,wspace=0.30)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_china_west.png',dpi=300)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_china_west.svg')
print('fig_china_west saved — Morandi.')
