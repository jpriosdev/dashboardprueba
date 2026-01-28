import fs from 'fs/promises';
import path from 'path';

export default async function handler(req, res) {
  const file = path.join(process.cwd(), 'public', 'data', 'build-debug.json');
  try {
    const txt = await fs.readFile(file, 'utf8');
    const json = JSON.parse(txt);
    res.setHeader('Content-Type', 'application/json');
    return res.status(200).json(json);
  } catch (e) {
    return res.status(404).json({ error: 'build-debug not found', message: e && e.message });
  }
}
