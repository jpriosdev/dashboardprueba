import fs from 'fs/promises';
import path from 'path';

const DATA_JSON = path.join(process.cwd(), 'public', 'data', 'qa-data.json');

async function readJsonIfExists() {
  try {
    const txt = await fs.readFile(DATA_JSON, 'utf8');
    return JSON.parse(txt);
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

    // If no JSON, try DAL (which may read JSON or other sources via shim)
    if (!raw) {
      try {
        const DAL = (await import('./database/dal.js')).default;
        if (DAL && typeof DAL.getFullQAData === 'function') {
          raw = await DAL.getFullQAData();
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
        // persist enriched JSON
        try {
          await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
          await fs.writeFile(DATA_JSON, JSON.stringify(enriched, null, 2), 'utf8');
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
