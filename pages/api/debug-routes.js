import fs from 'fs';
import path from 'path';

const PAGE_EXTS = ['.js', '.jsx', '.ts', '.tsx'];

function existsSyncAny(candidates) {
  for (const c of candidates) if (fs.existsSync(c)) return c;
  return null;
}

export default function handler(req, res) {
  const routesToCheck = ['/qa-dashboard', '/config-dashboard', '/executive-dashboard'];
  const pagesDir = path.join(process.cwd(), 'pages');

  const pagesFiles = (function listPages(dir, base = '') {
    try {
      return fs.readdirSync(dir).flatMap(name => {
        const full = path.join(dir, name);
        const rel = path.join(base, name);
        if (fs.statSync(full).isDirectory()) return listPages(full, rel);
        return rel.replace(/\\\\/g, '/');
      });
    } catch (e) { return []; }
  })(pagesDir);

  const results = routesToCheck.map(route => {
    const routePath = route.replace(/^\//, '');
    const candidates = [];
    // page at root: pages/route.js
    for (const ext of PAGE_EXTS) candidates.push(path.join(pagesDir, routePath + ext));
    // page as index: pages/route/index.js
    for (const ext of PAGE_EXTS) candidates.push(path.join(pagesDir, routePath, 'index' + ext));

    const found = existsSyncAny(candidates);
    return {
      route,
      found: !!found,
      foundPath: found ? path.relative(process.cwd(), found) : null,
      candidates: candidates.map(p => path.relative(process.cwd(), p)),
    };
  });

  // Also check API endpoints used by pages
  const apiEndpoints = ['/api/qa-data', '/api/config', '/api/build-debug'];
  const apiChecks = apiEndpoints.map(ep => {
    const apiFile = path.join(process.cwd(), 'pages', ep.replace(/^\//, '') + '.js');
    return { endpoint: ep, exists: fs.existsSync(apiFile), file: fs.existsSync(apiFile) ? path.relative(process.cwd(), apiFile) : null };
  });

  return res.status(200).json({
    ok: true,
    timestamp: new Date().toISOString(),
    pagesCount: pagesFiles.length,
    pagesFiles: pagesFiles.slice(0, 200),
    routeResults: results,
    apiChecks,
  });
}
