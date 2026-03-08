# Tavily Search è¯¦ç»æå

AI ä¼åçç½ç»æç´¢å·¥å·ã?
---

## 1. æç´¢å½ä»¤

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 10
node {baseDir}/scripts/search.mjs "query" --deep
node {baseDir}/scripts/search.mjs "query" --topic news
```

---

## 2. åæ°éé¡¹

| åæ° | è¯´æ | é»è®¤å?|
|------|------|--------|
| `-n <count>` | è¿åç»ææ°é | 5 |
| `--deep` | æ·±åº¦æç´¢ï¼æ´å¨é¢ä½æ´æ¢ï¼ | å³é­ |
| `--topic <topic>` | æç´¢ç±»åï¼`general` æ?`news` | general |
| `--days <n>` | æ°é»æç´¢æ¶éå¶å¤©æ?| - |

---

## 3. ä»?URL æååå®¹

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

---

## 4. ä½¿ç¨æå·?
| åºæ¯ | æ¨èå½ä»¤ |
|------|----------|
| å¿«éæç´?| `node {baseDir}/scripts/search.mjs "query"` |
| è·åæ´å¤ç»æ | `node {baseDir}/scripts/search.mjs "query" -n 10` |
| æ·±åº¦ç ç©¶ | `node {baseDir}/scripts/search.mjs "query" --deep` |
| æ¥æ¾æ°é» | `node {baseDir}/scripts/search.mjs "query" --topic news` |
| æåç½é¡µåå®¹ | `node {baseDir}/scripts/extract.mjs "url"` |

---

## 5. æ³¨æäºé¡¹

- API Key å·²éç½®å¨ config.json ä¸?- Tavily ä¸ä¸º AI ä¼åï¼è¿åç®æ´ãç¸å³çåå®¹çæ®µ
- å¤æç ç©¶é®é¢ä½¿ç¨ `--deep`
- æ¥æ¾æ¶äºæ°é»ä½¿ç¨ `--topic news`
