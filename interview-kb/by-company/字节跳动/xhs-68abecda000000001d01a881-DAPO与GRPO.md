---
source: xiaohongshu
source_url: "https://www.xiaohongshu.com/explore/68abecda000000001d01a881"
collected_at: "unknown"
company: "字节跳动"
role: "unknown"
interview_round: "二面"
topics: ["DAPO", "GRPO", "强化学习"]
difficulty: 前沿
confidence: 低
has_questions: true
---

# 字节二面：DAPO 在 GRPO 上改进了什么？

## 具体问题

1. 「DAPO 在 GRPO 上改进了什么？」

公司与轮次来自笔记标题；正文和图片主要是论文学习笔记，没有提供现场面试对话。

## 参考答案要点

以下内容来自全部 6 张图片，未补入外部知识：

1. **Clip-Higher**：解耦裁剪上下界，增大上界，为低概率 token 留出更大的增长空间；原文强调保持下界不变，以维持探索空间。
2. **动态采样**：过滤组内回答全对或全错的 prompt，持续过采样，直到凑齐既非全对也非全错的有效 prompt；维持每个 batch 的有效 prompt 数量。
3. **Token-level policy gradient loss**：原文对比了 GRPO 的“样本内平均、再跨样本平均”和 token 级聚合，说明长回答中各 token 的模式应得到相应的促进或抑制。
4. **过长回答处理**：Overlong Filtering 屏蔽截断样本的损失；Soft Overlong Punishment 在长度缓冲区间内引入逐步变大的负奖励，降低截断带来的奖励噪声。
5. 另外两个设置：移除 KL 惩罚项；采用基于最终正确性的规则奖励，原图列出正确 `+1`、否则 `-1`。

图片 6 的过长惩罚公式已对照原图阅读，OCR 中的乱码不作为公式来源：

$$
R_{\mathrm{length}}(y)=
\begin{cases}
0, & |y|\le L_{\max}-L_{\mathrm{cache}},\\
\dfrac{(L_{\max}-L_{\mathrm{cache}})-|y|}{L_{\mathrm{cache}}}, & L_{\max}-L_{\mathrm{cache}}<|y|\le L_{\max},\\
-1, & L_{\max}<|y|.
\end{cases}
$$

## 关键细节

- 标题为“字节二面”，岗位未说明；内容是论文解读，不能据此确认真实面试经历，置信度为低。
- 图片中的示例裁剪值为 `0.2`；旧概率 `0.01` 与 `0.9` 对应原文演示的乘法上界 `0.012` 与 `1.08`。
- 图片 6 的对照图显示，Overlong Filtering 组在训练后段没有出现无过滤组的大幅生成熵尖峰；这是原图展示的实验现象。
- 原图表的指标为 **AIME24 avg@32**，按表中顺序保留数值，未做独立复现实验：

| 原图方案 | 数值 |
|---|---:|
| DeepSeek-R1-Zero-Qwen-32B | 47 |
| Naive GRPO | 30 |
| + Overlong Filtering | 36 |
| + Clip-Higher | 38 |
| + Soft Overlong Punishment | 41 |
| + Token-level Loss | 42 |
| + Dynamic Sampling（DAPO） | 50 |

- 原文称使用 Qwen-32B-Base，最终 AIME 2024 准确率达到 50%，训练步数为所比较基线的 50%；这些是原文实验描述。
- 全部 6 张图片已本地 OCR；数学公式与图表的 OCR 有噪声，保留原图用于核对。
- 关联：[[by-topic/DAPO|DAPO]]、[[by-topic/GRPO|GRPO]]、[[by-topic/强化学习|强化学习]]。

## 原文摘录

> 1. Clip-Higher，促进了系统的多样性并避免了熵崩溃。
> 2. 动态采样，提高训练效率和稳定性。
> 3. Token级别策略梯度损失，在长CoT RL场景中至关重要。
> 4. 过长奖励计算，减少奖励噪声并稳定训练。

原始材料：[正文、6 张图片与 OCR](../../raw/xiaohongshu/68abecda000000001d01a881.md)。
