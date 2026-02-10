#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const os = require("os");

// ─── Colors ──────────────────────────────────────

const c = {
  green: "\x1b[32m",
  cyan: "\x1b[36m",
  dim: "\x1b[2m",
  bold: "\x1b[1m",
  reset: "\x1b[0m",
};

// ─── Config ──────────────────────────────────────

const pkg = require("../package.json");

const CLAUDE_DIR =
  process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
const WARHORN_DIR = path.join(CLAUDE_DIR, "warhorn");
const COMMANDS_DIR = path.join(CLAUDE_DIR, "commands", "warhorn");
const SETTINGS_FILE = path.join(CLAUDE_DIR, "settings.json");
const ASSETS_DIR = path.join(__dirname, "..", "assets");

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

// ─── Banner ──────────────────────────────────────

const banner =
  "\n" +
  c.green +
  "   ██╗    ██╗ █████╗ ██████╗ ██╗  ██╗ ██████╗ ██████╗ ███╗   ██╗\n" +
  "   ██║    ██║██╔══██╗██╔══██╗██║  ██║██╔═══██╗██╔══██╗████╗  ██║\n" +
  "   ██║ █╗ ██║███████║██████╔╝███████║██║   ██║██████╔╝██╔██╗ ██║\n" +
  "   ██║███╗██║██╔══██║██╔══██╗██╔══██║██║   ██║██╔══██╗██║╚██╗██║\n" +
  "   ╚███╔███╔╝██║  ██║██║  ██║██║  ██║╚██████╔╝██║  ██║██║ ╚████║\n" +
  "    ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝" +
  c.reset + "\n" +
  `${c.dim}${`v${pkg.version}`.padStart(64)}${c.reset}\n`;

// ─── Helpers ─────────────────────────────────────

const ok = (msg) => console.log(`  ${c.green}✓${c.reset} ${msg}`);
const info = (msg) => console.log(`  ${c.dim}${msg}${c.reset}`);

function copyDirSync(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

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

function tildePath(p) {
  return p.replace(os.homedir(), "~");
}

// ─── Install ─────────────────────────────────────

function install() {
  console.log(banner);

  const installDir = tildePath(CLAUDE_DIR);
  info(`Installing to ${installDir}\n`);

  // 1. Sounds, scripts & config
  copyDirSync(path.join(ASSETS_DIR, "sounds"), path.join(WARHORN_DIR, "sounds"));
  copyDirSync(path.join(ASSETS_DIR, "scripts"), path.join(WARHORN_DIR, "scripts"));
  fs.chmodSync(path.join(WARHORN_DIR, "scripts", "play-sound.sh"), 0o755);

  const soundCount = fs
    .readdirSync(path.join(WARHORN_DIR, "sounds"), { recursive: true })
    .filter((f) => f.endsWith(".wav")).length;

  ok(`Installed ${soundCount} sounds & scripts`);

  // 2. Commands
  copyDirSync(path.join(ASSETS_DIR, "commands", "warhorn"), COMMANDS_DIR);
  ok(`Installed commands ${c.dim}(/warhorn:setup, /warhorn:mute, /warhorn:unmute)${c.reset}`);

  // 3. Hooks
  fs.mkdirSync(CLAUDE_DIR, { recursive: true });
  const settings = readJSON(SETTINGS_FILE);
  if (!settings.hooks) settings.hooks = {};

  const scriptRef = path.join(WARHORN_DIR, "scripts", "play-sound.sh");
  let hooksAdded = 0;

  for (const hook of HOOKS) {
    const hookEntry = {
      hooks: [{ type: "command", command: `${scriptRef} ${hook}` }],
    };

    if (!settings.hooks[hook]) {
      settings.hooks[hook] = [hookEntry];
      hooksAdded++;
    } else {
      const hasWarhorn = settings.hooks[hook].some((h) =>
        h.hooks?.some((inner) => inner.command?.includes("warhorn"))
      );
      if (!hasWarhorn) {
        settings.hooks[hook].push(hookEntry);
        hooksAdded++;
      }
    }
  }

  writeJSON(SETTINGS_FILE, settings);
  ok(`Registered ${hooksAdded} hooks in settings.json`);

  // 4. Done!
  console.log(
    `\n  ${c.green}Congrats, your Claude Code just got voice!${c.reset}`
  );
  console.log(
    `  Open Claude Code and run ${c.cyan}/warhorn:setup${c.reset}\n`
  );
  console.log(`  ${c.bold}Commands:${c.reset}`);
  console.log(
    `    ${c.cyan}/warhorn:setup${c.reset}     Interactive setup wizard`
  );
  console.log(
    `    ${c.cyan}/warhorn:mute${c.reset}      Silence all sounds`
  );
  console.log(
    `    ${c.cyan}/warhorn:unmute${c.reset}    Re-enable everything`
  );
  console.log(
    `\n  ${c.dim}npx warhorn uninstall — cleanly remove everything${c.reset}\n`
  );
}

// ─── CLI ─────────────────────────────────────────

const command = process.argv[2];

if (command === "uninstall" || command === "remove") {
  require("./uninstall.js");
} else if (command === "help" || command === "--help" || command === "-h") {
  console.log(banner);
  console.log(`  ${c.bold}Usage:${c.reset}`);
  console.log(`    ${c.cyan}npx warhorn${c.reset}            Install warhorn`);
  console.log(
    `    ${c.cyan}npx warhorn uninstall${c.reset}  Remove everything cleanly`
  );
  console.log(`    ${c.cyan}npx warhorn help${c.reset}       Show this message\n`);
} else {
  install();
}
