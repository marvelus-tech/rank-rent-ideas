#!/usr/bin/env node

const { program } = require('commander');
const SignupAgent = require('./signup-agent');

program
  .name('signup-agent')
  .description('Automated business directory signup agent')
  .version('1.0.0');

program
  .option('-d, --directory <name>', 'Target directory name')
  .option('-e, --entity <id>', 'Entity ID to use (e.g., marvelus, nolostsales)')
  .option('-l, --list', 'List available directories and entities')
  .option('--all', 'Sign up to all directories')
  .option('--headless', 'Run in headless mode (no browser window)')
  .parse();

const options = program.opts();

async function main() {
  const agent = new SignupAgent();
  
  // Initialize with entity if provided
  await agent.init(options.entity);

  if (options.list) {
    console.log('Available entities:');
    const entities = await agent.listEntities();
    for (const entity of entities) {
      const status = entity.active ? '✅' : '❌';
      console.log(`  ${status} ${entity.id} — ${entity.name}`);
    }
    console.log('\nAvailable directories:');
    for (const dir of agent.directories) {
      console.log(`  ${dir.name} (Priority: ${dir.priority})`);
    }
    return;
  }

  if (!options.directory && !options.all) {
    console.log('Use --directory <name> or --all');
    console.log('Use --list to see available directories and entities');
    console.log('Use --entity <id> to specify which business to sign up');
    return;
  }

  const targetDirs = options.all 
    ? agent.directories.map(d => d.name)
    : [options.directory];

  await agent.launchBrowser();

  for (const dirName of targetDirs) {
    console.log(`\n🚀 Starting signup for: ${dirName} (${agent.currentEntity?.name})`);
    const success = await agent.signupToDirectory(dirName);
    
    if (success) {
      console.log(`✅ ${dirName}: SUCCESS`);
    } else {
      console.log(`❌ ${dirName}: FAILED`);
    }
    
    // Wait between signups to avoid rate limiting
    if (targetDirs.length > 1) {
      console.log('⏳ Waiting 30 seconds before next signup...');
      await new Promise(r => setTimeout(r, 30000));
    }
  }

  await agent.close();
  console.log('\n🏁 All signups complete!');
  console.log(`📋 Entity: ${agent.currentEntity?.name}`);
  console.log('📁 Credentials saved to: storage/credentials.json');
  console.log('📊 Results saved to: logs/signup-results.json');
}

main().catch(console.error);
