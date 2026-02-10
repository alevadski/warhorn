# zugzug

Sound notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Chimes, alerts, and AI voice lines — your choice.

Never miss the end of a long task, a permission request, or a failed tool call again.

## Install

```bash
npx zugzug
```

That's it. Open Claude Code and run `/zugzug:setup` to pick your hooks, sounds, and voice.

## Uninstall

```bash
npx zugzug uninstall
```

## Commands

| Command | What it does |
|---------|-------------|
| `/zugzug:setup` | Interactive setup — pick hooks, sound type, voice character |
| `/zugzug:mute` | Mute all sounds |
| `/zugzug:unmute` | Unmute sounds |

## How it works

Two sound modes, set via `/zugzug:setup`:

- **Instrumental only** — bundled chimes and pings. Works immediately, no setup needed.
- **AI voice lines** — character voice via [edge-tts](https://github.com/rany2/edge-tts) (free Microsoft TTS). Needs `pip install edge-tts` + internet to generate.

You can also use **both** — instrumentals + voice lines mixed randomly per hook.

```
~/.claude/zugzug/
├── sounds/
│   ├── Stop/               ← random .wav plays when Claude finishes
│   │   ├── chime.wav
│   │   └── success.wav
│   ├── PostToolUseFailure/  ← plays when a tool fails
│   ├── PermissionRequest/   ← plays when Claude needs approval
│   └── ...                  ← 14 hook folders total
└── scripts/
    ├── play-sound.sh        ← picks random file, plays it
    └── generate_voices.py   ← generate WAVs via edge-tts
```

## Voice lines

The `/zugzug:setup` wizard lets you pick a voice and personality tone. Claude Code writes short, punchy voice lines for each hook and generates them as WAV files using [edge-tts](https://github.com/rany2/edge-tts) (free Microsoft TTS).

You can also generate voice lines manually:

```bash
pip install edge-tts

python3 ~/.claude/zugzug/scripts/generate_voices.py \
  --hooks Stop,PermissionRequest,PostToolUseFailure \
  --preset male_mid --tone sarcastic --count 3
```

### Voice presets

| Preset | Voice |
|--------|-------|
| `male_deep` | Australian male, deep and gruff |
| `male_mid` | British male, mid-pitch (default) |
| `female_mid` | British female, mid-pitch |
| `female_high` | American female, bright and high |

### Personality tones

| Tone | Vibe | Example (Stop hook) |
|------|------|-------------------|
| **sarcastic** | Makes fun of you | "Done. You're welcome." |
| **grumpy** | Hates everything | "Done. Go away." |
| **enthusiastic** | Annoyingly excited | "WOOHOO! Done!" |
| **informational** | Just the facts | "Response complete." |
| **dramatic** | Over the top epic | "The quest is complete!" |

You can also describe a **custom** personality during `/zugzug:setup` and Claude will write voice lines for it.

## Supported hooks

| Hook | Default sound | When it fires |
|------|:---:|-------------|
| `Stop` | chime, success, bell | Claude finishes responding |
| `SessionStart` | boot, ready | Session begins |
| `SessionEnd` | shutdown | Session ends |
| `PostToolUseFailure` | buzz, sad, wonk | Tool fails |
| `PermissionRequest` | alert, doorbell | Claude needs approval |
| `Notification` | ping, bubble | Claude sends notification |
| `SubagentStart` | spawn | Subagent spawns |
| `SubagentStop` | return | Subagent finishes |
| `TaskCompleted` | victory | Task marked complete |
| `PreCompact` | warning | Context compaction starting |
| `UserPromptSubmit` | tick, tap | You submit a prompt |
| `PreToolUse` | _(empty)_ | Before every tool call |
| `PostToolUse` | _(empty)_ | After every tool call |
| `TeammateIdle` | _(empty)_ | Team member idles |

## Add your own sounds

Drop any audio file into a hook folder:

```bash
cp ~/my-sound.wav ~/.claude/zugzug/sounds/Stop/
```

Supported formats: `.wav` (recommended), `.mp3`, `.aiff`, `.ogg`

## Requirements

- **macOS**: Works out of the box (`afplay` is built in)
- **Linux**: Needs `pulseaudio` or `alsa-utils` for sounds
- **Voice lines** (optional): `pip install edge-tts` + internet

## What `npx zugzug` does

1. Copies sounds and scripts to `~/.claude/zugzug/`
2. Copies commands to `~/.claude/commands/zugzug/`
3. Adds hooks to `~/.claude/settings.json`

`npx zugzug uninstall` cleanly reverses all three steps.

## License

MIT
