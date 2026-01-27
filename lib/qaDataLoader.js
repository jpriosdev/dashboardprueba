import fs from 'fs/promises';
import path from 'path';

const DATA_JSON = path.join(process.cwd(), 'public', 'data', 'qa-data.json');

export async function getQAData(options = {}) {
  const { forceReload = false } = options;

  // If cached JSON exists and no forceReload, return it
  try {
    if (!forceReload) {
      const txt = await fs.readFile(DATA_JSON, 'utf8');
      try {
        const parsed = JSON.parse(txt);
        return parsed;
      } catch (e) {
        // fallthrough to regenerate
      }
    }
  } catch (e) {
    // file not found — will try to generate
  }

  // Fallback: try to use DAL (SQLite) to build data
  try {
    const DAL = (await import('./database/dal.js')).default;
    if (DAL && typeof DAL.getFullQAData === 'function') {
      const data = await DAL.getFullQAData();
      // persist to JSON cache if possible
      try {
        await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
        await fs.writeFile(DATA_JSON, JSON.stringify(data, null, 2), 'utf8');
      } catch (e) {
        // ignore write errors
      }
      return data;
    }
  } catch (err) {
    // DAL not available or failed — fall through
  }

  // Last resort: return minimal structure so APIs don't crash
  const fallback = { summary: {}, bugsByPriority: {}, bugsByModule: [], bugsByCategory: [], developerData: [], sprintData: [], metadata: null };
  try {
    await fs.mkdir(path.dirname(DATA_JSON), { recursive: true });
    await fs.writeFile(DATA_JSON, JSON.stringify(fallback, null, 2), 'utf8');
  } catch (e) {}
  return fallback;
}

export default { getQAData };
