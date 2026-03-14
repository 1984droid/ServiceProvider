#!/usr/bin/env node
/**
 * Port Check Script
 *
 * Ensures the correct ports are available before starting servers.
 * HARD RULE: Backend MUST be on 8001, Frontend MUST be on 5174.
 */

const net = require('net');

const REQUIRED_PORTS = {
  backend: 8001,
  frontend: 5174,
};

function checkPort(port) {
  return new Promise((resolve, reject) => {
    const server = net.createServer();

    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        reject(new Error(`Port ${port} is already in use`));
      } else {
        reject(err);
      }
    });

    server.once('listening', () => {
      server.close();
      resolve();
    });

    server.listen(port);
  });
}

async function main() {
  console.log('🔍 Checking required ports...\n');

  let hasErrors = false;

  for (const [name, port] of Object.entries(REQUIRED_PORTS)) {
    try {
      await checkPort(port);
      console.log(`✅ ${name} port ${port} is available`);
    } catch (error) {
      console.error(`❌ ${name} port ${port} is NOT available: ${error.message}`);
      hasErrors = true;
    }
  }

  console.log('\n' + '='.repeat(50));

  if (hasErrors) {
    console.error('\n⛔ PORT CHECK FAILED');
    console.error('\nHARD RULE: Backend must run on port 8001, Frontend must run on port 5174.');
    console.error('Please free up these ports before starting the servers.\n');
    process.exit(1);
  } else {
    console.log('\n✅ All required ports are available!');
    console.log('\nYou can now start the servers:');
    console.log('  Backend:  python manage.py runserver 8001');
    console.log('  Frontend: cd frontend && npm run dev\n');
    process.exit(0);
  }
}

main();
