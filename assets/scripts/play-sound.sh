#!/usr/bin/env bash
# ───────────────────────────────────────────────────
# zugzug: play a random sound for a hook event
#
# Usage: play-sound.sh <HookName>
#
# Looks in ~/.claude/zugzug/sounds/<HookName>/ for audio files.
# Picks one at random. Empty folder → silence.
# .muted file → silence. Skips if another sound is playing.
# ───────────────────────────────────────────────────
set -euo pipefail

HOOK_NAME="${1:-}"
if [ -z "$HOOK_NAME" ]; then
  exit 0
fi

ZUGZUG_ROOT="$HOME/.claude/zugzug"

# Check mute
if [ -f "$ZUGZUG_ROOT/.muted" ]; then
  exit 0
fi

# No overlap: skip if another zugzug sound is still playing
LOCK_FILE="$ZUGZUG_ROOT/.playing"
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    exit 0
  fi
  rm -f "$LOCK_FILE"
fi

SOUNDS_DIR="$ZUGZUG_ROOT/sounds/${HOOK_NAME}"

# No folder → silence
if [ ! -d "$SOUNDS_DIR" ]; then
  exit 0
fi

# Collect all sound files
SOUND_FILES=()
while IFS= read -r -d '' f; do
  SOUND_FILES+=("$f")
done < <(find "$SOUNDS_DIR" -maxdepth 1 \( -name '*.wav' -o -name '*.mp3' -o -name '*.aiff' -o -name '*.ogg' \) -print0 2>/dev/null)

if [ ${#SOUND_FILES[@]} -eq 0 ]; then
  exit 0
fi

# Pick a random one
SOUND_FILE="${SOUND_FILES[$((RANDOM % ${#SOUND_FILES[@]}))]}"

# Play it (non-blocking) and track PID for overlap prevention
if [[ "$OSTYPE" == "darwin"* ]]; then
  afplay "$SOUND_FILE" &
  echo $! > "$LOCK_FILE"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if command -v paplay &>/dev/null; then
    paplay "$SOUND_FILE" &
    echo $! > "$LOCK_FILE"
  elif command -v aplay &>/dev/null; then
    aplay -q "$SOUND_FILE" &
    echo $! > "$LOCK_FILE"
  else
    echo "zugzug: no audio player found (install pulseaudio or alsa-utils)" >&2
  fi
else
  echo "zugzug: unsupported OS ($OSTYPE) — see README for supported platforms" >&2
fi

exit 0
