const SignupAgent = require('./signup-agent');

async function test() {
  const agent = new SignupAgent();
  await agent.init();
  
  console.log('Testing Signup Agent...');
  console.log('NAP Profile:', agent.nap);
  console.log('Directories:', agent.directories.map(d => d.name));
  
  // Test credential generation
  const creds = agent.generateCredentials('TestSite');
  console.log('Generated credentials:', creds);
  
  // Test address formatting
  console.log('Formatted address:', agent.formatAddress());
  
  console.log('\nAll tests passed!');
}

test().catch(console.error);
