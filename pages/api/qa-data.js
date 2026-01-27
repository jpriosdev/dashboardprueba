// pages/api/qa-data.js
import { getQAData } from '../../lib/qaDataLoader.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const force = req.query?.force === '1' || req.query?.force === 'true';
    const qaData = await getQAData({ forceReload: force });
    
    // Server-side debug log: print sprintData summary so it's visible in server console
    try {
      const sprintSample = Array.isArray(qaData.sprintData) ? qaData.sprintData.slice(0, 8) : qaData.sprintData;
      console.log('\n[qa-data] source=%s real=%s sprints=%d', qaData._dataSource || 'unknown', !!qaData._isRealData, qaData.sprintData?.length || 0);
      console.log('[qa-data] sprintData sample:', JSON.stringify(sprintSample, null, 2));
    } catch (e) {
      console.warn('Unable to stringify sprintData for debug logging', e && e.message);
    }

    // Añadir cabeceras útiles para diagnóstico
    res.setHeader('X-QA-Data-Source', qaData._dataSource || 'unknown');
    res.setHeader('X-QA-Sprint-Count', String(qaData.sprintData?.length || 0));
    res.setHeader('X-QA-Is-Real', qaData._isRealData ? '1' : '0');

    // Agregar info de debugging en la respuesta (no incluir secretos)
    const safeEnv = {
      NODE_ENV: process.env.NODE_ENV,
      VERCEL: process.env.VERCEL,
      VERCEL_ENV: process.env.VERCEL_ENV,
      VERCEL_URL: process.env.VERCEL_URL,
      DATA_SOURCE: process.env.DATA_SOURCE
    };

    const pick = (obj, keys) => keys.reduce((a, k) => { if (obj && Object.prototype.hasOwnProperty.call(obj, k)) a[k] = obj[k]; return a; }, {});

    const requestMeta = {
      method: req.method,
      url: req.url,
      host: req.headers.host,
      origin: req.headers.origin,
      referer: req.headers.referer,
      'x-forwarded-for': req.headers['x-forwarded-for'],
      userAgent: req.headers['user-agent'],
      cookiesPresent: !!req.headers.cookie
    };

    const vercelHeaders = pick(req.headers, ['x-vercel-id', 'x-vercel-deployment-url', 'x-vercel-proxied-for', 'x-vercel-cache-control']);

    const response = {
      ...qaData,
      _debug: {
        timestamp: new Date().toISOString(),
        dataSource: qaData._dataSource,
        isRealData: qaData._isRealData,
        sprintCount: qaData.sprintData?.length || 0,
        request: requestMeta,
        vercelHeaders,
        environment: safeEnv,
        node: { pid: process.pid, version: process.version }
      }
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Error loading QA data:', error);
    return res.status(500).json({
      error: 'No QA data is available right now. Try again later.',
      errorMessage: error.message,
    });
  }
}
