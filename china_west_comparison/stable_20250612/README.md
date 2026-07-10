# 中式 vs. 西式音乐情绪对比研究

## 文件夹说明

本文件夹是从 `five_tone_experiment` 完整复制而来，用于新阶段的对比研究。
原始工作（音乐心理学版 + UbiComp版）完整保留在父目录中，不会受到影响。

## 与原始版本的区别

| | 原始版 | 对比版（本文件夹） |
|---|---|---|
| 刺激曲目 | 24 首中式传统器乐 | 24 首中式 + 5 首西式 |
| 叙事 | 五音调式→声学度量 | 中式传统音乐 vs. 西式流行音乐的情绪效应对比 |
| 核心问题 | 五音标签能否预测情绪？ | 中式音乐能否像西式音乐一样调节情绪？ |

## 待完成任务

### 1. 准备 Western 音频
- [ ] 准备 5 首西式音乐 45 秒片段（64kbps 单声道 MP3）
- [ ] 放入 `audio/western/` 目录
- [ ] 文件命名：`west_01.mp3` ~ `west_05.mp3`

推荐曲目：
| # | 曲目 | 艺人 | 情绪 | 截取区间 |
|---|------|------|------|----------|
| 1 | SICKO MODE | Travis Scott | 高唤醒 | 0:45–1:30 |
| 2 | God's Plan | Drake | 中高唤醒 | 0:30–1:15 |
| 3 | Feather | Nujabes | 中性/流畅 | 0:00–0:45 |
| 4 | Thinkin Bout You | Frank Ocean | 中低唤醒 | 0:30–1:15 |
| 5 | Holocene | Bon Iver | 低唤醒 | 0:00–0:45 |

备选：
| 替换 | 原曲 | 备选 |
|------|------|------|
| 1 | SICKO MODE | HUMBLE. — Kendrick Lamar (0:00–0:45) |
| 4 | Thinkin Bout You | Good Days — SZA (0:30–1:15) |
| 5 | Holocene | Avril 14th — Aphex Twin (0:00–0:45, 纯钢琴) |

### 2. 更新工具
- [ ] 修改 `五音情绪感知实验.html` 或 `index_light.html`
- [ ] 添加 5 首 Western 曲目的配置（mode 标记为 `western`）
- [ ] 上传音频到 CDN
- [ ] 更新 CloudBase 部署

### 3. 重新部署
- [ ] 向原 50 人发补测链接（仅 5 首 Western）
- [ ] 向新群发完整版链接（中西混合）
- [ ] 收集数据

### 4. 分析
- [ ] 中 vs. 西唤醒度分布对比（violin plot）
- [ ] 中 vs. 西情绪标签分布对比（stacked bar）
- [ ] 中 vs. 西声学特征 PCA 叠加
- [ ] 统计检验（Mann-Whitney U / t-test）

### 5. 论文
- [ ] 改写 paper_ubicomp.md 加入 §4.4 中西对比
- [ ] 生成 Fig 7（中西对比图）
- [ ] 更新 DOCX/HTML
