---
name: warhorn:setup
description: Configure warhorn sound notifications
allowed-tools:
  - AskUserQuestion
  - Bash
---

<objective>
Configure warhorn sound notifications. Interview the user about their preferences, then apply the configuration.
NEVER modify, overwrite, or recreate ANY files in ~/.claude/warhorn/scripts/. Those scripts are pre-installed. Only CALL them.
</objective>

<process>

## Step 1: Greet and Ask About Hooks

Display:
```
Let's configure warhorn! I'll ask a few quick questions.
```

Use the AskUserQuestion tool:

```json
{
  "questions": [
    {
      "question": "Which hooks should play sounds?",
      "header": "Hooks",
      "multiSelect": true,
      "options": [
        {
          "label": "Core (recommended)",
          "description": "Stop, PermissionRequest, PostToolUseFailure — the essentials"
        },
        {
          "label": "Session",
          "description": "SessionStart, SessionEnd — know when sessions begin/end"
        },
        {
          "label": "Notifications",
          "description": "Notification, TaskCompleted — important alerts"
        },
        {
          "label": "Subagents",
          "description": "SubagentStart, SubagentStop — track agent activity"
        }
      ]
    }
  ]
}
```

Wait for response using AskUserQuestion. If they select "Other" and type custom hooks, parse the hook names from their text.

Map selections to hook names:
- Core = Stop, PermissionRequest, PostToolUseFailure
- Session = SessionStart, SessionEnd
- Notifications = Notification, TaskCompleted
- Subagents = SubagentStart, SubagentStop
- If they mention "all" or "everything" = all 14 hooks
- If they mention "granular" = PreToolUse, PostToolUse, UserPromptSubmit, TeammateIdle, PreCompact

## Step 2: Ask About Sound Type

Use the AskUserQuestion tool:

```json
{
  "questions": [
    {
      "question": "How should sounds work?",
      "header": "Sound type",
      "multiSelect": false,
      "options": [
        {
          "label": "Instrumental only (recommended)",
          "description": "Bundled chimes and pings. Works right away, no setup needed."
        },
        {
          "label": "AI voice lines",
          "description": "Character voice via edge-tts (needs pip install edge-tts + internet)"
        },
        {
          "label": "Both",
          "description": "Instrumentals + voice lines mixed in each folder"
        }
      ]
    }
  ]
}
```

Wait for response using AskUserQuestion.

- If "Instrumental only" → skip to Step 5 (Apply).
- If "AI voice lines" or "Both" → continue to Step 3.

## Step 3: Ask About Voice Character (only if voice or both)

Use the AskUserQuestion tool:

```json
{
  "questions": [
    {
      "question": "Pick a voice:",
      "header": "Voice",
      "multiSelect": false,
      "options": [
        {
          "label": "Male mid-range",
          "description": "British male, mid-pitch. Versatile default."
        },
        {
          "label": "Male deep",
          "description": "Australian male, deep and gruff."
        },
        {
          "label": "Female mid-range",
          "description": "British female, mid-pitch."
        },
        {
          "label": "Female high",
          "description": "American female, bright and high."
        }
      ]
    },
    {
      "question": "Pick a personality tone:",
      "header": "Tone",
      "multiSelect": false,
      "options": [
        {
          "label": "sarcastic",
          "description": "Makes fun of you — \"Done. You're welcome.\""
        },
        {
          "label": "grumpy",
          "description": "Hates everything — \"Done. Go away.\""
        },
        {
          "label": "enthusiastic",
          "description": "Annoyingly excited — \"WOOHOO! Done!\""
        },
        {
          "label": "dramatic",
          "description": "Over the top epic — \"The quest is complete!\""
        }
      ]
    }
  ]
}
```

Wait for response using AskUserQuestion. If they select "Other" for tone and type a custom description, save it for voice line generation.

Map voice selection to preset name:
- "Male mid-range" → `male_mid`
- "Male deep" → `male_deep`
- "Female mid-range" → `female_mid`
- "Female high" → `female_high`

## Step 4: Ask How Many Variations (only if voice or both)

Use the AskUserQuestion tool:

```json
{
  "questions": [
    {
      "question": "How many voice line variations per hook?",
      "header": "Variations",
      "multiSelect": false,
      "options": [
        {
          "label": "3 (recommended)",
          "description": "Quick to generate, good variety"
        },
        {
          "label": "5",
          "description": "More variety, takes a bit longer"
        },
        {
          "label": "8",
          "description": "Maximum variety, slower generation"
        }
      ]
    }
  ]
}
```

Wait for response using AskUserQuestion. Parse the number from their selection.

## Step 5: Apply Configuration

Say: "Applying your configuration..."

### 5a. Update hooks in settings.json

```bash
python3 -c "
import json, os

settings_path = os.path.expanduser('~/.claude/settings.json')
script = os.path.expanduser('~/.claude/warhorn/scripts/play-sound.sh')

try:
    settings = json.load(open(settings_path))
except:
    settings = {}

if 'hooks' not in settings:
    settings['hooks'] = {}

all_hooks = ['SessionStart','UserPromptSubmit','PreToolUse','PermissionRequest','PostToolUse','PostToolUseFailure','Notification','SubagentStart','SubagentStop','Stop','TeammateIdle','TaskCompleted','PreCompact','SessionEnd']

enabled = [ENABLED_HOOKS_LIST]

for hook in all_hooks:
    entry = {'hooks': [{'type': 'command', 'command': f'{script} {hook}'}]}
    if hook in enabled:
        if hook not in settings['hooks']:
            settings['hooks'][hook] = [entry]
        else:
            has_zz = any(h.get('hooks') and any('warhorn' in (i.get('command','')) for i in h['hooks']) for h in settings['hooks'][hook])
            if not has_zz:
                settings['hooks'][hook].append(entry)
    else:
        if hook in settings['hooks']:
            settings['hooks'][hook] = [h for h in settings['hooks'][hook] if not (h.get('hooks') and any('warhorn' in (i.get('command','')) for i in h['hooks']))]
            if not settings['hooks'][hook]:
                del settings['hooks'][hook]

if not settings['hooks']:
    del settings['hooks']

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')

print(f'Hooks updated: {len(enabled)} enabled, {len(all_hooks) - len(enabled)} disabled')
"
```

Replace `[ENABLED_HOOKS_LIST]` with the user's choices, e.g.: `'Stop', 'PermissionRequest', 'PostToolUseFailure'`

### 5b. Generate voice lines (only if voice or both)

Install edge-tts:
```bash
pip install edge-tts 2>/dev/null || pip3 install edge-tts 2>/dev/null || pip install --user edge-tts
```

**YOU must write the voice lines.** Generate a JSON file with short, punchy lines — **maximum 4 words each**. Write at least N+2 lines per enabled hook (where N is the variation count the user chose), so the generator has enough to pick from randomly.

The lines must match the chosen tone. Examples for "sarcastic" tone:
- Stop: "Done. You're welcome.", "Finished. Hold applause."
- PermissionRequest: "Approve me. Chop chop.", "Permission. Now, boss."
- PostToolUseFailure: "Broke. Shocking.", "Not my fault."

Write the JSON and generate:

```bash
WARHORN_ROOT="$HOME/.claude/warhorn"
cat > "$WARHORN_ROOT/custom_lines.json" << 'LINES_EOF'
{
  "Stop": ["line1", "line2", "line3", ...],
  "PermissionRequest": ["line1", "line2", ...],
  ...
}
LINES_EOF
python3 "$WARHORN_ROOT/scripts/generate_voices.py" \
  --hooks "<comma-separated enabled hooks>" \
  --preset <chosen_preset> \
  --lines-file "$WARHORN_ROOT/custom_lines.json" \
  --count <variation_count>
```

Use the ALREADY INSTALLED generate_voices.py. Do NOT create a new script.

If voice generation fails, tell the user and keep instrumentals.

If voice-only (no instrumentals), remove bundled sounds:
```bash
find "$WARHORN_ROOT/sounds" -maxdepth 2 -type f \( -name "*.wav" -o -name "*.mp3" \) ! -name "voice_*" -delete
```

### 5c. Unmute and test

```bash
rm -f "$HOME/.claude/warhorn/.muted"
"$HOME/.claude/warhorn/scripts/play-sound.sh" Stop
```

### 5d. Summary

Tell the user what was configured and remind them about `/warhorn:mute` and `/warhorn:unmute`.

</process>

<critical_rules>
1. ONE question at a time — never ask multiple questions in same message
2. WAIT for answers — don't proceed until they respond
3. Use AskUserQuestion tool — for every question with predefined options
4. NEVER modify files in ~/.claude/warhorn/scripts/ — only CALL them
5. Always write voice lines yourself as JSON — never use --tone flag, always use --lines-file
6. Voice lines must be maximum 4 words each
7. If edge-tts fails → suggest pip3 install --break-system-packages edge-tts
8. If voice generation fails → keep instrumentals, tell user to retry later
9. If any script errors → tell user to reinstall with npx warhorn, do NOT rewrite scripts
</critical_rules>
