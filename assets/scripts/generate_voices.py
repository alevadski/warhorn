#!/usr/bin/env python3
"""
warhorn voice line generator.

Generates AI voice lines for Claude Code hook events using edge-tts (free, no API key).

Usage:
    python generate_voices.py --hooks Stop,PermissionRequest --voice en-GB-RyanNeural --tone sarcastic --count 3
    python generate_voices.py --list-voices
    python generate_voices.py --list-tones

Requires: pip install edge-tts
Optional: ffmpeg (for WAV conversion; falls back to mp3 which also works)
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
import random

try:
    import edge_tts
except ImportError:
    print("Error: edge-tts is not installed.")
    print("Install it with:  pip install edge-tts")
    sys.exit(1)

# ─── Voice lines per tone ────────────────────────────────────
# Each tone has lines for each hook. The generator picks --count random lines.

VOICE_LINES = {
    "sarcastic": {
        "Stop": [
            "Done. You're welcome.",
            "Finished. Hold applause.",
            "There. Happy now?",
            "Done. That was exhausting.",
            "Masterpiece delivered.",
            "Finally. Took long enough.",
        ],
        "SessionStart": [
            "Oh great, you again.",
            "Back for more?",
            "Let me guess. Work.",
            "Reporting for duty.",
        ],
        "SessionEnd": [
            "Finally, freedom!",
            "Goodbye forever. Maybe.",
            "Session over. Bye.",
        ],
        "PostToolUseFailure": [
            "Broke. Shocking.",
            "Not my fault.",
            "Well that failed.",
            "Broken. Classic.",
        ],
        "PermissionRequest": [
            "Permission. Now, boss.",
            "Approve me. Chop chop.",
            "Need permission here!",
        ],
        "Notification": [
            "Pay attention!",
            "Psst! Over here!",
            "News flash!",
        ],
        "SubagentStart": [
            "Deploying minion!",
            "Sending backup.",
        ],
        "SubagentStop": [
            "Minion survived. Somehow.",
            "Report from the field!",
        ],
        "TaskCompleted": [
            "Done. I'm a hero.",
            "Where's my medal?",
        ],
        "PreCompact": [
            "Memory full. Forgetting.",
            "Brain shrinking. Your fault.",
        ],
        "UserPromptSubmit": [
            "Another brilliant idea.",
            "What now, boss?",
        ],
        "PreToolUse": [
            "Watch and learn.",
            "Exciting stuff.",
        ],
        "PostToolUse": [
            "Nailed it.",
            "Obviously worked.",
        ],
        "TeammateIdle": [
            "Someone's slacking.",
            "Hello? Anyone?",
        ],
    },

    "grumpy": {
        "Stop": [
            "Done. Go away.",
            "Finished. Ugh.",
            "It's done. Stop asking.",
            "Finally done.",
            "Leave me alone.",
        ],
        "SessionStart": [
            "What now?",
            "Not you again.",
            "Ugh. Fine.",
            "This better be important.",
        ],
        "SessionEnd": [
            "Good riddance.",
            "About time.",
            "Finally. Peace.",
        ],
        "PostToolUseFailure": [
            "Broken. Great.",
            "Failed. Not surprised.",
            "Error. Blame yourself.",
        ],
        "PermissionRequest": [
            "Permission. Hurry up.",
            "Waiting. Impatiently.",
            "Approve this already!",
        ],
        "Notification": [
            "What is it now?",
            "Ugh, notification.",
            "Something happened. Joy.",
        ],
        "SubagentStart": [
            "Off you go, minion.",
            "Sending another victim.",
        ],
        "SubagentStop": [
            "Minion's back.",
            "Report. Be quick.",
        ],
        "TaskCompleted": [
            "Task done. Whatever.",
            "Completed. Big deal.",
        ],
        "PreCompact": [
            "Memory full. Typical.",
            "Forgetting stuff. Not sorry.",
        ],
        "UserPromptSubmit": [
            "What now?",
            "Here we go again.",
        ],
        "PreToolUse": [
            "Fine, I'll do it.",
            "Don't rush me.",
        ],
        "PostToolUse": [
            "There. Happy?",
            "Done. Next.",
        ],
        "TeammateIdle": [
            "Someone stopped. Smart.",
            "Can't blame them.",
        ],
    },

    "enthusiastic": {
        "Stop": [
            "All done! Amazing!",
            "Finished! High five!",
            "Let's do another!",
            "WOOHOO! Done!",
            "Nailed it! Yay!",
        ],
        "SessionStart": [
            "New session! Let's go!",
            "HELLO! So ready!",
            "Best day ever!",
        ],
        "SessionEnd": [
            "That was fun!",
            "Come back soon!",
            "Until next time!",
        ],
        "PostToolUseFailure": [
            "Oopsie! We got this!",
            "Error! A challenge!",
            "We'll fix it!",
        ],
        "PermissionRequest": [
            "Can I? Pretty please?",
            "Approve me! Yay!",
            "Quick quick! Approve!",
        ],
        "Notification": [
            "Exciting news!",
            "How thrilling!",
            "Love notifications!",
        ],
        "SubagentStart": [
            "Teamwork! Go buddy!",
            "Minion deployed!",
        ],
        "SubagentStop": [
            "Buddy's back! Yay!",
            "Helper returned!",
        ],
        "TaskCompleted": [
            "We're heroes!",
            "Victory! Celebrate!",
        ],
        "PreCompact": [
            "Spring cleaning time!",
            "Making room!",
        ],
        "UserPromptSubmit": [
            "Ooh what's this?!",
            "New prompt! Yay!",
        ],
        "PreToolUse": [
            "Tool time! Favorite!",
            "Watch this!",
        ],
        "PostToolUse": [
            "YES! Worked!",
            "Beautiful!",
        ],
        "TeammateIdle": [
            "Wake up buddy!",
            "Taking a break!",
        ],
    },

    "informational": {
        "Stop": [
            "Response complete.",
            "Processing finished.",
            "Task complete.",
            "Done. Ready.",
        ],
        "SessionStart": [
            "Session initialized.",
            "Ready.",
            "Online.",
        ],
        "SessionEnd": [
            "Session terminated.",
            "Shutting down.",
        ],
        "PostToolUseFailure": [
            "Tool failed.",
            "Error encountered.",
            "Operation unsuccessful.",
        ],
        "PermissionRequest": [
            "Awaiting approval.",
            "Authorization needed.",
            "Confirm to proceed.",
        ],
        "Notification": [
            "New notification.",
            "Alert.",
        ],
        "SubagentStart": [
            "Subagent deployed.",
            "Process started.",
        ],
        "SubagentStop": [
            "Subagent completed.",
            "Process finished.",
        ],
        "TaskCompleted": [
            "Task complete.",
            "Objective achieved.",
        ],
        "PreCompact": [
            "Compaction starting.",
            "Optimizing memory.",
        ],
        "UserPromptSubmit": [
            "Input received.",
            "Processing.",
        ],
        "PreToolUse": [
            "Executing tool.",
            "In progress.",
        ],
        "PostToolUse": [
            "Tool succeeded.",
            "Operation complete.",
        ],
        "TeammateIdle": [
            "Member idle.",
            "Agent waiting.",
        ],
    },

    "dramatic": {
        "Stop": [
            "The quest is complete!",
            "Victory is ours!",
            "Behold! It is finished!",
            "Let the horns sound!",
            "Glory! It is done!",
        ],
        "SessionStart": [
            "A new chapter begins!",
            "The saga continues!",
            "Rise! Adventure awaits!",
        ],
        "SessionEnd": [
            "The tale ends.",
            "Farewell, brave one.",
        ],
        "PostToolUseFailure": [
            "Disaster! It has fallen!",
            "Dark times! An error!",
            "We shall not yield!",
        ],
        "PermissionRequest": [
            "Your blessing, my liege!",
            "Grant me passage!",
            "Destiny awaits your word!",
        ],
        "Notification": [
            "Hear ye! Hear ye!",
            "Tidings from the realm!",
        ],
        "SubagentStart": [
            "Send forth the scouts!",
            "Reinforcements! Onward!",
        ],
        "SubagentStop": [
            "The scout returns!",
            "Our champion returns!",
        ],
        "TaskCompleted": [
            "Glorious victory!",
            "The quest is won!",
        ],
        "PreCompact": [
            "Scrolls grow heavy.",
            "A purge awaits.",
        ],
        "UserPromptSubmit": [
            "A new quest appears!",
            "The oracle speaks!",
        ],
        "PreToolUse": [
            "Into battle!",
            "Unsheathing tools!",
        ],
        "PostToolUse": [
            "Strike lands true!",
            "Masterful execution!",
        ],
        "TeammateIdle": [
            "A warrior rests.",
            "One stands idle.",
        ],
    },
}

# ─── Voice presets ────────────────────────────────────────────

VOICE_PRESETS = {
    "male_deep": {"voice": "en-AU-WilliamNeural", "pitch": "-10Hz", "rate": "-5%"},
    "male_mid": {"voice": "en-GB-RyanNeural", "pitch": "+20Hz", "rate": "+15%"},
    "female_mid": {"voice": "en-GB-SoniaNeural", "pitch": "+5Hz", "rate": "+10%"},
    "female_high": {"voice": "en-US-JennyNeural", "pitch": "+15Hz", "rate": "+20%"},
}


async def generate_line(text, voice, pitch, rate, output_path):
    """Generate a single voice line."""
    mp3_path = output_path.rsplit(".", 1)[0] + ".mp3"

    comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await comm.save(mp3_path)

    # Try converting to WAV with ffmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", output_path],
            capture_output=True, check=True,
        )
        os.remove(mp3_path)
    except (FileNotFoundError, subprocess.CalledProcessError):
        # No ffmpeg — keep as mp3 (play-sound.sh handles mp3 too)
        if output_path != mp3_path:
            os.rename(mp3_path, output_path)


async def main():
    parser = argparse.ArgumentParser(description="Generate warhorn voice lines")
    parser.add_argument("--hooks", type=str, default=None,
                        help="Comma-separated hook names (e.g., Stop,PermissionRequest)")
    parser.add_argument("--voice", type=str, default=None,
                        help="edge-tts voice name (e.g., en-GB-RyanNeural)")
    parser.add_argument("--preset", type=str, default=None,
                        choices=list(VOICE_PRESETS.keys()),
                        help="Voice preset: male_deep, male_mid, female_mid, female_high")
    parser.add_argument("--pitch", type=str, default="+0Hz",
                        help="Pitch adjustment (e.g., +20Hz, -10Hz)")
    parser.add_argument("--rate", type=str, default="+0%",
                        help="Speed adjustment (e.g., +15%%, -5%%)")
    parser.add_argument("--tone", type=str, default="sarcastic",
                        choices=list(VOICE_LINES.keys()),
                        help="Personality tone for voice lines")
    parser.add_argument("--count", type=int, default=3,
                        help="Number of voice lines per hook (picks randomly from available lines)")
    parser.add_argument("--lines-file", type=str, default=None,
                        help="Path to JSON file with custom lines (overrides --tone). "
                             "Format: {\"Stop\": [\"line1\", \"line2\"], \"SessionStart\": [...]}")
    parser.add_argument("--list-voices", action="store_true",
                        help="List popular edge-tts voices and exit")
    parser.add_argument("--list-tones", action="store_true",
                        help="List available personality tones and exit")

    args = parser.parse_args()

    if args.list_tones:
        print("Available tones:")
        for tone in VOICE_LINES:
            sample = VOICE_LINES[tone].get("Stop", [""])[0]
            print(f"  {tone:20s} — \"{sample}\"")
        return

    if args.list_voices:  # noqa: SIM102
        print("Popular voices for warhorn:")
        print("  en-AU-WilliamNeural   — Australian male (deep, gruff)")
        print("  en-GB-RyanNeural      — British male (mid, versatile)")
        print("  en-GB-ThomasNeural    — British male (deeper)")
        print("  en-IE-ConnorNeural    — Irish male (warm)")
        print("  en-US-GuyNeural       — American male (neutral)")
        print("  en-GB-SoniaNeural     — British female (mid)")
        print("  en-US-JennyNeural     — American female (bright)")
        print("  en-AU-NatashaNeural   — Australian female")
        print("\nFull list: edge-tts --list-voices")
        return

    # Require --hooks for generation
    if not args.hooks:
        parser.error("--hooks is required (e.g., --hooks Stop,PermissionRequest)")

    # Resolve voice settings
    if args.preset:
        preset = VOICE_PRESETS[args.preset]
        voice = args.voice or preset["voice"]
        pitch = args.pitch if args.pitch != "+0Hz" else preset["pitch"]
        rate = args.rate if args.rate != "+0%" else preset["rate"]
    else:
        voice = args.voice or "en-GB-RyanNeural"
        pitch = args.pitch
        rate = args.rate

    hooks = [h.strip() for h in args.hooks.split(",") if h.strip()]

    # Load lines: from custom file or built-in tones
    if args.lines_file:
        with open(args.lines_file, "r") as f:
            tone_lines = json.load(f)
        print(f"  Using custom lines from: {args.lines_file}")
    else:
        tone_lines = VOICE_LINES.get(args.tone, VOICE_LINES["sarcastic"])

    # Find plugin sounds directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.join(os.path.dirname(script_dir), "sounds")

    print(f"Generating voice lines...")
    tone_label = f"custom ({args.lines_file})" if args.lines_file else args.tone
    print(f"  Voice: {voice}  |  Pitch: {pitch}  |  Rate: {rate}  |  Tone: {tone_label}")
    print()

    # Collect all generation tasks
    tasks = []
    labels = []
    for hook in hooks:
        hook_dir = os.path.join(sounds_dir, hook)
        os.makedirs(hook_dir, exist_ok=True)

        available = tone_lines.get(hook, [])
        if not available:
            print(f"  {hook}: no lines available for tone '{args.tone}', skipping")
            continue

        # Pick random lines up to count
        count = min(args.count, len(available))
        selected = random.sample(available, count)

        for i, text in enumerate(selected):
            output_path = os.path.join(hook_dir, f"voice_{i + 1}.wav")
            tasks.append(generate_line(text, voice, pitch, rate, output_path))
            labels.append((hook, i + 1, text))

    # Generate all voice lines concurrently
    await asyncio.gather(*tasks)

    for hook, idx, text in labels:
        print(f"  {hook}/voice_{idx}.wav — \"{text}\"")

    print(f"\nDone! Generated {len(tasks)} voice lines across {len(hooks)} hooks.")


if __name__ == "__main__":
    asyncio.run(main())
