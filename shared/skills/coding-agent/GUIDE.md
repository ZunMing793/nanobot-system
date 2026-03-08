# Coding Agent è¯¦ç»æå

éè¿ tmux ç®¡ç Claude Code CLI ä¼è¯ï¼è®© NanoBot è½å¤æ§è¡ç¼ç¨ä»»å¡ã?
---

## 0. â ï¸ å¼ºå¶æ§è¡è§åï¼å¿è¯»ï¼

**ä»¥ä¸æåµå¿é¡»éè¿ tmux å¯å¨ Claude Codeï¼ç»å¯¹ä¸è½ç¨ exec/shell å½ä»¤æ¿ä»£**ï¼?
| è§¦åè¯?| è¯´æ |
|--------|------|
| ãç¨ Claude å¸®æ...ã?| ç¨æ·æç¡®æå®è¦ç¨ Claude |
| ãè®© Claude æ?..ã?| ç¨æ·æç¡®æå®è¦ç¨ Claude |
| ãClaude Codeã?| ç¨æ·ç´æ¥æå° Claude Code |
| ãæ¹å¼?ã?| ç¨æ·éæ©æ¹å¼2ï¼å³ coding-agentï¼?|
| ã?claudeã?| ç¨æ·ä½¿ç¨å½ä»¤è§¦å |

**éè¯¯ç¤ºä¾**ï¼ç»å¯¹ç¦æ­¢ï¼ï¼?```
ç¨æ·: ç?Claude å¸®ææ«æé¡¹ç®ç»æ
Bot: [å·æç´æ¥ç?exec æ§è¡ ls å½ä»¤]  â?éè¯¯ï¼?```

**æ­£ç¡®ç¤ºä¾**ï¼?```
ç¨æ·: ç?Claude å¸®ææ«æé¡¹ç®ç»æ
Bot: [æ§è¡ coding-agent.sh start]
     [æ§è¡ coding-agent.sh send "æ«æé¡¹ç®ç»æ"]
     [ç­å¾ Claude Code æ§è¡]
     [æè·è¾åºè¿åç»ç¨æ·]  â?æ­£ç¡®ï¼?```

**ä¸ºä»ä¹å¿é¡»ç¨ tmux**ï¼?1. Claude Code æ¯ä¸ä¸ªäº¤äºå¼ CLIï¼éè¦é¿æè¿è¡çä¼è¯
2. NanoBot ç?exec å·¥å·æ?60 ç§è¶æ¶éå?3. å¤æä»»å¡éè¦å¤è½®å¯¹è¯ï¼tmux å¯ä»¥ä¿æç¶æ?4. ç¨æ·æç¡®è¦æ±ç?Claude Codeï¼å¿é¡»å°éç¨æ·éæ©

**åµå¥ä¼è¯é®é¢**ï¼?- Claude Code ä¸åè®¸å¨å¦ä¸ä¸?Claude Code ä¼è¯ä¸­å¯å?- èæ¬å·²å¤çï¼ä½¿ç¨ `unset CLAUDECODE && claude` ç»è¿æ£æµ?- å¦æä»ç¶å¤±è´¥ï¼æ£æ¥ç¯å¢åé?`CLAUDECODE` æ¯å¦è¢«æ­£ç¡®æ¸é?
---

## 1. æ ¸å¿åè½

| åè½ | è¯´æ |
|------|------|
| å¯å¨ä»»å¡ | å?tmux ä¸­å¯å?Claude Code æ§è¡ç¼ç¨ä»»å¡ |
| çæ§è¿åº¦ | å®ææ£æ¥ä»»å¡æ§è¡ç¶æ?|
| å®æ¶äº¤äº | å?Claude Code åéæ¶æ¯ãè·åè¾å?|
| ä¼è¯ç®¡ç | éç½®ãéæ¯ä¼è¯?|

---

## 2. å½ä»¤åè¡¨

### 2.1 /claude \<ä»»å¡\>

å¯å¨ä¸ä¸ªæ°ä»»å¡ãå¦æ?tmux ä¼è¯ä¸å­å¨ï¼ä¼èªå¨åå»ºã?
**ç¤ºä¾**ï¼?```
/claude å¸®æå?/home/ubuntu/my-project ç®å½ä¸åå»ºä¸ä¸?Python èæ¬
```

### 2.2 /claude status

æ¥çå½å Claude Code ä¼è¯ç¶æã?
**è¿å**ï¼?- `running` - æ­£å¨æ§è¡
- `waiting` - ç­å¾è¾å¥
- `done` - ä»»å¡å®æ
- `no_session` - æ ä¼è¯?
### 2.3 /claude reset

éæ¯å½å?tmux ä¼è¯å¹¶éæ°åå»ºãç¨äºï¼
- ä»»å¡å¡ä½æ æ³ç»§ç»­
- éè¦åæ¢å°å®å¨ä¸åçä»»å?- ä¼è¯åºç°å¼å¸¸

### 2.4 /claude capture

è·å Claude Code å½åè¾åºï¼æå?50 è¡ï¼ã?
---

## 3. tmux æä½æ¹æ³

### 3.1 ä¼è¯ä¿¡æ¯

| éç½®é¡?| å?|
|--------|-----|
| ä¼è¯åç§° | `claude-code` |
| å·¥ä½ç®å½ | `/home/ubuntu` |
| Shell | `bash` |

### 3.2 æ ¸å¿å½ä»¤

```bash
# å¯å¨ä¼è¯å¹¶è¿è¡?Claude Code
tmux new-session -d -s claude-code -c /home/ubuntu "claude"

# åéæ¶æ¯ï¼æ¨¡æç¨æ·è¾å¥ï¼?tmux send-keys -t claude-code "ç¨æ·æ¶æ¯åå®¹" Enter

# æè·è¾åºï¼æå?50 è¡ï¼
tmux capture-pane -t claude-code -p -S -50

# æ£æ¥ä¼è¯æ¯å¦å­å?tmux has-session -t claude-code 2>/dev/null && echo "exists" || echo "not_exists"

# éæ¯ä¼è¯?tmux kill-session -t claude-code
```

### 3.3 è¾å©èæ¬

ä½¿ç¨å°è£å¥½çèæ¬ç®åæä½ï¼

```bash
# å¯å¨
coding-agent/scripts/coding-agent.sh start

# åéæ¶æ?coding-agent/scripts/coding-agent.sh send "å¸®æåä¸ª hello world"

# æè·è¾åº
coding-agent/scripts/coding-agent.sh capture

# æ£æ¥ç¶æ?coding-agent/scripts/coding-agent.sh status

# éç½®
coding-agent/scripts/coding-agent.sh reset

# è®°å½æ¥å¿
coding-agent/scripts/coding-agent.sh log "ä»»å¡å®æï¼åå»?hello.py"
```

---

## 4. ä»»å¡çæ§æºå¶

### 4.1 çæ§æµç¨

```
ç¨æ·åéä»»å?â?å¯å¨ tmux ä¼è¯ â?å®ææ£æ¥ç¶æ?â?æ£æµå®æ?â?æ±æ¥ç»æ
```

### 4.2 æ£æ¥é¢ç?
| ç¶æ?| æ£æ¥é´é?| è¶æ¶å¤ç |
|------|----------|----------|
| ä»»å¡æ§è¡ä¸?| æ¯?1 åé | 3 åéæ ååºæéç¨æ?|
| ç­å¾è¾å¥ | ç«å³éç¥ç¨æ· | ç­å¾ç¨æ·åå¤ |

### 4.3 ç¶ææ£æµé»è¾

1. **running**: tmux ä¼è¯å­å¨ï¼æåå è¡æ²¡ææç¤ºç¬¦
2. **waiting**: æ£æµå° Claude Code ç­å¾è¾å¥çç¹å¾ï¼å¦?`>`ã`?`ã`[y/n]`ï¼?3. **done**: è¾åºä¸­åå?`[TASK_DONE]` æ è®°æä»»å¡å®æç¹å¾?
---

## 5. ä»»å¡å®ææ£æµ?
### 5.1 å®ææ è®°

Claude Code å®æä»»å¡åä¼å¨è¾åºä¸­æ¾ç¤ºï¼?- `Task completed successfully`
- æç¨æ·å¨ä»»å¡æè¿°ä¸­çº¦å®?`[TASK_DONE]` æ è®°

### 5.2 ç­å¾è¾å¥ç¹å¾

æ£æµä»¥ä¸æ¨¡å¼å¤æ­æ¯å¦å¨ç­å¾è¾å¥ï¼?```
>
?
[y/n]
(Y/n)
éæ©
è¯·è¾å?```

---

## 6. æ¥å¿è®°å½æ ¼å¼

### 6.1 æ¥å¿æä»¶

`coding-agent/logs/tasks.log`

### 6.2 æ¥å¿æ ¼å¼

```
[2024-01-15 14:30:00] [START] ç¨æ·ï¼å¸®æåä¸?hello world
[2024-01-15 14:32:15] [STATUS] ä»»å¡æ§è¡ä¸?[2024-01-15 14:35:00] [WAITING] Claude è¯¢é®ï¼ä½¿ç¨ä»ä¹è¯­è¨ï¼?[2024-01-15 14:35:30] [INPUT] ç¨æ·åå¤ï¼Python
[2024-01-15 14:38:00] [DONE] ä»»å¡å®æï¼åå»?hello.py
```

### 6.3 æ¥å¿çº§å«

| çº§å« | è¯´æ |
|------|------|
| START | ä»»å¡å¼å§?|
| STATUS | ç¶ææ´æ?|
| WAITING | ç­å¾ç¨æ·è¾å¥ |
| INPUT | ç¨æ·è¾å¥ |
| DONE | ä»»å¡å®æ |
| ERROR | éè¯¯åç |

---

## 7. ç¤ºä¾å¯¹è¯æµç¨

### åºæ¯ï¼ç¨æ·è¯·æ±åå»ºèæ?
```
ç¨æ·: ç?Claude å¸®æå?/home/ubuntu ç®å½ä¸åå»ºä¸ä¸?Python èæ¬ï¼è¾å?hello world

Bot: [è¯»å GUIDE.md]
å·²è¯»åï¼SKILL.mdãGUIDE.md

å¥½çï¼ææ¥å¯å?Claude Code æ§è¡è¿ä¸ªä»»å¡ã?
[æ§è¡] coding-agent.sh start
[æ§è¡] coding-agent.sh send "å?/home/ubuntu ç®å½ä¸åå»ºä¸ä¸?Python èæ¬ï¼è¾å?hello world"
[æ§è¡] coding-agent.sh log "[START] åå»º Python hello world èæ¬"

Bot: ä»»å¡å·²å¯å¨ï¼æ­£å¨æ§è¡ä¸?..

[ç­å¾ 1 åéåæ£æ¥]

[æ§è¡] coding-agent.sh status â?waiting
[æ§è¡] coding-agent.sh capture

Bot: Claude Code è¯¢é®ï¼æ¨å¸æèæ¬å½åä¸?hello.py å¯ä»¥åï¼

ç¨æ·: å¯ä»¥

[æ§è¡] coding-agent.sh send "å¯ä»¥ï¼å½åä¸º hello.py"
[æ§è¡] coding-agent.sh log "[INPUT] ç¨æ·ç¡®è®¤å½å"

[ç­å¾ 30 ç§åæ£æ¥]

[æ§è¡] coding-agent.sh status â?done
[æ§è¡] coding-agent.sh capture
[æ§è¡] coding-agent.sh log "[DONE] åå»º hello.py æå"

Bot: ä»»å¡å®æï¼å·²å?/home/ubuntu/hello.py åå»ºèæ¬ã?```

---

## 8. æ³¨æäºé¡¹

### 8.1 è¶æ¶å¤ç

- NanoBot exec å·¥å·é»è®¤ 60 ç§è¶æ?- é¿æ¶é´ä»»å¡å¿é¡»å¨ tmux ä¸­è¿è¡ï¼ä¸è½ç´æ¥ exec
- 3 åéæ ååºè¦ä¸»å¨æéç¨æ·

### 8.2 ä¼è¯å²çª

- ç¡®ä¿ä¼è¯åç§° `claude-code` ä¸ä¼ä¸å¶ä»è¿ç¨å²çª?- åä¸æ¶é´åªè½æä¸ä¸ªæ´»è·ä»»å?- æ°ä»»å¡ä¼è¦çæ§ä»»å¡ï¼åæéç¨æ·ï¼

### 8.3 éè¯¯å¤ç

| éè¯¯ | å¤çæ¹å¼ |
|------|----------|
| tmux ä¼è¯ä¸å­å?| èªå¨åå»ºæ°ä¼è¯?|
| Claude Code å´©æº | éå¯ä¼è¯ï¼éç¥ç¨æ· |
| æéä¸è¶³ | æ£æ¥æä»?ç®å½æéï¼éç¥ç¨æ· |

### 8.4 å®å¨æ³¨æ

- ä¸è¦å?Claude Code ä¸­æ§è¡å±é©å½ä»¤ï¼rm -rfãsudo ç­ï¼
- ä¿®æ¹éè¦æä»¶åæéç¨æ·ç¡®è®?- ææä¿¡æ¯ä¸è¦è®°å½å°æ¥å¿?
---

## 9. èæ¬å®ç°åè?
```bash
#!/bin/bash
# coding-agent.sh - Claude Code tmux ç®¡çèæ¬

SESSION_NAME="claude-code"
WORK_DIR="/home/ubuntu"
LOG_FILE="coding-agent/logs/tasks.log"

log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

case "$1" in
    start)
        if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo "Session already exists"
        else
            tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "claude"
            log_message "START" "Claude Code session started"
            echo "Session started"
        fi
        ;;
    send)
        tmux send-keys -t "$SESSION_NAME" "$2" Enter
        log_message "INPUT" "$2"
        ;;
    capture)
        tmux capture-pane -t "$SESSION_NAME" -p -S -50
        ;;
    status)
        if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
            echo "no_session"
        else
            # æ£æ¥æåå è¡æ¯å¦å¨ç­å¾è¾å¥
            local output=$(tmux capture-pane -t "$SESSION_NAME" -p -S -5)
            if echo "$output" | grep -qE '(^\s*>|^\s*\?|\[y/n\]|\(Y/n\)|éæ©|è¯·è¾å?'; then
                echo "waiting"
            elif echo "$output" | grep -qE '(Task completed|TASK_DONE)'; then
                echo "done"
            else
                echo "running"
            fi
        fi
        ;;
    reset)
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null
        tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR" "claude"
        log_message "RESET" "Session reset"
        echo "Session reset"
        ;;
    log)
        log_message "INFO" "$2"
        ;;
    *)
        echo "Usage: $0 {start|send|capture|status|reset|log}"
        exit 1
        ;;
esac
```

---

## 10. å¿«éåè?
| æä½ | å½ä»¤ |
|------|------|
| å¯å¨ä»»å¡ | `/claude <ä»»å¡æè¿°>` |
| æ¥çç¶æ?| `/claude status` |
| è·åè¾åº | `/claude capture` |
| éç½®ä¼è¯ | `/claude reset` |
| èæ¬è·¯å¾ | `coding-agent/scripts/coding-agent.sh` |
| æ¥å¿è·¯å¾ | `coding-agent/logs/tasks.log` |
