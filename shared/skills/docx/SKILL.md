---
name: docx
description: "Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation."
always: true
allowed-tools:
  - Bash
  - Read
---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/docx/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 这是撒谎行为，会导致输出质量不合格

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

## 触发场景

1. 用户想要创建、编辑、读取或操作 Word (.docx) 文档
2. 用户提到 "Word doc"、"word document"、".docx"，或请求专业的 Word 文档格式（目录、标题、页码、信头）
3. 用户想要从 .docx 文件提取或重新组织内容，插入/替换图片，或在 Word 文件中执行查找替换
4. 用户需要在 Word 文档中处理修订或批注
5. 用户请求将内容转换为精美的 Word 文档（报告、备忘录、信函、模板等，输出为 .docx）

## 详细指南索引

完整操作流程、格式规范、示例请阅读：
- **GUIDE.md**：详细指南

## 概览

.docx 文件本质是包含 XML 文件的 ZIP 压缩包。
- 创建新文档：使用 JavaScript (docx-js)
- 编辑现有文档：解包后修改 XML
- 读取内容：使用 pandoc 或解包查看原始 XML
