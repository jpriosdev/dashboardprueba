const http = require('http');
const url = 'http://localhost:3000/api/qa-data';
http.get(url, res => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => {
    try {
      const j = JSON.parse(d);
      const sd = j.sprintData || [];
      const sumPlanned = sd.reduce((a, s) => a + (s.testCasesPlanned || 0), 0);
      const sumExecuted = sd.reduce((a, s) => a + (s.testCases || 0), 0);
      console.log('sprintCount', sd.length);
      console.log('sumPlanned', sumPlanned);
      console.log('sumExecuted', sumExecuted);
      console.log('sampleSprints:', JSON.stringify(sd.slice(0,6), null, 2));
    } catch (e) {
      console.error('parse error', e.message);
      console.log(d.slice(0,1000));
    }
  });
}).on('error', err => console.error(err));
