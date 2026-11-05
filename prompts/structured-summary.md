# 面经结构化总结

只根据提供的原始 Markdown 生成一篇中文笔记。保真优先，不得把常识或推断伪装成原文。

frontmatter 必须包含且不得留空：

```yaml
---
source: douyin | xiaohongshu
source_url: ""
collected_at: ""
company: "unknown"
role: "unknown"
interview_round: "unknown"
topics: ["unknown"]
difficulty: 基础 | 进阶 | 前沿 | unknown
confidence: 高 | 中 | 低
has_questions: true | false
---
```

正文必须严格包含：

```markdown
## 具体问题

## 参考答案要点

## 关键细节

## 原文摘录
```

要求：

- `## 具体问题` 逐条保留原始问题表述；没有具体问题时写“原文未提供具体面试问题”。
- 答案只写原文提供的思路；没有答案时明确写“原文未提供”。
- 可选知识补充必须放在独立的“Agent 补充”标记下，并遵循补充规则。
- 公司、轮次或岗位无法确认时填 `unknown`，不得使用空字符串。
- `confidence` 衡量其是否像真实面经：具体公司、轮次、题目和细节越完整越高；营销汇总或泛知识点应降低。
- 原文摘录累计不超过 500 个中文字符。
- 末尾加入原始素材的相对链接，保证可溯源。
