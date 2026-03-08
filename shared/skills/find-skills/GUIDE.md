# Find Skills è¯¦ç»æå

æ¬ææ¡£åå«åç°åå®è£ agent skills çå®æ´æä½æµç¨ã?
---

## 1. ä¸¤å¹³å°æç´¢ç­ç?
### Platform 1: skills.sh (å®æ¹)

```bash
npx skills find [query]
```
- å®æ¹æè½æ³¨åè¡¨
- ç²¾éé«è´¨éæè?- éç¨äºï¼å¼åå·¥å·ãå®æ¹éæ?
### Platform 2: ClawHub (ç¤¾åº)

```bash
npx clawhub@latest search [query]
npx clawhub@latest explore  # æµè§ææ°æè?```
- æ´å¹¿æ³çç¤¾åºæè?- æ´å¤éç¨å·¥å·
- éç¨äºï¼çäº§åãèªå¨åãä¸ä¸ä»»å?
**å¨çº¿æµè§ï¼?*
- https://skills.sh/
- https://clawhub.ai/

---

## 2. å¸®å©ç¨æ·åç°æè?
### åºæ¯ Aï¼ç¨æ·ç¥éèªå·±éè¦ä»ä¹?
**Step 1: æç´¢æè?*
```bash
# å¨ä¸¤ä¸ªå¹³å°ä¸æç´¢ä»¥è·å¾æä½³ç»æ?npx skills find [query]
npx clawhub@latest search [query]
```

**Step 2: å±ç¤ºéé¡¹**
åç¨æ·å±ç¤ºï¼
1. æè½åç§°åæè¿°
2. å®è£å½ä»¤
3. äºè§£æ´å¤çé¾æ?
**Step 3: è·å¾æ¹ååå®è£?*

### åºæ¯ Bï¼ç¨æ·ä¸ç¥éæç´¢ä»ä¹?
**Step 1: æ¥éæè½ç®å½?*

éè¯»æè½ç®å½åèæä»¶ä»¥æ¾å°ç¸å³ç±»å«ï¼?```
find-skills/references/skills-catalog.md
```

**Step 2: æåºæ¾æ¸é®é¢**
- "æ¨æ³å®æä»ä¹ç±»åçä»»å¡ï¼?
- "æ¨æ¯å¨å¤çææ¡£ãæ°æ®ãç½é¡µæç´¢è¿æ¯èªå¨åï¼?

**Step 3: æ ¹æ®ç±»å«æ¨è**

| ç¨æ·éæ±?| æ¨èæè?|
|----------|----------|
| å¤çææ¡£ | `pdf`, `docx`, `xlsx`, `pptx` |
| ç½é¡µæç´¢ | `tavily-search`, `exa-web-search-free` |
| éèæ°æ® | `tushare-finance`, `stock-market-pro` |
| æµè§å¨èªå¨å | `agent-browser` |
| è§é¢ç¼è¾ | `ffmpeg-video-editor` |
| é®ä»¶å¤ç | `email-management-expert` |

---

## 3. å¸¸ç¨æè½ç±»å?
| ç±»å« | æç´¢å³é®è¯?|
|------|-----------|
| Web å¼å?| react, nextjs, typescript, css, tailwind |
| æµè¯ | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| ææ¡£ | docs, readme, changelog, api-docs |
| ä»£ç è´¨é | review, lint, refactor, best-practices |
| è®¾è®¡ | ui, ux, design-system, accessibility |
| çäº§å?| workflow, automation, git |
| æ°æ® | finance, stock, analysis, excel |

---

## 4. NanoBot ç³»ç»å®è£æ¹æ³

**éè¦ï¼NanoBot ä½¿ç¨å±äº«æè½ç®å½ï¼**

### æ¹æ³ 1: ClawHubï¼æ¨è?- æ¯æ --workdirï¼?
```bash
npx clawhub@latest install <slug> --workdir /home/NanoBot/shared
```

### æ¹æ³ 2: skills.shï¼éå?cd å°ç®å½ï¼

```bash
# skills CLI ä¸æ¯æ?--workdirï¼å¿é¡»å cd
cd /home/NanoBot/shared/skills
npx skills add <owner/repo@skill> -y
cd -  # è¿åä¹åçç®å½?```

### æ¹æ³ 3: æå¨ä¸è½½ï¼ç½ç»å¤±è´¥æ¶ï¼?
å½?`git clone` è¶æ¶æ¶ï¼ä½¿ç¨ GitHub API + wget æå¨ä¸è½½æä»¶ã?
**Step 1: ååºæè½ç®å½åå®?*
```bash
# æ£æ¥æè½ä¸­æåªäºæä»?curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>" | jq -r ".[].name"
```

**Step 2: åå»ºæè½ç®å½ç»æ?*
```bash
mkdir -p <skill-name>/{scripts,references}
```

**Step 3: ä¸è½½æä»¶**
```bash
# ä¸è½½ SKILL.mdï¼å¿éï¼?wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/SKILL.md" \
  -O <skill-name>/SKILL.md

# ä¸è½½èæ¬ï¼å¦æï¼
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/script.py" \
  -O <skill-name>/scripts/script.py

# ä¸è½½åèæä»¶ï¼å¦æï¼?wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/references/ref.md" \
  -O <skill-name>/references/ref.md
```

**Step 4: æ¹éä¸è½½ç®å½ä¸­çæææä»?*
```bash
# ä¸è½½ scripts ç®å½ä¸­çæææä»?for f in $(curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>/scripts" | jq -r ".[].name"); do
  wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/$f" \
    -O "<skill-name>/scripts/$f"
done
```

**å¸¸è§éè¯¯ç±»ååè§£å³æ¹æ¡ï¼**

| éè¯¯ | å«ä¹ | è§£å³æ¹æ¡ |
|------|------|----------|
| `Connection timed out` | ç½ç»è¶æ¶ | ä½¿ç¨ GitHub API + wget |
| `TLS connection was non-properly terminated` | TLS ä¸­æ­ | ä½¿ç¨ GitHub API + wget |
| `Failed to connect to xxx port 443` | ç«¯å£è¢«é»æ­?| ä½¿ç¨ GitHub API + wget |

**ä¸ºä»ä¹?GitHub API å?git clone å¤±è´¥æ¶ä»è½å·¥ä½ï¼**
- API ä½¿ç¨ HTTPS over 443 ç«¯å£ï¼ä¸ git ç¸åï¼?- API æ´ç¨³å®ï¼ä¸éè¦?git åè®®
- åæä»¶ä¸è½½æ¯å®æ´åéæ´å°

---

## 5. å¸¸è§éè¯¯é¿å

| éè¯¯ | åå  | æ­£ç¡®æ¹å¼ |
|------|------|----------|
| `npx skills add xxx -g -y` | å¨å±å®è£ï¼éå±äº« | `cd /home/NanoBot/shared/skills && npx skills add xxx -y` |
| `npx skills add xxx --workdir ...` | skills CLI ä¸æ¯æ?--workdir | ä½¿ç¨ ClawHub æå cd |
| `npx clawhub install xxx -g` | éè¯¯åæ° | `npx clawhub install xxx --workdir /home/NanoBot/shared` |

---

## 6. å®è£åæ£æ¥æ¸å?
å®è£æ°æè½åï¼æ£æ¥ï¼

1. **allowed-tools** - å¦ææè½æèæ¬ï¼ç¡®ä¿?SKILL.md æï¼
   ```yaml
   allowed-tools:
     - Bash(python:*)  # ç¨äº Python èæ¬
     - Read
   ```

2. **API éç½®** - å¦ææè½éè¦å¤é?APIï¼åå»?config.jsonï¼?   ```bash
   echo '{"api_key": "your_key"}' > <skill-name>/config.json
   ```

3. **éå¯ bots** ä»¥å è½½æ°æè?
---

## 7. æªæ¾å°æè½æ¶

1. æ¿è®¤æ²¡ææ¾å°ç°ææè?2. æä¾ç¨éç¨è½åå¸®å©
3. å»ºè®®åå»ºèªå®ä¹æè½ï¼

```bash
npx skills init my-custom-skill
```

---

## 8. åèæä»?
- **æè½ç®å½?*: `references/skills-catalog.md` - æç±»å«ç»ç»çå®æ´æè½ç®å½?