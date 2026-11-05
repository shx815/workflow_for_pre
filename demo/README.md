# 端到端 Demo：3 条抖音 + 3 条小红书

以下均来自已登录账号的指定收藏夹，使用真实采集内容；未使用合成面经。

| 来源与收藏夹 | 结构化条目 | 原始材料 |
|---|---|---|
| 抖音 `Knowledge base` | [因果掩码自注意力](../interview-kb/by-company/字节跳动/770043-因果掩码自注意力.md) | 见条目内原文链接 |
| 抖音 `Knowledge base` | [Agent 面试题仓库](../interview-kb/by-company/unknown/770081-大模型Agent面试题仓库.md) | 见条目内原文链接 |
| 抖音 `Knowledge base` | [Transformer 为何不用 BN](../interview-kb/by-company/unknown/770311-Transformer为何不用BN.md) | 见条目内原文链接 |
| 小红书 `knowledge` | [大模型题库与 KV Cache 分页](../interview-kb/by-company/unknown/xhs-6a8bec1f00000000330216c4-KVCache与分页.md) | 正文 + 全部 8 张图片 OCR |
| 小红书 `knowledge` | [DAPO 与 GRPO](../interview-kb/by-company/字节跳动/xhs-68abecda000000001d01a881-DAPO与GRPO.md) | 正文 + 全部 6 张图片 OCR，公式与实验图人工对照 |
| 小红书 `knowledge` | [百度一二面](../interview-kb/by-company/百度/xhs-6ab135d10000000035019d56-大模型算法岗一二面.md) | 正文 + 全部 1 张图片 OCR |

Demo 之外还完成 2 条小红书条目：[高频手撕清单](../interview-kb/by-company/unknown/xhs-694f63fc000000001e02153c-高频手撕清单.md)、[腾讯 Agentic/RL 面经](../interview-kb/by-company/腾讯/xhs-6a6481c3000000000e0365e2-Agent与RL面经.md)。

小红书首批合计 5 篇、20 张正文图片；OCR 失败数和缺图数均为 0。来源与每张图片的 SHA-256 见 [提取报告](../state/rednote-extraction-report.json)。

抖音主工具 fav2kb 遭遇 HTTP 403，本 Demo 的抖音内容使用指定 fallback 提取。阶段一的 3 条图文未做图片 OCR，Demo 对其仅使用真实提取到的正文；该限制不影响小红书的 20 张图片 OCR 验收。
