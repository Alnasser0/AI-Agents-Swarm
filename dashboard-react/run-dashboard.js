#!/usr/bin/env node

/**
 * AI Agents Swarm - React Dashboard Setup & Launch Script
 * 
 * This script handles installation and launching of the Next.js dashboard
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✅${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}❌${colors.reset} ${msg}`),
  header: (msg) => console.log(`${colors.cyan}${colors.bright}🚀 ${msg}${colors.reset}`),
};

class DashboardLauncher {
  constructor() {
    this.projectRoot = __dirname;
    this.isWindows = os.platform() === 'win32';
    this.nodeVersion = process.version;
  }

  checkPrerequisites() {
    log.header('Checking Prerequisites...');
    
    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion < 18) {
      log.error(`Node.js 18+ is required. Current version: ${nodeVersion}`);
      log.info('Please upgrade Node.js: https://nodejs.org/');
      process.exit(1);
    }
    
    log.success(`Node.js ${nodeVersion} ✓`);
    
    // Check if package.json exists
    if (!fs.existsSync(path.join(this.projectRoot, 'package.json'))) {
      log.error('package.json not found. Are you in the correct directory?');
      process.exit(1);
    }
    
    log.success('Project structure ✓');
  }

  async checkDependencies() {
    log.info('Checking dependencies...');
    
    const nodeModulesExists = fs.existsSync(path.join(this.projectRoot, 'node_modules'));
    const packageLockExists = fs.existsSync(path.join(this.projectRoot, 'package-lock.json'));
    
    if (!nodeModulesExists || !packageLockExists) {
      log.warning('Dependencies need to be installed');
      return false;
    }
    
    try {
      // Check if key dependencies are installed
      const packageJson = JSON.parse(fs.readFileSync(path.join(this.projectRoot, 'package.json'), 'utf8'));
      const requiredDeps = ['next', 'react', 'react-dom', 'typescript'];
      
      for (const dep of requiredDeps) {
        if (!packageJson.dependencies?.[dep] && !packageJson.devDependencies?.[dep]) {
          log.warning(`Missing dependency: ${dep}`);
          return false;
        }
      }
      
      log.success('Dependencies installed ✓');
      return true;
    } catch (error) {
      log.warning('Could not verify dependencies');
      return false;
    }
  }

  async installDependencies() {
    log.header('Installing Dependencies...');
    
    return new Promise((resolve, reject) => {
      const npmCmd = this.isWindows ? 'npm.cmd' : 'npm';
      const installProcess = spawn(npmCmd, ['install'], {
        cwd: this.projectRoot,
        stdio: 'pipe',
        shell: this.isWindows
      });

      let output = '';
      installProcess.stdout.on('data', (data) => {
        output += data.toString();
        process.stdout.write(data);
      });

      installProcess.stderr.on('data', (data) => {
        output += data.toString();
        process.stderr.write(data);
      });

      installProcess.on('close', (code) => {
        if (code === 0) {
          log.success('Dependencies installed successfully!');
          resolve();
        } else {
          log.error(`npm install failed with code ${code}`);
          reject(new Error(`Installation failed: ${code}`));
        }
      });

      installProcess.on('error', (error) => {
        log.error(`Failed to start npm install: ${error.message}`);
        reject(error);
      });
    });
  }

  async checkBackendConnection() {
    log.info('Checking backend connection...');
    
    try {
      const response = await fetch('http://localhost:8000/health', {
        timeout: 5000
      });
      
      if (response.ok) {
        log.success('Backend connected ✓');
        return true;
      } else {
        log.warning('Backend responded but not healthy');
        return false;
      }
    } catch (error) {
      log.warning('Backend not reachable (will use mock data)');
      return false;
    }
  }

  async startDevelopmentServer() {
    log.header('Starting Development Server...');
    
    return new Promise((resolve) => {
      const npmCmd = this.isWindows ? 'npm.cmd' : 'npm';
      const devProcess = spawn(npmCmd, ['run', 'dev'], {
        cwd: this.projectRoot,
        stdio: 'pipe',
        shell: this.isWindows
      });

      let serverReady = false;

      devProcess.stdout.on('data', (data) => {
        const output = data.toString();
        process.stdout.write(data);
        
        // Check if server is ready
        if (output.includes('Local:') || output.includes('localhost:3000')) {
          if (!serverReady) {
            serverReady = true;
            setTimeout(() => {
              this.openBrowser();
              resolve();
            }, 2000);
          }
        }
      });

      devProcess.stderr.on('data', (data) => {
        process.stderr.write(data);
      });

      devProcess.on('close', (code) => {
        log.info(`Development server stopped with code ${code}`);
      });

      // Handle Ctrl+C gracefully
      process.on('SIGINT', () => {
        log.info('Shutting down development server...');
        devProcess.kill('SIGTERM');
        process.exit(0);
      });
    });
  }

  openBrowser() {
    const url = 'http://localhost:3000';
    log.success(`Dashboard available at: ${url}`);
    
    try {
      const start = this.isWindows ? 'start' : os.platform() === 'darwin' ? 'open' : 'xdg-open';
      
      if (this.isWindows) {
        execSync(`start ${url}`, { stdio: 'ignore' });
      } else {
        execSync(`${start} ${url}`, { stdio: 'ignore' });
      }
      
      log.success('Opening dashboard in browser...');
    } catch (error) {
      log.warning(`Could not open browser automatically. Please visit: ${url}`);
    }
  }

  async run() {
    try {
      console.log(`${colors.cyan}${colors.bright}`);
      console.log('🤖 AI Agents Swarm - React Dashboard');
      console.log('=====================================');
      console.log(`${colors.reset}`);
      
      // Check system prerequisites
      this.checkPrerequisites();
      
      // Check and install dependencies
      const depsInstalled = await this.checkDependencies();
      if (!depsInstalled) {
        await this.installDependencies();
      }
      
      // Check backend connection (optional)
      await this.checkBackendConnection();
      
      // Start development server
      log.header('🎉 Starting Dashboard...');
      log.info('Dashboard will be available at: http://localhost:3000');
      log.info('Press Ctrl+C to stop the server');
      log.info('');
      
      await this.startDevelopmentServer();
      
    } catch (error) {
      log.error(`Failed to start dashboard: ${error.message}`);
      process.exit(1);
    }
  }
}

// Handle command line arguments
const args = process.argv.slice(2);
const command = args[0];

if (command === 'install') {
  // Just install dependencies
  const launcher = new DashboardLauncher();
  launcher.checkPrerequisites();
  launcher.installDependencies()
    .then(() => {
      log.success('Installation complete!');
      log.info('Run "npm run dev" to start the dashboard');
    })
    .catch((error) => {
      log.error(`Installation failed: ${error.message}`);
      process.exit(1);
    });
} else if (command === 'build') {
  // Build for production
  log.header('Building for production...');
  try {
    execSync('npm run build', { stdio: 'inherit' });
    log.success('Build complete!');
    log.info('Run "npm start" to start the production server');
  } catch (error) {
    log.error('Build failed');
    process.exit(1);
  }
} else {
  // Default: run development server
  const launcher = new DashboardLauncher();
  launcher.run();
}

module.exports = DashboardLauncher;
