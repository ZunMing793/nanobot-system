# Skills Catalog Reference

This file provides a curated catalog of available skills from multiple platforms to help you discover the right skill for your needs.

## Platform Overview

| Platform | Focus | Search Command | Install Command |
|----------|-------|----------------|-----------------|
| **skills.sh** | Official & community skills | `npx skills find [query]` | `cd /home/NanoBot/shared/skills && npx skills add <owner/repo@skill> -y` |
| **ClawHub** | General-purpose skills | `npx clawhub@latest search [query]` | `npx clawhub@latest install <slug> --workdir /home/NanoBot/shared` |

---

## Skills by Category

### Web & Frontend Development

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `vercel-react-best-practices` | React/Next.js performance optimization | `cd /home/NanoBot/shared/skills && npx skills add vercel-labs/agent-skills@vercel-react-best-practices -y` |
| `tailwind-design` | Tailwind CSS design patterns | Search: `npx skills find tailwind` |
| `typescript-expert` | TypeScript best practices | Search: `npx skills find typescript` |

### Document Processing

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `pdf` | PDF reading and analysis | `cd /home/NanoBot/shared/skills && npx skills add anthropics/skills@pdf -y` |
| `docx` | Word document processing | `cd /home/NanoBot/shared/skills && npx skills add anthropics/skills@docx -y` |
| `xlsx` | Excel spreadsheet handling | `cd /home/NanoBot/shared/skills && npx skills add anthropics/skills@xlsx -y` |
| `pptx` | PowerPoint presentation handling | `cd /home/NanoBot/shared/skills && npx skills add anthropics/skills@pptx -y` |

### Data & Finance

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `tushare-finance` | Chinese financial data analysis | `npx clawhub@latest install tushare-finance --workdir /home/NanoBot/shared` |
| `china-stock-analysis` | A-share market analysis | `npx clawhub@latest install china-stock-analysis --workdir /home/NanoBot/shared` |
| `stock-market-pro` | Stock market analysis tools | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@stock-market-pro -y` |

### Search & Research

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `tavily-search` | Web search API integration | `cd /home/NanoBot/shared/skills && npx skills add anthropics/skills@tavily-search -y` |
| `exa-web-search-free` | Free web search with Exa | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@exa-web-search-free -y` |
| `twitter-search` | Twitter/X content search | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@twitter-search -y` |

### DevOps & Cloud

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `docker-expert` | Docker container management | Search: `npx skills find docker` |
| `kubernetes-deploy` | K8s deployment workflows | Search: `npx skills find kubernetes` |
| `ci-cd-pipeline` | CI/CD pipeline automation | Search: `npx skills find ci-cd` |

### Browser & Automation

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `agent-browser` | Browser automation with Playwright | Already installed at `agent-browser` |

### Communication

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `email-management-expert` | Email handling and management | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@email-management-expert -y` |
| `internal-comms` | Internal communication tools | Already installed |

### Media Processing

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `ffmpeg-video-editor` | Video editing with FFmpeg | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@ffmpeg-video-editor -y` |

### Productivity & Self-Improvement

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `self-improvement` | Personal development workflows | `cd /home/NanoBot/shared/skills && npx skills add sundial-org/awesome-openclaw-skills@self-improvement -y` |
| `self-improving-agent` | Learn from mistakes and feedback | Already installed |

### Design & Creative

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| `canvas-design` | Canvas-based design tools | Already installed |
| `brand-guidelines` | Brand identity guidelines | Already installed |

---

## Scenario-Based Recommendations

### "I need to analyze a document"
1. **PDF** 鈫?`pdf` skill
2. **Word** 鈫?`docx` skill
3. **Excel** 鈫?`xlsx` skill
4. **PowerPoint** 鈫?`pptx` skill

### "I need to search the web"
1. **General search** 鈫?`tavily-search` or `exa-web-search-free`
2. **Social media** 鈫?`twitter-search`

### "I need to handle financial data"
1. **Chinese stocks** 鈫?`tushare-finance` or `china-stock-analysis`
2. **General stocks** 鈫?`stock-market-pro`

### "I need to automate browser tasks"
鈫?`agent-browser` skill

### "I need to process video/audio"
鈫?`ffmpeg-video-editor` skill

### "I need help with coding"
1. **React/Next.js** 鈫?`vercel-react-best-practices`
2. **General** 鈫?Search `npx skills find [technology]`

---

## NanoBot Installation Guide

### Important Notes

1. **skills CLI does NOT support `--workdir`**
   - Must `cd` to target directory first
   - Or use ClawHub which supports `--workdir`

2. **ClawHub supports `--workdir`**
   - Can install directly to shared directory

### Correct Installation Methods

```bash
# Method 1: ClawHub (Recommended)
npx clawhub@latest install <slug> --workdir /home/NanoBot/shared

# Method 2: skills.sh (cd first)
cd /home/NanoBot/shared/skills
npx skills add <owner/repo@skill> -y
cd -

# Method 3: Manual download (network fallback)

When `git clone` times out, use GitHub API + wget to download files manually.

**Step 1: List skill directory contents**
```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>" | jq -r ".[].name"
```

**Step 2: Create skill directory structure**
```bash
mkdir -p <skill-name>/{scripts,references}
```

**Step 3: Download files**
```bash
# Download SKILL.md (required)
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/SKILL.md" \
  -O <skill-name>/SKILL.md

# Download scripts (if any)
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/script.py" \
  -O <skill-name>/scripts/script.py
```

**Step 4: Batch download all files in a directory**
```bash
for f in $(curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>/scripts" | jq -r ".[].name"); do
  wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/$f" \
    -O "<skill-name>/scripts/$f"
done
```

**Why GitHub API works when git clone fails:**
- API is more stable than git protocol
- Single file downloads are smaller than full clone
- Works even when git port is blocked
```

### Common Mistakes

| Wrong Command | Problem | Correct Command |
|---------------|---------|-----------------|
| `npx skills add xxx -g -y` | Installs globally, not to shared | `cd /home/NanoBot/shared/skills && npx skills add xxx -y` |
| `npx skills add xxx --workdir /home/NanoBot/shared` | skills CLI doesn't support --workdir | Use ClawHub or cd first |
| `npx clawhub install xxx` | Installs to current dir | `npx clawhub install xxx --workdir /home/NanoBot/shared` |

---

## Search Tips

### Effective Keywords
- Be specific: "react testing" > "testing"
- Try alternatives: "deploy" / "deployment" / "ci-cd"
- Include framework names: "nextjs", "django", "flask"

### When No Results Found
1. Try broader keywords
2. Check ClawHub: `npx clawhub@latest search [query]`
3. Browse online: https://skills.sh/ or https://clawhub.ai/

---

## Post-Installation Checklist

```bash
# 1. Check if skill has scripts
ls <skill-name>/scripts/

# 2. If scripts exist, verify allowed-tools in SKILL.md
grep "allowed-tools:" <skill-name>/SKILL.md

# 3. If API needed, create config.json
echo '{"api_key": "your_key"}' > <skill-name>/config.json

# 4. Restart bots to load new skills
```
