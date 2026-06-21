#!/usr/bin/env node
/**
 * Scan Obsidian Ideas vault and generate projects JSON for Mission Control
 * Supports: milestones (auto-calculated), manual progress override, stage defaults
 * Run: node scan-ideas.js
 */

const fs = require('fs');
const path = require('path');

const IDEAS_DIR = '/Users/oktos/Obsidian/Ideas';
const OUTPUT_FILE = '/Users/oktos/.openclaw/workspace/mission-control/projects.json';

// Stage priority for sorting
const STAGE_PRIORITY = {
  'building': 1,
  'validating': 2,
  'inbox': 3,
  'launched': 4,
  'archived': 5
};

// Default milestone template
const DEFAULT_MILESTONES = [
  '[ ] Brainstorm / Research',
  '[ ] Build / MVP',
  '[ ] Test with users',
  '[ ] Launch'
];

function parseFrontmatter(content) {
  const fm = {};
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  
  if (match) {
    const lines = match[1].split('\n');
    let inMilestones = false;
    
    for (const line of lines) {
      // Check for milestones array start
      if (line.trim() === 'milestones:') {
        fm.milestones = [];
        inMilestones = true;
        continue;
      }
      
      // Parse milestone items
      if (inMilestones) {
        if (line.startsWith('  - ')) {
          fm.milestones.push(line.slice(4).trim());
          continue;
        } else if (line.trim() === '' || line.trim().startsWith('-')) {
          inMilestones = false;
        } else {
          inMilestones = false;
        }
      }
      
      // Parse regular key: value
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0 && !line.startsWith('  -')) {
        const key = line.slice(0, colonIndex).trim();
        const value = line.slice(colonIndex + 1).trim().replace(/^["']|["']$/g, '');
        if (key !== 'milestones') {
          fm[key] = value;
        }
      }
    }
  }
  
  return fm;
}

function calculateProgress(fm, stage) {
  // Priority 1: Manual progress override
  if (fm.progress) {
    return parseInt(fm.progress);
  }
  
  // Priority 2: Calculate from milestones
  if (fm.milestones && fm.milestones.length > 0) {
    const total = fm.milestones.length;
    const completed = fm.milestones.filter(m => m.startsWith('[x]') || m.startsWith('[X]')).length;
    return Math.round((completed / total) * 100);
  }
  
  // Priority 3: Stage-based defaults
  const stageLower = stage.toLowerCase();
  if (stageLower === 'building') return 50;
  if (stageLower === 'validating') return 25;
  if (stageLower === 'launched') return 100;
  if (stageLower === 'archived') return 100;
  return 5; // inbox default
}

function getMilestones(fm) {
  // Return custom milestones if defined, otherwise default template
  if (fm.milestones && fm.milestones.length > 0) {
    return fm.milestones;
  }
  return DEFAULT_MILESTONES;
}

function scanIdeas() {
  const projects = [];
  const stages = ['0-Inbox', '1-Validating', '2-Building', '3-Launched', '4-Archived'];
  
  for (const stageDir of stages) {
    const dirPath = path.join(IDEAS_DIR, stageDir);
    
    if (!fs.existsSync(dirPath)) continue;
    
    const files = fs.readdirSync(dirPath).filter(f => f.endsWith('.md'));
    
    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const content = fs.readFileSync(filePath, 'utf8');
      const fm = parseFrontmatter(content);
      
      // Skip templates and READMEs
      if (file.includes('TEMPLATE') || file.includes('README') || file.includes('SUMMARY')) continue;
      
      const projectName = path.basename(file, '.md');
      
      // Map folder to stage
      let stage = 'Inbox';
      if (stageDir === '1-Validating') stage = 'Validating';
      if (stageDir === '2-Building') stage = 'Building';
      if (stageDir === '3-Launched') stage = 'Launched';
      if (stageDir === '4-Archived') stage = 'Archived';
      
      // Use frontmatter status if available
      if (fm.status) {
        stage = fm.status.charAt(0).toUpperCase() + fm.status.slice(1);
      }
      
      const progress = calculateProgress(fm, stage);
      const milestones = getMilestones(fm);
      
      projects.push({
        name: projectName,
        stage: stage,
        progress: progress,
        milestones: milestones,
        hasManualProgress: !!fm.progress
      });
    }
  }
  
  // Sort by stage priority
  projects.sort((a, b) => {
    const priorityA = STAGE_PRIORITY[a.stage.toLowerCase()] || 99;
    const priorityB = STAGE_PRIORITY[b.stage.toLowerCase()] || 99;
    return priorityA - priorityB;
  });
  
  return projects;
}

function main() {
  console.log('🔍 Scanning Obsidian Ideas vault...\n');
  
  const projects = scanIdeas();
  
  const output = {
    generated: new Date().toISOString(),
    count: projects.length,
    projects: projects
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  
  console.log(`✅ Generated projects.json with ${projects.length} projects\n`);
  
  // Log summary
  for (const p of projects) {
    const milestoneInfo = p.milestones.length > 4 ? ` (+${p.milestones.length - 4} more)` : '';
    const manualFlag = p.hasManualProgress ? ' [MANUAL]' : '';
    console.log(`  • ${p.name}`);
    console.log(`    → ${p.stage} | ${p.progress}%${manualFlag}`);
    console.log(`    → ${p.milestones.filter(m => m.startsWith('[x]')).length}/${p.milestones.length} milestones${milestoneInfo}`);
    console.log('');
  }
  
  console.log('📁 Output:', OUTPUT_FILE);
}

main();
