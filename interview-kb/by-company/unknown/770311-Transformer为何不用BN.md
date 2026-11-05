---
source: douyin
source_url: "https://www.douyin.com/video/7703111353434721577"
collected_at: "2026-11-03T08:08:52+00:00"
company: "unknown"
role: "unknown"
interview_round: "unknown"
topics: ["Transformer", "Batch Normalization", "Layer Normalization"]
difficulty: 基础
confidence: 低
has_questions: true
aweme_id: "7703111353434721577"
author: "临渊不咸鱼🍂"
---

# Transformer 为何不用 BN？

关联主题：[[by-topic/Transformer|Transformer]] · [[by-topic/归一化|归一化]]

## 具体问题

1. Transformer 为何通常不用 Batch Normalization（BN）？

## 参考答案要点

原文未提供答案，采集到的内容只有问题标题和标签。

> **Agent 补充：** BN 依赖 batch 维度上的统计量，容易受到 batch size、样本长度和 padding 分布变化的影响；序列任务中不同位置的语义和有效 token 数也不稳定。Layer Normalization 在每个 token 的特征维度内独立归一化，不依赖其他样本，训练与自回归推理的行为更一致，因此更适合 Transformer。具体架构仍可能使用 RMSNorm、QK-Norm 或其他归一化变体，不能把“不用 BN”理解为绝对规则。

## 关键细节

- 原文作者自述为研一、深度学习学习者，没有提供公司、岗位或面试轮次。
- 当前条目更像面试知识点标题，而不是可验证的真实面经，所以置信度为“低”。
- 图文画面没有经过 OCR，答案可能存在于图片中；当前总结不能把 Agent 补充当作原文答案。

## 原文摘录

> Transformer 为何不用 BN？科软研一在读，深度学习小白，开一个抖音号监督自己每天学习。#科软 #深度学习 #transfomer

原始素材：[[raw/douyin/collection-7703111353434721577|collection-7703111353434721577]]
