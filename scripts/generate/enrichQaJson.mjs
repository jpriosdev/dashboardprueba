#!/usr/bin/env node
import { getQAData } from '../../lib/qaDataLoader.js';
import fs from 'fs/promises';
import path from 'path';
import { execSync } from 'child_process';

const DEBUG_PATH = path.join(process.cwd(), 'public', 'data', 'build-debug.json');

async function writeDebug(data) {
  const debug = {
    timestamp: new Date().toISOString(),
    node: process.version,
    platform: process.platform,
    arch: process.arch,
    env: {
      NODE_ENV: process.env.NODE_ENV || null,
      VERCEL: process.env.VERCEL || null,
      VERCEL_GIT_COMMIT_SHA: process.env.VERCEL_GIT_COMMIT_SHA || null,
      VERCEL_GIT_COMMIT_MESSAGE: process.env.VERCEL_GIT_COMMIT_MESSAGE || null,
      DATA_SOURCE: process.env.DATA_SOURCE || null
    },
    git: {},
    qaSummary: {
      sprints: (data?.sprintData && data.sprintData.length) || 0,
      totalBugs: data?.summary?.totalBugs || data?.summary?.total_bugs || null
    }
  };
  try {
    debug.git.commit = process.env.VERCEL_GIT_COMMIT_SHA || execSync('git rev-parse --short HEAD').toString().trim();
  } catch (e) { /* ignore */ }
  try {
    debug.git.branch = process.env.VERCEL_GIT_COMMIT_REF || execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
  } catch (e) { /* ignore */ }

  try {
    await fs.mkdir(path.dirname(DEBUG_PATH), { recursive: true });
    await fs.writeFile(DEBUG_PATH, JSON.stringify(debug, null, 2), 'utf8');
    console.log('ℹ️  Build debug written to', DEBUG_PATH);
  } catch (e) {
    console.warn('⚠️  Could not write build debug file:', e && e.message);
  }
}

async function main(){
  try{
    console.log('🔁 Enriching QA JSON (force reload)');
    const data = await getQAData({ forceReload: true });
    if (data) {
      console.log('✅ QA JSON enriched. Sprints:', (data.sprintData && data.sprintData.length) || 0);
      await writeDebug(data);
      process.exit(0);
    }
    console.error('❌ No data returned from getQAData');
    await writeDebug(null);
    process.exit(1);
  }catch(e){
    console.error('❌ Error enriching QA JSON:', e && e.message);
    try { await writeDebug(null); } catch(_) {}
    process.exit(1);
  }
}

main();
