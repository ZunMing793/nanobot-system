# Agent Browser 详细指南

网页自动化浏览器操作指南。

---

## 1. 快速使用（推荐）

使用 `ab` 命令，自动处理反检测：

```bash
# 打开网页（自动设置反检测）
ab open "https://mp.weixin.qq.com/s/xxx"

# 获取页面内容
ab snapshot

# 截图
ab screenshot

# 关闭浏览器
ab close
```

---

## 2. 读取微信公众号文章

```bash
ab open "https://mp.weixin.qq.com/s/xxx"
ab snapshot
```

---

## 3. 常用命令

| 命令 | 说明 |
|------|------|
| `ab open <url>` | 打开网页 |
| `ab snapshot` | 获取页面快照 |
| `ab snapshot -i` | 只获取可交互元素 |
| `ab click @e1` | 点击元素 |
| `ab fill @e2 "text"` | 填写输入框 |
| `ab screenshot` | 截图 |
| `ab close` | 关闭浏览器 |

---

## 4. 操作流程示例

### 4.1 读取文章内容

```bash
ab open "https://example.com/article"
ab snapshot
# 分析内容后
ab close
```

### 4.2 自动化操作

```bash
ab open "https://example.com"
ab snapshot -i          # 获取可交互元素
ab click @e1            # 点击第一个元素
ab fill @e2 "搜索内容"  # 填写输入框
ab snapshot             # 获取结果
ab close
```

---

## 5. 注意事项

- 使用 `ab` 命令会自动设置反检测配置
- 微信公众号等网站**必须**使用 `ab` 命令而非 `agent-browser`
- 操作完成后记得 `ab close` 关闭浏览器
- 如果页面加载慢，可以等待后再执行 snapshot
