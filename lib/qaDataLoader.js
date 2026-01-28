import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';

const DATA_JSON = path.join(process.cwd(), 'public', 'data', 'qa-data.json');

async function readJsonIfExists() {
  try {
    const txt = await fs.readFile(DATA_JSON, 'utf8');
    const parsed = JSON.parse(txt);
    if (process.env.DEBUG_QA === 'true') {
      try {
        console.log('DEBUG_QA: readJsonIfExists read', DATA_JSON, 'size', Buffer.byteLength(txt, 'utf8'));
        console.log('DEBUG_QA: preview:', txt.slice(0, 800));
        console.log('DEBUG_QA: parsed.sprintData length', Array.isArray(parsed.sprintData) ? parsed.sprintData.length : 'no-array');
      } catch (e) {}
    }
    try {
      if (fsSync.existsSync(DATA_JSON)) parsed._sourceFile = DATA_JSON;
    } catch (e) {}
    return parsed;
  } catch (e) {
    return null;
  }
}

export async function getQAData(options = {}) {
  const { forceReload = false } = options;

  // If cached JSON exists and no forceReload, return it (but ensure it's enriched)
  try {
    if (!forceReload) {
      const parsed = await readJsonIfExists();
      if (parsed) return parsed;
    }
  } catch (e) {
    // fallthrough to regenerate
  }

  // Try to generate/enrich JSON from available sources
  try {
    // Prefer existing JSON as raw input to the processor
    let raw = await readJsonIfExists();
      if (process.env.DEBUG_QA === 'true') {
        console.log('DEBUG_QA: raw after readJsonIfExists ->', raw ? (Array.isArray(raw.sprintData) ? raw.sprintData.length : 'no-array') : 'null');
      }

    // If no JSON, try DAL (which may read JSON or other sources via shim)
    if (!raw) {
      try {
        const DAL = (await import('./database/dal.js')).default;
        if (DAL && typeof DAL.getFullQAData === 'function') {
          raw = await DAL.getFullQAData();
          try {
            if (DAL && typeof DAL.getDataSourceInfo === 'function') {
              const info = await DAL.getDataSourceInfo();
              if (info) raw._sourceFile = info.sourceFilePath || info.sourceFileName || raw._sourceFile || null;
            }
          } catch (e) {
            // ignore
          }
        }
      } catch (e) {
        // continue
      }
    }

    // If still no data, create minimal skeleton
    if (!raw) raw = { summary: {}, sprintData: [], developerData: [], bugsByPriority: {}, bugsByModule: [], bugsByCategory: [], bugs: [], metadata: null };

    // Enrich with QADataProcessor if available
    try {
      const proc = (await import('../utils/dataProcessor.js')).QADataProcessor;
      if (proc && typeof proc.processQAData === 'function') {
          const enriched = await proc.processQAData(raw);
          if (raw && raw._sourceFile && !enriched._sourceFile) enriched._sourceFile = raw._sourceFile;
        // persist enriched JSON to a separate file to avoid overwriting the original source
        try {
          await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
          const enrichedPath = path.join(path.dirname(DATA_JSON), 'qa-data.enriched.json');
          await fs.writeFile(enrichedPath, JSON.stringify(enriched, null, 2), 'utf8');
        } catch (e) {
          // ignore write errors
        }
        return enriched;
      }
    } catch (err) {
      // processor not available — fall back to raw
    }

    // Persist raw fallback
    try {
      await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
      await fs.writeFile(DATA_JSON, JSON.stringify(raw, null, 2), 'utf8');
    } catch (e) {}
    return raw;
  } catch (err) {
    // If everything fails, return minimal structure
    return { summary: {}, bugsByPriority: {}, bugsByModule: [], bugsByCategory: [], developerData: [], sprintData: [], metadata: null };
  }
}

export default { getQAData };
