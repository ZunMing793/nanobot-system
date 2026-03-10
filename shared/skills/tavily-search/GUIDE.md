# Tavily Search 详细指南

AI 优化的网络搜索工具。

---

## 1. 搜索命令

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 10
node {baseDir}/scripts/search.mjs "query" --deep
node {baseDir}/scripts/search.mjs "query" --topic news
```

---

## 2. 参数选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-n <count>` | 返回结果数量 | 5 |
| `--deep` | 深度搜索（更全面但更慢） | 关闭 |
| `--topic <topic>` | 搜索类型：`general` 或 `news` | general |
| `--days <n>` | 新闻搜索时限制天数 | - |

---

## 3. 从 URL 提取内容

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

---

## 4. 使用技巧

| 场景 | 推荐命令 |
|------|----------|
| 快速搜索 | `node {baseDir}/scripts/search.mjs "query"` |
| 获取更多结果 | `node {baseDir}/scripts/search.mjs "query" -n 10` |
| 深度研究 | `node {baseDir}/scripts/search.mjs "query" --deep` |
| 查找新闻 | `node {baseDir}/scripts/search.mjs "query" --topic news` |
| 提取网页内容 | `node {baseDir}/scripts/extract.mjs "url"` |

---

## 5. 注意事项

- API Key 已配置在 config.json 中
- Tavily 专为 AI 优化，返回简洁、相关的内容片段
- 复杂研究问题使用 `--deep`
- 查找时事新闻使用 `--topic news`
