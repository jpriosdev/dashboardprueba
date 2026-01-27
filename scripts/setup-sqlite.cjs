const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3');

const cwd = process.cwd();
const dataSource = process.env.DATA_SOURCE;
const argv = process.argv.slice(2);

let dbPath;
if (dataSource && dataSource !== 'none') {
  dbPath = path.isAbsolute(dataSource) ? dataSource : path.join(cwd, dataSource);
} else {
  dbPath = path.join(cwd, 'public', 'data', 'qa-dashboard.db');
}

console.log('Comprobando base de datos en:', dbPath);

if (fs.existsSync(dbPath)) {
  const stat = fs.statSync(dbPath);
  console.log('✅ Encontrada base de datos:', dbPath);
  console.log('   Tamaño:', `${Math.round(stat.size / 1024)} KB`);
  process.exit(0);
}

if (argv.includes('--generate') || argv.includes('-g')) {
  const csvPath = path.join(cwd, 'data', 'MockDataV0.csv');
  if (!fs.existsSync(csvPath)) {
    console.error('❌ No se encontró el CSV fuente en:', csvPath);
    process.exit(1);
  }

  console.log('Generando BD desde CSV:', csvPath);
  const text = fs.readFileSync(csvPath, 'utf8');

  function parseCSV(text) {
    const lines = [];
    let cur = '';
    let row = [];
    let inQuotes = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === '"') {
        if (inQuotes && text[i+1] === '"') { cur += '"'; i++; } else { inQuotes = !inQuotes; }
        continue;
      }
      if (ch === ',' && !inQuotes) { row.push(cur); cur = ''; continue; }
      if ((ch === '\n' || ch === '\r') && !inQuotes) {
        if (cur !== '' || row.length > 0) { row.push(cur); lines.push(row); row = []; cur = ''; }
        if (ch === '\r' && text[i+1] === '\n') i++;
        continue;
      }
      cur += ch;
    }
    if (cur !== '' || row.length > 0) { row.push(cur); lines.push(row); }
    return lines;
  }

  const rows = parseCSV(text);
  if (!rows || rows.length < 2) {
    console.error('CSV vacío o formato inesperado.');
    process.exit(1);
  }

  const headers = rows[0].map(h => h.trim());
  const dataRows = rows.slice(1);
  const cols = headers.map(h => h.toLowerCase().replace(/[^a-z0-9]+/g, '_'));

  const dbDir = path.dirname(dbPath);
  if (!fs.existsSync(dbDir)) fs.mkdirSync(dbDir, { recursive: true });

  const db = new sqlite3.Database(dbPath);

  function execAsync(sql) {
    return new Promise((resolve, reject) => db.exec(sql, (err) => { if (err) reject(err); else resolve(); }));
  }

  (async () => {
    try {
      await execAsync('BEGIN TRANSACTION');
      await execAsync(`CREATE TABLE IF NOT EXISTS bugs_detail (${cols.map(c => `${c} TEXT`).join(', ')});`);
      await execAsync('CREATE TABLE IF NOT EXISTS sprints_versions (sprint TEXT PRIMARY KEY, sprint_num INTEGER);');
      await execAsync(`CREATE TABLE IF NOT EXISTS data_source_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file_name TEXT,
        source_file_path TEXT,
        source_file_size INTEGER,
        total_bugs_loaded INTEGER,
        total_sprints_loaded INTEGER,
        status TEXT,
        notes TEXT,
        load_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      );`);

      const placeholders = cols.map(_=> '?').join(',');
      const insertSql = `INSERT INTO bugs_detail (${cols.join(',')}) VALUES (${placeholders})`;
      const insertStmt = db.prepare(insertSql);
      for (const r of dataRows) {
        const row = cols.map((_, idx) => (r[idx] !== undefined ? r[idx] : null));
        insertStmt.run(row);
      }
      insertStmt.finalize();

      const sprintHeaderIndex = headers.findIndex(h => h && h.toLowerCase().includes('sprint'));
      if (sprintHeaderIndex >= 0) {
        const allSprints = new Set();
        for (const r of dataRows) {
          const val = r[sprintHeaderIndex];
          if (val) allSprints.add(val.trim());
        }
        const insertSprint = db.prepare('INSERT OR REPLACE INTO sprints_versions (sprint, sprint_num) VALUES (?, ?)');
        for (const s of allSprints) {
          const m = s.match(/(\d{1,4})/);
          const num = m ? Number(m[0]) : null;
          insertSprint.run(s, num);
        }
        insertSprint.finalize();
      }

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_bugs_by_sprint AS
        SELECT sprint, COUNT(*) as total,
          SUM(CASE WHEN prioridad = 'Major' THEN 1 ELSE 0 END) as critical,
          SUM(CASE WHEN estado = 'To Do' THEN 1 ELSE 0 END) as pending,
          SUM(CASE WHEN estado = 'Canceled' THEN 1 ELSE 0 END) as canceled
        FROM bugs_detail
        GROUP BY sprint;`);

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_bugs_by_priority AS
        SELECT prioridad as prioridad, COUNT(*) as count, SUM(CASE WHEN estado IN ('To Do','In Development') THEN 1 ELSE 0 END) as pending
        FROM bugs_detail
        GROUP BY prioridad;`);

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_bugs_by_developer AS
        SELECT desarrollador as developer_name, COUNT(*) as total_bugs
        FROM bugs_detail
        WHERE desarrollador IS NOT NULL AND desarrollador != ''
        GROUP BY desarrollador;`);

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_bug_resolution_stats AS
        SELECT 0 as bugs_closed, 0 as production_bugs;`);

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_testcase_stats AS
        SELECT COUNT(*) as total_records, SUM(CASE WHEN LOWER(resumen) LIKE '%test%' THEN 1 ELSE 0 END) as testcases_with_type FROM bugs_detail;`);

      await execAsync(`CREATE VIEW IF NOT EXISTS vw_bugs_summary AS
        SELECT COUNT(*) as total, SUM(CASE WHEN prioridad='Major' THEN 1 ELSE 0 END) as critical FROM bugs_detail;`);

      const stats = fs.statSync(csvPath);
      const totalBugs = await new Promise((res, rej) => db.get('SELECT COUNT(*) as c FROM bugs_detail', (e, r) => e ? rej(e) : res(r.c)));
      await execAsync(`INSERT INTO data_source_metadata (source_file_name, source_file_path, source_file_size, total_bugs_loaded, total_sprints_loaded, status, notes)
        VALUES (${JSON.stringify(path.basename(csvPath))}, ${JSON.stringify(csvPath)}, ${stats.size}, ${totalBugs || 0}, (SELECT COUNT(*) FROM sprints_versions), 'success', 'Generated from MockDataV0.csv');`);

      await execAsync('COMMIT');
      console.log('✅ Base de datos generada en:', dbPath);
      db.close();
      process.exit(0);
    } catch (err) {
      console.error('Error generando BD:', err);
      try { await execAsync('ROLLBACK'); } catch(e) {}
      db.close();
      process.exit(1);
    }
  })();
  return;
}

console.error('❌ No se encontró la base de datos en la ruta esperada.');
console.log('Opciones para continuar:');
console.log('- Ejecuta: node scripts/setup-sqlite.cjs --generate   (crea la DB desde data/MockDataV0.csv)');
console.log("- O añade el archivo SQLite a la ruta: " + dbPath);
console.log("- O sube la BD a un almacenamiento público (S3) y establece 'DATA_SOURCE' a la URL en Vercel");
process.exit(1);
