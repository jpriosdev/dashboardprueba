import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';

const DATA_JSON = path.join(process.cwd(), 'public', 'data', 'qa-data.json');

function safeNumber(v, def = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

async function readJson() {
  try {
    const txt = await fs.readFile(DATA_JSON, 'utf8');
    try {
      const parsed = JSON.parse(txt) || {};
      parsed._sourceFile = DATA_JSON;
      return parsed;
    } catch (e) {
      return {};
    }
  } catch (e) {
    // Try to fall back to the latest file in data/versions if available
    try {
      const versionsDir = path.join(process.cwd(), 'data', 'versions');
      if (fsSync.existsSync(versionsDir)) {
        const files = fsSync.readdirSync(versionsDir)
          .filter(f => f.endsWith('.json'))
          .map(f => ({ name: f, path: path.join(versionsDir, f), stat: fsSync.statSync(path.join(versionsDir, f)) }))
          .sort((a, b) => b.stat.mtimeMs - a.stat.mtimeMs);
        if (files.length) {
          try {
            const txt2 = fsSync.readFileSync(files[0].path, 'utf8');
            try {
              const parsed2 = JSON.parse(txt2) || {};
              parsed2._sourceFile = files[0].path;
              console.log('ℹ️  DAL fallback: using', files[0].path);
              return parsed2;
            } catch (e2) {
              return {};
            }
          } catch (e2) {
            return null;
          }
        }
      }
    } catch (e3) {
      // ignore
    }
    return null;
  }
}

async function getFullQAData() {
  const data = await readJson();
  if (!data) return { summary: {}, sprintData: [], bugs: [], metadata: null };
  return {
    summary: data.summary || data.summaryRaw || {},
    sprintData: data.sprintData || [],
    bugs: data.bugs || [],
    developerData: data.developerData || [],
    bugsByPriority: data.bugsByPriority || {},
    bugsByModule: data.bugsByModule || [],
    bugsByCategory: data.bugsByCategory || [],
    metadata: data.metadata || null
  };
}

async function getDataSourceInfo() {
  try {
    const data = await readJson();
    if (data && data.metadata) return data.metadata;
    if (fsSync.existsSync(DATA_JSON)) {
      const st = fsSync.statSync(DATA_JSON);
      return {
        sourceFileName: path.basename(DATA_JSON),
        sourceFilePath: DATA_JSON,
        fileSizeBytes: st.size,
        fileSizeKB: (st.size / 1024).toFixed(2),
        loadedAt: st.mtime.toISOString(),
        totalBugsLoaded: data?.summary?.totalBugs || data?.summary?.total_bugs || 0,
        totalSprintsLoaded: data?.sprintData?.length || 0,
        status: 'json',
        notes: 'loaded from public/data/qa-data.json'
      };
    }
    return null;
  } catch (e) {
    return null;
  }
}

async function getStatistics() {
  const data = await readJson();
  const summary = data?.summary || {};
  return {
    totalBugs: summary.totalBugs || summary.total_bugs || 0,
    totalSprints: data?.sprintData?.length || summary.totalSprints || 0,
    criticalBugs: summary.criticalBugs || summary.critical_bugs || 0,
    pendingBugs: summary.pendingBugs || summary.pending_bugs || 0,
    summaryRaw: summary
  };
}

async function getAllSprints() {
  const data = await readJson();
  return data?.sprintData || [];
}

async function getBugsBySprint() {
  const data = await readJson();
  const sprints = data?.sprintData || [];
  return sprints.map((s, idx) => ({
    sprint: s.sprint || s.sprintName || `Sprint ${idx + 1}`,
    sprint_num: Number(s.sprint_num ?? s.sprintNumber ?? (idx + 1)) || (idx + 1),
    total_bugs: safeNumber(s.total || s.total_bugs || s.bugs || 0),
    critical_bugs: safeNumber(s.critical || s.criticalBugsTotal || 0),
    pending_bugs: safeNumber(s.pending || s.bugsPending || 0)
  }));
}

// Compatibility: SQL-like helpers but not implemented for JSON backend
async function runQuery() { return []; }
async function runScalar(sql) {
  const low = (sql || '').toString().trim().toLowerCase();
  if (low.startsWith('select 1')) return { ok: 1 };
  return null;
}

async function recordDataSourceMetadata() { return { success: true }; }
async function getLatestDataSourceMetadata() { return null; }
async function getAllDataSourceMetadata() { return []; }

const DAL = {
  getFullQAData,
  getDataSourceInfo,
  getStatistics,
  getAllSprints,
  getBugsBySprint,
  runQuery,
  runScalar,
  recordDataSourceMetadata,
  getLatestDataSourceMetadata,
  getAllDataSourceMetadata
};

export default DAL;

