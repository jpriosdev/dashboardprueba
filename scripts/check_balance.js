const fs = require('fs');
const path = process.argv[2];
if (!path) {
  console.error('Usage: node check_balance.js <file>');
  process.exit(1);
}
const src = fs.readFileSync(path, 'utf8');
const pairs = ['()', '{}', '[]', '<>'];
const counters = { '()':0, '{}':0, '[]':0, '<>':0 };
for (const ch of src) {
  if (ch === '(') counters['()']++;
  if (ch === ')') counters['()']--;
  if (ch === '{') counters['{}']++;
  if (ch === '}') counters['{}']--;
  if (ch === '[') counters['[]']++;
  if (ch === ']') counters['[]']--;
  if (ch === '<') counters['<>']++;
  if (ch === '>') counters['<>']--;
}
console.log('Totals:', counters);

// Find first position where any counter goes negative
let c1=0,c2=0,c3=0,c4=0;
for (let i=0;i<src.length;i++){
  const ch=src[i];
  if (ch==='(') c1++; if (ch===')') c1--;
  if (ch==='{') c2++; if (ch==='}') c2--;
  if (ch==='[') c3++; if (ch===']') c3--;
  if (ch==='<') c4++; if (ch==='>') c4--;
  if (c1<0||c2<0||c3<0||c4<0) {
    const lines = src.slice(0,i+1).split('\n');
    console.log('First negative at index',i,'line',lines.length, 'char', lines[lines.length-1].length+1, 'counters', {paren:c1,brace:c2,brack:c3,angle:c4});
    break;
  }
}

// Print last 60 lines for inspection
const lines = src.split('\n');
const last = lines.slice(-120).join('\n');
console.log('\n--- Last 120 lines ---\n' + last);
