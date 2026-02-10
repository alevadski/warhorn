---
name: warhorn:unmute
description: Unmute all warhorn sounds
allowed-tools:
  - Bash
---

Unmute all warhorn sounds. Run this command:

```bash
rm -f "$HOME/.claude/warhorn/.muted"
```

Confirm: "Sounds unmuted. The horn sounds!"
