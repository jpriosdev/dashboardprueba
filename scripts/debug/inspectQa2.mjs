import fs from 'fs/promises';
import path from 'path';
import { QADataProcessor } from '../../utils/dataProcessor.js';

(async function(){
  const p = path.join(process.cwd(),'public','data','qa-data.json');
  try{
    const txt = await fs.readFile(p,'utf8');
    console.log('raw file size:', txt.length);
    console.log('contains "sprintData"?', txt.indexOf('sprintData') !== -1);
    console.log('first 1200 chars:\n', txt.slice(0,1200));
    const raw = JSON.parse(txt);
    console.log('raw sprintData length =', Array.isArray(raw.sprintData)? raw.sprintData.length : 'no-array');
    const processed = QADataProcessor.processQAData(raw);
    console.log('processed sprintData length =', Array.isArray(processed.sprintData)? processed.sprintData.length : 'no-array');
    console.log('sample raw[0]=', raw.sprintData && raw.sprintData[0]);
    console.log('sample processed[0]=', processed.sprintData && processed.sprintData[0]);
  }catch(e){
    console.error('error', e && e.message);
  }
})();
