#!/usr/bin/env node
import { getQAData } from '../../lib/qaDataLoader.js';

async function main(){
  try{
    console.log('🔁 Enriching QA JSON (force reload)');
    const data = await getQAData({ forceReload: true });
    if (data) {
      console.log('✅ QA JSON enriched. Sprints:', (data.sprintData && data.sprintData.length) || 0);
      process.exit(0);
    }
    console.error('❌ No data returned from getQAData');
    process.exit(1);
  }catch(e){
    console.error('❌ Error enriching QA JSON:', e && e.message);
    process.exit(1);
  }
}

main();
