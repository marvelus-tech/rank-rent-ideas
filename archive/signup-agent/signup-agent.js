const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');
const winston = require('winston');
const notifier = require('node-notifier');
const axios = require('axios');

// Logger setup
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
});

class SignupAgent {
  constructor() {
    this.configDir = path.join(__dirname, 'config');
    this.storageDir = path.join(__dirname, 'storage');
    this.logsDir = path.join(__dirname, 'logs');
    this.stateFile = path.join(this.storageDir, 'agent-state.json');
    this.credsFile = path.join(this.storageDir, 'credentials.json');
    this.obsidianCredsFile = path.join(process.env.HOME, 'Obsidian', 'Penelopi', 'Credentials', 'directory-signups.md');
    this.resultsFile = path.join(this.logsDir, 'signup-results.json');
    this.entitiesFile = path.join(this.configDir, 'entities.json');
    this.dirsFile = path.join(this.configDir, 'directories.json');
    this.browser = null;
    this.context = null;
    this.page = null;
    this.currentEntity = null;
  }

  async init(entityId = null) {
    await this.ensureDirs();
    
    // Load entities config
    const entities = JSON.parse(await fs.readFile(this.entitiesFile, 'utf8'));
    
    if (entityId) {
      // Find specific entity
      const entity = entities.entities.find(e => e.id === entityId);
      if (!entity) {
        throw new Error(`Entity ${entityId} not found. Available: ${entities.entities.map(e => e.id).join(', ')}`);
      }
      this.currentEntity = entity;
      const napFile = path.join(this.configDir, `nap-${entityId}.json`);
      this.nap = JSON.parse(await fs.readFile(napFile, 'utf8'));
    } else {
      // Default to first active entity
      const defaultEntity = entities.entities.find(e => e.active);
      if (!defaultEntity) {
        throw new Error('No active entity found in config');
      }
      this.currentEntity = defaultEntity;
      const napFile = path.join(this.configDir, `nap-${defaultEntity.id}.json`);
      this.nap = JSON.parse(await fs.readFile(napFile, 'utf8'));
    }
    
    this.directories = JSON.parse(await fs.readFile(this.dirsFile, 'utf8')).directories;
  }

  async listEntities() {
    const entities = JSON.parse(await fs.readFile(this.entitiesFile, 'utf8'));
    return entities.entities;
  }

  async ensureDirs() {
    for (const dir of [this.configDir, this.storageDir, this.logsDir]) {
      await fs.mkdir(dir, { recursive: true });
    }
  }

  async launchBrowser() {
    const bravePath = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';
    this.browser = await chromium.launch({
      headless: false,
      executablePath: bravePath,
      args: ['--disable-blink-features=AutomationControlled']
    });
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    this.page = await this.context.newPage();
    await this.page.evaluate(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });
    logger.info('Browser launched with Brave');
  }

  generateCredentials(siteName) {
    const adjectives = ['Quick', 'Bright', 'Smart', 'Swift', 'Bold', 'Prime', 'Core', 'Peak'];
    const nouns = ['Wave', 'Spark', 'Pulse', 'Edge', 'Hub', 'Nest', 'Base', 'Link'];
    const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const noun = nouns[Math.floor(Math.random() * nouns.length)];
    const num = Math.floor(Math.random() * 9000) + 1000;
    const username = `${adj}${noun}${num}`.toLowerCase();
    const password = this.generateStrongPassword();
    return { username, password, email: this.nap.email };
  }

  generateStrongPassword() {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let pwd = '';
    for (let i = 0; i < 16; i++) {
      pwd += chars[Math.floor(Math.random() * chars.length)];
    }
    return pwd;
  }

  async notifyCaptcha(siteName, pageUrl) {
    const message = `🚨 CAPTCHA DETECTED on ${siteName}\nURL: ${pageUrl}\n\nPlease solve the CAPTCHA in the browser window. The agent is paused and waiting.`;
    
    // Desktop notification
    notifier.notify({
      title: 'Signup Agent - CAPTCHA Required',
      message: `Solve CAPTCHA on ${siteName}`,
      sound: true,
      wait: true
    });

    // Telegram notification if configured
    const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN;
    const telegramChatId = process.env.TELEGRAM_CHAT_ID;
    if (telegramBotToken && telegramChatId) {
      try {
        await axios.post(`https://api.telegram.org/bot${telegramBotToken}/sendMessage`, {
          chat_id: telegramChatId,
          text: message
        });
      } catch (e) {
        logger.error('Telegram notification failed:', e.message);
      }
    }

    logger.info(`CAPTCHA notification sent for ${siteName}`);
  }

  async detectCaptcha() {
    const captchaSelectors = [
      '.g-recaptcha',
      '[data-sitekey]',
      '.h-captcha',
      'iframe[src*="recaptcha"]',
      'iframe[src*="hcaptcha"]',
      '#captcha',
      '.captcha',
      'img[src*="captcha"]'
    ];
    
    for (const selector of captchaSelectors) {
      const element = await this.page.$(selector);
      if (element) {
        const isVisible = await element.isVisible().catch(() => false);
        if (isVisible) return selector;
      }
    }
    return null;
  }

  async waitForCaptchaSolved() {
    logger.info('Waiting for CAPTCHA to be solved...');
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes (5 second intervals)
    
    while (attempts < maxAttempts) {
      await new Promise(r => setTimeout(r, 5000));
      const stillThere = await this.detectCaptcha();
      if (!stillThere) {
        logger.info('CAPTCHA appears to be solved!');
        return true;
      }
      attempts++;
    }
    
    logger.error('CAPTCHA timeout - user did not solve within 10 minutes');
    return false;
  }

  async saveState(directoryName, step, data = {}) {
    const state = {
      directory: directoryName,
      currentStep: step,
      timestamp: new Date().toISOString(),
      data
    };
    await fs.writeFile(this.stateFile, JSON.stringify(state, null, 2));
  }

  async loadState() {
    try {
      const data = await fs.readFile(this.stateFile, 'utf8');
      return JSON.parse(data);
    } catch {
      return null;
    }
  }

  async saveCredentials(directoryName, credentials) {
    // Save to local JSON with entity context
    let creds = { credentials: [] };
    try {
      const data = await fs.readFile(this.credsFile, 'utf8');
      creds = JSON.parse(data);
    } catch {}
    
    creds.credentials.push({
      directory: directoryName,
      entity: this.currentEntity?.id || 'unknown',
      entityName: this.currentEntity?.name || 'Unknown',
      ...credentials,
      createdAt: new Date().toISOString()
    });
    
    await fs.writeFile(this.credsFile, JSON.stringify(creds, null, 2));
    
    // Also save to Obsidian with entity info
    await this.saveToObsidian(directoryName, credentials, this.nap, this.currentEntity);
    
    logger.info(`Credentials saved for ${directoryName} (${this.currentEntity?.name})`);
  }

  async saveToObsidian(directoryName, credentials, napProfile = null, entity = null, verificationStatus = 'pending') {
    try {
      const obsidianDir = path.join(process.env.HOME, 'Obsidian', 'Penelopi', 'Credentials');
      await fs.mkdir(obsidianDir, { recursive: true });
      
      const obsidianFile = path.join(obsidianDir, 'directory-signups.md');
      
      let content = '';
      try {
        content = await fs.readFile(obsidianFile, 'utf8');
      } catch {
        content = '# Directory Signup Credentials\n\n> Auto-generated by signup-agent\n\n';
      }
      
      // Include business name and entity info
      const businessName = napProfile ? napProfile.name : 'Unknown Business';
      const entityName = entity ? entity.name : 'Unknown Entity';
      
      const entry = `\n## ${directoryName} — ${businessName}\n\n- **Entity:** ${entityName}\n- **Username:** ${credentials.username}\n- **Password:** ${credentials.password}\n- **Email:** ${credentials.email}\n- **Business:** ${businessName}\n- **Verification Status:** ${verificationStatus}\n- **Created:** ${new Date().toISOString()}\n\n`;
      
      content += entry;
      await fs.writeFile(obsidianFile, content);
      logger.info(`Credentials saved to Obsidian: ${obsidianFile}`);
    } catch (e) {
      logger.warn(`Could not save to Obsidian: ${e.message}`);
    }
  }

  async checkVerificationNeeded(directoryName, credentials) {
    // Common verification indicators on the page after signup
    const verificationIndicators = [
      'verify your email',
      'confirmation email',
      'verification email',
      'check your inbox',
      'confirm your account',
      'email sent',
      'verify email',
      'activate your account'
    ];
    
    const pageText = await this.page.textContent('body').catch(() => '');
    const needsVerification = verificationIndicators.some(indicator => 
      pageText.toLowerCase().includes(indicator)
    );
    
    if (needsVerification) {
      logger.info(`⚠️ Email verification required for ${directoryName} (${this.currentEntity?.name})`);
      
      // Send notification
      await this.notifyVerificationRequired(directoryName, credentials);
      
      // Update Obsidian with verification reminder
      await this.updateVerificationStatus(directoryName, credentials, 'verification-needed');
    }
  }

  async notifyVerificationRequired(directoryName, credentials) {
    const entityName = this.currentEntity?.name || 'Unknown Entity';
    const message = `📧 EMAIL VERIFICATION REQUIRED\n\nEntity: ${entityName}\nDirectory: ${directoryName}\nEmail: ${credentials.email}\nUsername: ${credentials.username}\n\nAction needed: Check your email inbox and click the verification link.`;
    
    // Desktop notification
    notifier.notify({
      title: 'Signup Agent - Verification Required',
      message: `Check email for ${entityName} - ${directoryName}`,
      sound: true,
      wait: true
    });

    // Telegram notification if configured
    const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN;
    const telegramChatId = process.env.TELEGRAM_CHAT_ID;
    if (telegramBotToken && telegramChatId) {
      try {
        await axios.post(`https://api.telegram.org/bot${telegramBotToken}/sendMessage`, {
          chat_id: telegramChatId,
          text: message
        });
      } catch (e) {
        logger.error('Telegram verification notification failed:', e.message);
      }
    }

    // Log to console prominently
    console.log('\n' + '='.repeat(60));
    console.log('📧 EMAIL VERIFICATION REQUIRED');
    console.log('='.repeat(60));
    console.log(`Entity:    ${entityName}`);
    console.log(`Directory: ${directoryName}`);
    console.log(`Email:     ${credentials.email}`);
    console.log(`Username:  ${credentials.username}`);
    console.log('');
    console.log('Action: Check your email inbox and click the verification link.');
    console.log('        Some directories require verification before the');
    console.log('        listing goes live.');
    console.log('='.repeat(60) + '\n');

    logger.info(`Verification reminder sent for ${directoryName} (${entityName})`);
  }

  async updateVerificationStatus(directoryName, credentials, status) {
    try {
      const obsidianDir = path.join(process.env.HOME, 'Obsidian', 'Penelopi', 'Credentials');
      const obsidianFile = path.join(obsidianDir, 'directory-signups.md');
      
      let content = '';
      try {
        content = await fs.readFile(obsidianFile, 'utf8');
      } catch {
        return; // File doesn't exist yet
      }
      
      // Find the entry for this directory and entity and update status
      const entityName = this.currentEntity?.name || 'Unknown';
      const searchString = `## ${directoryName} — ${this.nap?.name || 'Unknown'}`;
      const index = content.indexOf(searchString);
      
      if (index !== -1) {
        // Find the end of this entry (next ## or end of file)
        const nextEntry = content.indexOf('\n## ', index + 1);
        const entryEnd = nextEntry !== -1 ? nextEntry : content.length;
        const entry = content.substring(index, entryEnd);
        
        // Replace verification status
        const updatedEntry = entry.replace(
          /- \*\*Verification Status:\*\* .*/,
          `- **Verification Status:** ${status} ⚠️`
        );
        
        content = content.substring(0, index) + updatedEntry + content.substring(entryEnd);
        await fs.writeFile(obsidianFile, content);
        logger.info(`Updated verification status for ${directoryName} to ${status}`);
      }
    } catch (e) {
      logger.warn(`Could not update verification status: ${e.message}`);
    }
  }

  async logResult(directoryName, success, details = {}) {
    let results = { results: [] };
    try {
      const data = await fs.readFile(this.resultsFile, 'utf8');
      results = JSON.parse(data);
    } catch {}
    
    results.results.push({
      directory: directoryName,
      success,
      timestamp: new Date().toISOString(),
      ...details
    });
    
    await fs.writeFile(this.resultsFile, JSON.stringify(results, null, 2));
  }

  async fillField(selector, value, fieldName) {
    if (!value || !selector) return;
    try {
      await this.page.waitForSelector(selector, { timeout: 5000 });
      await this.page.fill(selector, value);
      logger.info(`Filled ${fieldName}: ${value}`);
    } catch (e) {
      logger.warn(`Could not fill ${fieldName}: ${e.message}`);
    }
  }

  async signupToDirectory(directoryName) {
    const directory = this.directories.find(d => d.name === directoryName);
    if (!directory) {
      logger.error(`Directory ${directoryName} not found in config`);
      return false;
    }

    logger.info(`Starting signup for ${directory.name}`);
    await this.saveState(directoryName, 'starting');

    try {
      await this.page.goto(directory.url, { waitUntil: 'networkidle' });
      await this.saveState(directoryName, 'page_loaded');

      // Check for CAPTCHA immediately
      const captcha = await this.detectCaptcha();
      if (captcha) {
        await this.saveState(directoryName, 'captcha_detected', { selector: captcha });
        await this.notifyCaptcha(directory.name, directory.url);
        const solved = await this.waitForCaptchaSolved();
        if (!solved) {
          await this.logResult(directoryName, false, { reason: 'captcha_timeout' });
          return false;
        }
        await this.saveState(directoryName, 'captcha_solved');
      }

      // Generate credentials
      const creds = this.generateCredentials(directory.name);
      await this.saveState(directoryName, 'credentials_generated', { username: creds.username });

      // Fill form fields based on directory config
      const fields = directory.fields || {};
      
      if (fields.email) await this.fillField(fields.email, creds.email, 'email');
      if (fields.username) await this.fillField(fields.username, creds.username, 'username');
      if (fields.password) await this.fillField(fields.password, creds.password, 'password');
      if (fields.business_name) await this.fillField(fields.business_name, this.nap.name, 'business_name');
      if (fields.category) await this.fillField(fields.category, this.nap.category, 'category');
      if (fields.phone) await this.fillField(fields.phone, this.nap.phone, 'phone');
      if (fields.website) await this.fillField(fields.website, this.nap.website, 'website');
      if (fields.address) await this.fillField(fields.address, this.formatAddress(), 'address');
      if (fields.first_name) await this.fillField(fields.first_name, 'Okeito', 'first_name');
      if (fields.last_name) await this.fillField(fields.last_name, 'TBD', 'last_name');

      await this.saveState(directoryName, 'form_filled');

      // Check for CAPTCHA again before submit
      const captchaBeforeSubmit = await this.detectCaptcha();
      if (captchaBeforeSubmit) {
        await this.saveState(directoryName, 'captcha_detected_pre_submit', { selector: captchaBeforeSubmit });
        await this.notifyCaptcha(directory.name, this.page.url());
        const solved = await this.waitForCaptchaSolved();
        if (!solved) {
          await this.logResult(directoryName, false, { reason: 'captcha_timeout_pre_submit' });
          return false;
        }
      }

      // Submit form
      if (directory.submit_selector) {
        await this.page.click(directory.submit_selector);
        await this.page.waitForTimeout(3000);
      }

      await this.saveState(directoryName, 'submitted');

      // Check for success indicators
      const success = await this.checkSuccess(directory);
      
      if (success) {
        await this.saveCredentials(directoryName, creds);
        await this.logResult(directoryName, true, { username: creds.username });
        logger.info(`✅ Signup successful for ${directory.name}`);
        
        // Show credentials to user
        console.log(`\n🔑 CREDENTIALS FOR ${directory.name}:`);
        console.log(`   Username: ${creds.username}`);
        console.log(`   Password: ${creds.password}`);
        console.log(`   Email: ${creds.email}`);
        console.log(`   Save these! They are also stored in storage/credentials.json\n`);
        
        return true;
      } else {
        await this.logResult(directoryName, false, { reason: 'success_check_failed' });
        logger.warn(`⚠️ Signup may have failed for ${directory.name}`);
        return false;
      }

    } catch (error) {
      logger.error(`Signup failed for ${directory.name}:`, error.message);
      await this.logResult(directoryName, false, { reason: error.message });
      return false;
    }
  }

  async checkSuccess(directory) {
    // Check for common success indicators
    const successIndicators = [
      'success',
      'welcome',
      'thank you',
      'account created',
      'verification email',
      'dashboard',
      'profile',
      'business added'
    ];
    
    const pageText = await this.page.textContent('body').catch(() => '');
    const url = this.page.url();
    
    for (const indicator of successIndicators) {
      if (pageText.toLowerCase().includes(indicator) || url.toLowerCase().includes(indicator)) {
        return true;
      }
    }
    
    // Check if we're still on the signup page (likely failure)
    if (url.includes('signup') || url.includes('register')) {
      return false;
    }
    
    return true; // Assume success if redirected away from signup
  }

  formatAddress() {
    const a = this.nap.address;
    return `${a.street}, ${a.city}, ${a.state} ${a.postcode}, ${a.country}`;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      logger.info('Browser closed');
    }
  }
}

module.exports = SignupAgent;
