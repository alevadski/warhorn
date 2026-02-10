#!/usr/bin/env node

// Standalone uninstaller — also called by `npx zugzug uninstall`
// Can be run directly: node ~/.claude/zugzug/uninstall.js

const fs = require("fs");
const path = require("path");
const os = require("os");

// ─── Colors ──────────────────────────────────────

const c = {
  green: "\x1b[32m",
  red: "\x1b[31m",
  dim: "\x1b[2m",
  bold: "\x1b[1m",
  reset: "\x1b[0m",
};

// ─── Config ──────────────────────────────────────

const CLAUDE_DIR =
  process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
const ZUGZUG_DIR = path.join(CLAUDE_DIR, "zugzug");
const COMMANDS_DIR = path.join(CLAUDE_DIR, "commands", "zugzug");
const SKILLS_DIR = path.join(CLAUDE_DIR, "skills", "zugzug-talk");
const SETTINGS_FILE = path.join(CLAUDE_DIR, "settings.json");

const HOOKS = [
  "SessionStart",
  "UserPromptSubmit",
  "PreToolUse",
  "PermissionRequest",
  "PostToolUse",
  "PostToolUseFailure",
  "Notification",
  "SubagentStart",
  "SubagentStop",
  "Stop",
  "TeammateIdle",
  "TaskCompleted",
  "PreCompact",
  "SessionEnd",
];

// ─── Helpers ─────────────────────────────────────

const ok = (msg) => console.log(`  ${c.green}✓${c.reset} ${msg}`);

function readJSON(filepath) {
  try {
    return JSON.parse(fs.readFileSync(filepath, "utf8"));
  } catch {
    return {};
  }
}

function writeJSON(filepath, data) {
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2) + "\n");
}

// ─── Banner ──────────────────────────────────────

const banner =
  "\n" +
  c.red +
  "   ███████╗██╗   ██╗ ██████╗ ███████╗██╗   ██╗ ██████╗\n" +
  "   ╚══███╔╝██║   ██║██╔════╝ ╚══███╔╝██║   ██║██╔════╝\n" +
  "     ███╔╝ ██║   ██║██║  ███╗  ███╔╝ ██║   ██║██║  ███╗\n" +
  "    ███╔╝  ██║   ██║██║   ██║ ███╔╝  ██║   ██║██║   ██║\n" +
  "   ███████╗╚██████╔╝╚██████╔╝███████╗╚██████╔╝╚██████╔╝\n" +
  "   ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝" +
  c.reset +
  "\n\n" +
  `   ${c.dim}Uninstalling...${c.reset}\n`;

// ─── Uninstall ───────────────────────────────────

function uninstall() {
  console.log(banner);

  // 1. Remove ~/.claude/zugzug/
  if (fs.existsSync(ZUGZUG_DIR)) {
    fs.rmSync(ZUGZUG_DIR, { recursive: true });
    ok("Removed sounds, scripts & config");
  }

  // 2. Remove ~/.claude/commands/zugzug/
  if (fs.existsSync(COMMANDS_DIR)) {
    fs.rmSync(COMMANDS_DIR, { recursive: true });
    ok("Removed commands");
  }

  // 3. Remove ~/.claude/skills/zugzug-talk/
  if (fs.existsSync(SKILLS_DIR)) {
    fs.rmSync(SKILLS_DIR, { recursive: true });
    ok("Removed skills");
  }

  // 4. Remove hooks from settings.json
  if (fs.existsSync(SETTINGS_FILE)) {
    const settings = readJSON(SETTINGS_FILE);
    if (settings.hooks) {
      let removed = 0;
      for (const hook of HOOKS) {
        if (settings.hooks[hook]) {
          const before = settings.hooks[hook].length;
          settings.hooks[hook] = settings.hooks[hook].filter(
            (h) => !h.hooks?.some((inner) => inner.command?.includes("zugzug"))
          );
          removed += before - settings.hooks[hook].length;
          if (settings.hooks[hook].length === 0) {
            delete settings.hooks[hook];
          }
        }
      }
      if (Object.keys(settings.hooks).length === 0) {
        delete settings.hooks;
      }
      writeJSON(SETTINGS_FILE, settings);
      ok(`Removed ${removed} hooks from settings.json`);
    }
  }

  // 4. Remove personality block from CLAUDE.md
  const claudeMd = path.join(CLAUDE_DIR, "CLAUDE.md");
  if (fs.existsSync(claudeMd)) {
    let content = fs.readFileSync(claudeMd, "utf8");
    const startTag = "<!-- zugzug:personality:start -->";
    const endTag = "<!-- zugzug:personality:end -->";
    const startIdx = content.indexOf(startTag);
    const endIdx = content.indexOf(endTag);
    if (startIdx !== -1 && endIdx !== -1) {
      content =
        content.slice(0, startIdx).trimEnd() +
        "\n" +
        content.slice(endIdx + endTag.length).trimStart();
      fs.writeFileSync(claudeMd, content.trim() + "\n");
      ok("Removed personality from CLAUDE.md");
    }
  }

  console.log(
    `\n  ${c.green}${c.bold}Uninstalled.${c.reset} Goodbye! ${c.dim}...work work${c.reset}\n`
  );
}

uninstall();
