# Anthropic Brand Styling 详细指南

Anthropic 官方品牌标识和样式资源完整指南。

---

## 1. 品牌颜色

### 1.1 主要颜色

| 颜色 | 色值 | 用途 |
|------|------|------|
| Dark | `#141413` | 主要文本和深色背景 |
| Light | `#faf9f5` | 浅色背景和深色上的文本 |
| Mid Gray | `#b0aea5` | 次要元素 |
| Light Gray | `#e8e6dc` | 微妙背景 |

### 1.2 强调色

| 颜色 | 色值 | 用途 |
|------|------|------|
| Orange | `#d97757` | 主要强调色 |
| Blue | `#6a9bcc` | 次要强调色 |
| Green | `#788c5d` | 第三强调色 |

---

## 2. 字体规范

| 类型 | 字体 | 回退字体 |
|------|------|----------|
| 标题 | Poppins | Arial |
| 正文 | Lora | Georgia |

**注意**：字体应预先安装在环境中以获得最佳效果

---

## 3. 功能特性

### 3.1 智能字体应用

- 标题（24pt 及更大）应用 Poppins 字体
- 正文应用 Lora 字体
- 如果自定义字体不可用，自动回退到 Arial/Georgia
- 保持所有系统的可读性

### 3.2 文本样式

- 标题（24pt+）：Poppins 字体
- 正文：Lora 字体
- 基于背景智能选择颜色
- 保留文本层次和格式

### 3.3 形状和强调色

- 非文本形状使用强调色
- 循环使用橙色、蓝色和绿色强调
- 在保持品牌一致性的同时增加视觉趣味

---

## 4. 技术细节

### 4.1 字体管理

- 可用时使用系统安装的 Poppins 和 Lora 字体
- 自动回退到 Arial（标题）和 Georgia（正文）
- 无需字体安装 - 使用现有系统字体
- 为获得最佳效果，请在环境中预装 Poppins 和 Lora 字体

### 4.2 颜色应用

- 使用 RGB 颜色值应用精确品牌匹配
- 通过 python-pptx 的 RGBColor 类精度
- 保持跨系统的颜色保真度

---

## 5. 应用场景

### 5.1 适用文档类型

- 演示文稿（.pptx）
- 文档（.docx）
- PDF 文件
- HTML 页面
- 任何需要 Anthropic 品牌风格的作品

### 5.2 关键词

branding, corporate identity, visual identity, styling, brand colors, typography, Anthropic brand, visual formatting, visual identity, company design standards
