#!/usr/bin/env node
/**
 * R&D Debate Orchestrator v3 — Prompt Generator
 * 
 * This script DOES NOT call models directly.
 * Instead, it generates 3 structured prompt files and saves them.
 * The cron job or parent agent then feeds these prompts to the actual models.
 * 
 * Agents:
 *   1. 🔬 Research Analyst (Flash) — deep-dive research
 *   2. ⚙️ Systems Builder (Codex) — code/automation proposals  
 *   3. 🎯 Strategic Director (Kimi) — synthesis + bold recommendations
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const RND_DIR = __dirname;
const MEMORY_DIR = path.join(ROOT, 'memory');
const PROMPTS_DIR = path.join(RND_DIR, 'prompts');
const AGENTS_FILE = path.join(RND_DIR, 'agents.json');
const DAILY_DIR = path.join(ROOT, '..', 'Obsidian', 'Penelopi', 'Daily');

function nowLocal() {
  return new Date();
}

function formatDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function formatDateTime(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${day}-${hh}-${mm}`;
}

function safeRead(file) {
  if (!fs.existsSync(file)) return '';
  return fs.readFileSync(file, 'utf8');
}

function getLastNDates(n) {
  const out = [];
  const base = nowLocal();
  for (let i = 0; i < n; i++) {
    const d = new Date(base);
    d.setDate(d.getDate() - i);
    out.push(formatDate(d));
  }
  return out;
}

function loadRecentMemory(days = 3) {
  const dates = getLastNDates(days);
  return dates.map((date) => {
    const obsFile = path.join(DAILY_DIR, `${date}.md`);
    const oldFile = path.join(MEMORY_DIR, `${date}.md`);
    const content = safeRead(obsFile) || safeRead(oldFile) || '_No memory file found_';
    return { date, content };
  });
}

function getGitCommits(limit = 8) {
  try {
    const { execSync } = require('child_process');
    return execSync(`git -C "${ROOT}" log --oneline -n ${limit}`, { encoding: 'utf8' }).trim();
  } catch {
    return 'Git history unavailable';
  }
}

function loadContextPack() {
  return {
    generatedAt: new Date().toISOString(),
    recentMemory: loadRecentMemory(3),
    recentCommits: getGitCommits(8),
    today: formatDate(nowLocal()),
  };
}

function buildPrompt({ round, agent, context }) {
  const memoryContext = context.recentMemory
    .map((m) => `## ${m.date}\n${m.content}`)
    .join('\n\n');

  const tasks = {
    research: `SCOUT THE LANDSCAPE. Research ONE of the following (pick what's most relevant today):
- A competitor or alternative to Marvelus.cc / Nolostsales.cc
- A new AI tool, API, or platform that could accelerate lead generation
- A Solana project or DeFi mechanic worth tracking
- A UX/design trend that could improve conversion
- A market shift or regulation affecting AI-for-SMBs

Return: What you found, why it matters, links/sources, confidence (0-100).`,

    build: `BUILD SOMETHING. Based on the research round above, propose:
- A script, automation, or integration that exploits the opportunity
- OR a fix for a known pain point (Peekaboo TCC, lead scoring, etc.)
- OR a data pipeline that feeds the lead gen system

Write actual code or detailed pseudocode. Focus on speed — what can be tested in 1 day?`,

    direct: `MAKE THE CALL. Synthesize research + build output into a strategic recommendation:
- ONE bold move (high risk, high reward)
- ONE safe move (low risk, incremental gain)
- ONE experiment (testable in 48 hours)

For each: what, why, how, success metric, kill criteria. Challenge weak assumptions. Be specific enough to act on today.`
  };

  return [
    `# R&D Department — ${round.toUpperCase()} Round`,
    ``,
    `You are ${agent.name} (${agent.model}).`,
    `Role: ${agent.role}`,
    `Personality: ${agent.personality}`,
    ``,
    `## Mission`,
    `Produce high-signal output for Okeito's R&D department.`,
    `Today's date: ${context.today}`,
    ``,
    `## Recent Context (last 3 days)`,
    memoryContext,
    ``,
    `## Recent Git Commits`,
    context.recentCommits,
    ``,
    `## Your Task`,
    tasks[round] || 'Produce output relevant to your role.',
    ``,
    `## Output Rules`,
    `- Be specific and actionable.`,
    `- No filler, no hedging, no "it depends."`,
    `- If you need web search, use it.`,
    `- Return markdown with clear sections.`,
  ].join('\n');
}

function main() {
  const agentsConfig = JSON.parse(fs.readFileSync(AGENTS_FILE, 'utf8'));
  fs.mkdirSync(PROMPTS_DIR, { recursive: true });

  const context = loadContextPack();
  const timestamp = formatDateTime(nowLocal());
  
  const rounds = [
    { key: 'research', agentId: 'research-analyst' },
    { key: 'build', agentId: 'systems-builder' },
    { key: 'direct', agentId: 'strategic-director' },
  ];

  const manifest = {
    timestamp,
    generatedAt: new Date().toISOString(),
    rounds: [],
  };

  for (const round of rounds) {
    const agent = agentsConfig.agents.find((a) => a.id === round.agentId);
    if (!agent) throw new Error(`Missing agent for role: ${round.agentId}`);

    const prompt = buildPrompt({ round: round.key, agent, context });
    const promptFile = path.join(PROMPTS_DIR, `${timestamp}-${round.key}.md`);
    
    fs.writeFileSync(promptFile, prompt);
    
    manifest.rounds.push({
      round: round.key,
      agentId: agent.id,
      agentName: agent.name,
      model: agent.model,
      promptFile,
    });
    
    console.log(`Generated ${round.key} prompt: ${promptFile}`);
  }

  const manifestFile = path.join(PROMPTS_DIR, `${timestamp}-manifest.json`);
  fs.writeFileSync(manifestFile, JSON.stringify(manifest, null, 2));
  
  console.log(`\n✅ Generated ${rounds.length} prompts`);
  console.log(`Manifest: ${manifestFile}`);
  console.log(`\nNext step: Feed each prompt to its assigned model`);
  console.log(`Example: cat ${manifest.rounds[0].promptFile} | <model-runner>`);
}

main();
