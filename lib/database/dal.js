/**
 * DAL - Data Access Layer
 * Reusable functions for common queries against SQLite
 */

import sqlite3 from 'sqlite3';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Determinar la ruta de la base de datos. Permite sobrescribir con la variable
// de entorno DATA_SOURCE (ruta absoluta o relativa al cwd). Si no está definida,
// se usa el `.db` por defecto en `public/data`.
const defaultDbPath = path.join(__dirname, '../../public/data/qa-dashboard.db');
let dbPath;
if (process.env.DATA_SOURCE && process.env.DATA_SOURCE !== 'none') {
  const envPath = process.env.DATA_SOURCE;
  dbPath = path.isAbsolute(envPath) ? envPath : path.join(process.cwd(), envPath);
} else {
  dbPath = defaultDbPath;
}

// Crear directorio si no existe (si se está usando SQLite en archivo)
if (dbPath) {
  const dbDir = path.dirname(dbPath);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
}

// Pool simple de conexión
let db = null;

function getDatabase() {
  if (!db) {
    db = new (sqlite3.verbose().Database)(dbPath, (err) => {
      if (err) {
        console.error('❌ Error conectando a BD:', err);
      }
    });
  }
  return db;
}

// Promisify queries
function runQuery(sql, params = []) {
  return new Promise((resolve, reject) => {
    getDatabase().all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows || []);
    });
  });
}

function runScalar(sql, params = []) {
  return new Promise((resolve, reject) => {
    getDatabase().get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

// ============================================================================
// QUERIES: GENERAL SUMMARY
// ============================================================================

async function getBugsSummary() {
  return runQuery('SELECT * FROM vw_bugs_summary');
}

async function getTotalBugs() {
  const result = await runScalar("SELECT COUNT(*) as total FROM bugs_detail WHERE tipo_incidencia = 'Bug'");
  return result?.total || 0;
}

async function getTotalSprints() {
  const result = await runScalar('SELECT COUNT(*) as total FROM sprints_versions');
  return result?.total || 0;
}

// ============================================================================
// QUERIES: BUGS BY SPRINT
// ============================================================================

async function getBugsBySprint() {
  return runQuery('SELECT * FROM vw_bugs_by_sprint ORDER BY sprint_num');
}

async function getBugsBySprintIncludingSuggestions() {
  // Devolver todos los bugs por sprint SIN excluir sugerencias
  return runQuery(`
    SELECT 
      CAST(SUBSTR(sprint, -2) AS INTEGER) as sprint_num,
      sprint,
      COUNT(*) as total,
      SUM(CASE WHEN prioridad = 'Major' THEN 1 ELSE 0 END) as critical,
          SUM(CASE WHEN estado = 'To Do' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN estado = 'Canceled' THEN 1 ELSE 0 END) as canceled
    FROM bugs_detail
    GROUP BY sprint
    ORDER BY sprint_num
  `);
}

async function getTestCasesBySprint() {
  return runQuery(`
    SELECT
      CAST(SUBSTR(sprint, -2) AS INTEGER) as sprint_num,
      sprint,
      -- Executed test cases: only consider final/closed states (execution completed)
      SUM(CASE WHEN LOWER(COALESCE(resumen,'')) LIKE '%test%' AND tipo_incidencia != 'Bug' AND estado IN ('Done','Approved for Release','Reviewed','Testing Complete') THEN 1 ELSE 0 END) as total_tests
    FROM bugs_detail
    GROUP BY sprint
    ORDER BY sprint_num
  `);
}
async function getPlannedTestCasesBySprint() {
  return runQuery(`
    SELECT
      CAST(SUBSTR(sprint, -2) AS INTEGER) as sprint_num,
      sprint,
      -- Planned test cases: any row mentioning 'test' in resumen and NOT a Bug (all states)
      SUM(CASE WHEN LOWER(COALESCE(resumen,'')) LIKE '%test%' AND tipo_incidencia != 'Bug' THEN 1 ELSE 0 END) as total_tests
    FROM bugs_detail
    GROUP BY sprint
    ORDER BY sprint_num
  `);
}

async function getBugsBySprintAndStatus() {
  return runQuery('SELECT * FROM vw_bugs_by_sprint_status ORDER BY sprint');
}

async function getBugsBySprintNumber(sprintNum) {
  return runQuery(
    'SELECT * FROM vw_bugs_by_sprint WHERE sprint_num = ?',
    [sprintNum]
  );
}

async function getCriticalBugsPendingBySprint() {
  return runQuery(`
    SELECT 
      sprint,
      COUNT(*) as critical_pending
    FROM bugs_detail
    WHERE prioridad = 'Major'
      AND estado IN ('To Do', 'In Development')
    GROUP BY sprint
    ORDER BY sprint
  `);
}

async function getCriticalBugsBySprintAndState() {
  return runQuery(`
    SELECT 
      sprint,
      SUM(CASE WHEN prioridad = 'Major' AND estado = 'To Do' THEN 1 ELSE 0 END) as tareasPorHacer,
      SUM(CASE WHEN prioridad = 'Major' AND estado = 'In Development' THEN 1 ELSE 0 END) as enProgreso,
      SUM(CASE WHEN prioridad = 'Major' AND estado = 'Ready for Testing' THEN 1 ELSE 0 END) as reabierto
    FROM bugs_detail
    WHERE prioridad = 'Major'
    GROUP BY sprint
    ORDER BY sprint
  `);
}

// ============================================================================
// QUERIES: BREAKDOWN BY MODULE BY DEVELOPER
// ============================================================================

async function getDeveloperModulesSummary() {
  return runQuery(`
    SELECT 
      asignado_a as developer_name,
      COALESCE(modulo, 'Sin módulo') as modulo,
      COUNT(*) as count,
      SUM(CASE WHEN estado in ('To Do', 'Ready for Testing', 'In Development') THEN 1 ELSE 0 END) as pending,
      SUM(CASE WHEN estado not in ('To Do', 'Ready for Testing', 'In Development') THEN 1 ELSE 0 END) as resolved
    FROM bugs_detail
    WHERE asignado_a IS NOT NULL AND asignado_a != ''
      AND modulo IS NOT NULL AND modulo != ''
    GROUP BY asignado_a, modulo
    ORDER BY asignado_a, count DESC
  `);
}

// ============================================================================
// QUERIES: BUGS BY DEVELOPER
// ============================================================================

async function getBugsByDeveloper() {
  return runQuery('SELECT * FROM vw_bugs_by_developer ORDER BY total_bugs DESC');
}

async function getBugsByDeveloperName(devName) {
  return runQuery(
    'SELECT * FROM vw_bugs_by_developer WHERE developer_name = ?',
    [devName]
  );
}

// ============================================================================
// QUERIES: BUGS BY PRIORITY
// ============================================================================

async function getCriticalBugs() {
  return runQuery(
    `SELECT COUNT(*) as count FROM bugs_detail 
    WHERE prioridad = 'Major' AND tipo_incidencia = 'Bug'`
  );
}

// ============================================================================
// QUERIES: BUGS BY MODULE
// ============================================================================

async function getBugsByModule() {
  return runQuery('SELECT * FROM vw_bugs_by_module ORDER BY count DESC');
}

// ============================================================================
// QUERIES: BUGS BY CATEGORY
// ============================================================================

async function getBugsByCategory() {
  return runQuery('SELECT * FROM vw_bugs_by_category ORDER BY count DESC');
}

// ============================================================================
// QUERIES: SPECIFIC DETAILS
// ============================================================================

async function getBugDetail(clave) {
  return runScalar(
    'SELECT * FROM bugs_detail WHERE clave_incidencia = ?',
    [clave]
  );
}

async function getBugsByState(estado) {
  return runQuery(
    'SELECT * FROM bugs_detail WHERE estado = ? ORDER BY sprint',
    [estado]
  );
}

async function getBugsByPriority(prioridad) {
  if (prioridad) {
    // Si se pasa un parámetro, devolver detalles de esa prioridad
    return runQuery(
      'SELECT * FROM bugs_detail WHERE prioridad = ? ORDER BY sprint',
      [prioridad]
    );
  } else {
    // Si no se pasa parámetro, devolver resumen desde la vista (excluye sugerencias)
    return runQuery('SELECT * FROM vw_bugs_by_priority ORDER BY prioridad');
  }
}

// ============================================================================
// QUERIES: SPRINT INFORMATION
// ============================================================================

async function getSprintInfo(sprintNum) {
  return runScalar(
    'SELECT * FROM sprints_versions WHERE sprint = ?',
    [sprintNum]
  );
}

async function getAllSprints() {
  return runQuery('SELECT * FROM sprints_versions ORDER BY sprint');
}

// ============================================================================
// FILTERED QUERIES (combination of criteria)
// ============================================================================

async function getBugsFiltered(filters = {}) {
  let sql = 'SELECT * FROM bugs_detail WHERE 1=1';
  const params = [];

  if (filters.sprint) {
    sql += ' AND sprint LIKE ?';
    params.push(`%${filters.sprint}%`);
  }

  if (filters.prioridad) {
    sql += ' AND prioridad = ?';
    params.push(filters.prioridad);
  }

  if (filters.estado) {
    sql += ' AND estado = ?';
    params.push(filters.estado);
  }

  if (filters.modulo) {
    sql += ' AND modulo = ?';
    params.push(filters.modulo);
  }

  if (filters.asignado_a) {
    sql += ' AND asignado_a = ?';
    params.push(filters.asignado_a);
  }

  if (filters.categoria) {
    sql += ' AND categoria = ?';
    params.push(filters.categoria);
  }

  sql += ' ORDER BY sprint';

  return runQuery(sql, params);
}

// ============================================================================
// QUERIES: STATISTICS
// ============================================================================

async function getStatistics() {
  const [totalBugs, totalSprints, critical, pending, summary, bugStats, tcStats] = await Promise.all([
    getTotalBugs(),
    getTotalSprints(),
    getCriticalBugs(),
    // pending: intentamos contar estados abiertos (varia según idioma/convención)
    runScalar("SELECT COUNT(*) as count FROM bugs_detail WHERE estado IN ('To Do', 'In Development' ,'Ready for Testing') AND tipo_incidencia = 'Bug'"),
    getBugsSummary(),
    // vistas nuevas
    runScalar('SELECT * FROM vw_bug_resolution_stats'),
      runScalar('SELECT * FROM vw_testcase_stats')
  ]);

  const summaryRow = (summary && summary[0]) ? summary[0] : {};

  // Normalize and return camelCase keys expected by the processor
  return {
    totalBugs: totalBugs,
    totalSprints: totalSprints,
    criticalBugs: critical[0]?.count || summaryRow.critical || 0,
    pendingBugs: pending?.count || summaryRow.pending || 0,
    // Use resolution stats when available
    bugsClosed: (bugStats && bugStats.bugs_closed !== undefined) ? bugStats.bugs_closed : (summaryRow.resolved || 0),
    productionBugs: (bugStats && bugStats.production_bugs !== undefined) ? bugStats.production_bugs : 0,
    // Test case estimations: prefer values from summary if present, fallback to testcase view values (normalized to integers)
    testCasesTotal: (typeof summaryRow.testCasesTotal === 'number' && summaryRow.testCasesTotal >= 0)
      ? summaryRow.testCasesTotal
      : (tcStats && tcStats.total_records !== undefined) ? Number(tcStats.total_records) : 0,
    testCasesExecuted: (typeof summaryRow.testCasesExecuted === 'number' && summaryRow.testCasesExecuted >= 0)
      ? summaryRow.testCasesExecuted
      : (tcStats && tcStats.testcases_with_type !== undefined) ? Number(tcStats.testcases_with_type) : 0,
    // keep raw summary data for compatibility
    summaryRaw: summaryRow
  };
}

// ============================================================================
// QUERIES: DATA SOURCE METADATA
// ============================================================================

async function recordDataSourceMetadata(sourceFileName, sourceFilePath, fileSize, totalBugs, totalSprints, notes = '') {
  try {
    return new Promise((resolve, reject) => {
      const sql = `
        INSERT INTO data_source_metadata 
        (source_file_name, source_file_path, source_file_size, total_bugs_loaded, total_sprints_loaded, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;
      getDatabase().run(
        sql,
        [sourceFileName, sourceFilePath, fileSize, totalBugs, totalSprints, 'success', notes],
        (err) => {
          if (err) reject(err);
          else resolve({ success: true });
        }
      );
    });
  } catch (error) {
    console.error('Error recording metadata:', error);
    throw error;
  }
}

async function getLatestDataSourceMetadata() {
  return runScalar(`
    SELECT * FROM data_source_metadata 
    ORDER BY load_timestamp DESC 
    LIMIT 1
  `);
}

async function getAllDataSourceMetadata() {
  return runQuery(`
    SELECT * FROM data_source_metadata 
    ORDER BY load_timestamp DESC
  `);
}

async function getDataSourceInfo() {
  const latest = await getLatestDataSourceMetadata();
  if (latest) {
    return {
      sourceFileName: latest.source_file_name,
      sourceFilePath: latest.source_file_path,
      fileSizeBytes: latest.source_file_size,
      fileSizeKB: latest.source_file_size ? (latest.source_file_size / 1024).toFixed(2) : null,
      loadedAt: latest.load_timestamp,
      totalBugsLoaded: latest.total_bugs_loaded,
      totalSprintsLoaded: latest.total_sprints_loaded,
      status: latest.status,
      notes: latest.notes
    };
  }
  return null;
}

// ============================================================================
// QUERIES: TEAM ANALYSIS (from bugs_detail)
// ============================================================================

async function getDevelopersAnalysis() {
  // Prefer developers_summary (sheet "BUGS X DESARROLLADOR") as source of truth
  return runQuery(`
    SELECT 
      developer_name,
      total_bugs,
      tareas_por_hacer as pending,
      en_curso as in_progress,
      code_review,
      ready_for_testing,
      ready_for_uat,
      blocked,
      cancelado as canceled,
      ROUND(((total_bugs - tareas_por_hacer) * 100.0 / NULLIF(total_bugs, 0)), 2) as efficiency_percentage,
      CASE 
        WHEN tareas_por_hacer > 15 THEN 'Alto'
        WHEN tareas_por_hacer > 8 THEN 'Medio'
        ELSE 'Bajo'
      END as workload_level
    FROM developers_summary
    WHERE total_bugs > 0
    ORDER BY total_bugs DESC
  `);
}

async function getDeveloperByName(devName) {
  return runScalar(
    `SELECT 
      developer_name,
      total_bugs,
      tareas_por_hacer as pending,
      en_curso as in_progress,
      code_review,
      ready_for_testing,
      ready_for_uat,
      blocked,
      cancelado as canceled,
      ROUND(((total_bugs - tareas_por_hacer) * 100.0 / NULLIF(total_bugs, 0)), 2) as efficiency_percentage,
      CASE WHEN tareas_por_hacer > 15 THEN 'Alto' WHEN tareas_por_hacer > 8 THEN 'Medio' ELSE 'Bajo' END as workload_level
    FROM developers_summary WHERE developer_name = ? LIMIT 1`,
    [devName]
  );
}

async function getTeamSummary() {
  return runScalar(`
    SELECT 
      COUNT(DISTINCT asignado_a) as total_developers,
      SUM(CASE WHEN asignado_a IS NOT NULL AND asignado_a != '' THEN 1 ELSE 0 END) as total_assigned_bugs,
      SUM(CASE WHEN asignado_a IS NOT NULL AND asignado_a != '' AND estado = 'To Do' THEN 1 ELSE 0 END) as total_pending_assigned
    FROM bugs_detail
  `);
}

// ============================================================================
// EXPORTS
// ============================================================================

const DAL = {
    async getFullQAData() {
      // Resumen general
      const summary = await DAL.getStatistics();
      // Bugs por prioridad - convertir array a objeto indexado
      const bugsByPriorityArray = await DAL.getBugsByPriority();
      const bugsByPriority = {};
      bugsByPriorityArray.forEach(row => {
        bugsByPriority[row.prioridad] = {
          count: row.count,
          pending: row.pending,
          canceled: row.canceled,
          resolved: row.resolved
        };
      });
      // Bugs por módulo
      const bugsByModule = await DAL.getBugsByModule();
      // Bugs por categoría
      const bugsByCategory = await DAL.getBugsByCategory();
      // Datos de desarrolladores
      const developerData = await DAL.getDevelopersAnalysis();
      
      // Datos por sprint para densidad (excluye sugerencias)
      const sprintDataRaw = await DAL.getBugsBySprint();
      const sprintData = sprintDataRaw.map(sprint => ({
        ...sprint,
        bugs: sprint.total  // Para densidad de hallazgos
      }));
      
      // Datos por sprint para test cases
      // - executed: rows with 'test' in resumen (not Bug) and in final states
      // - planned: rows with 'test' in resumen (not Bug) in any state
      const executedTestCasesRaw = await DAL.getTestCasesBySprint();
      const plannedTestCasesRaw = await DAL.getPlannedTestCasesBySprint();
      const executedMap = {};
      executedTestCasesRaw.forEach(r => {
        executedMap[(r.sprint || '').toString()] = r.total_tests || 0;
      });
      const plannedMap = {};
      plannedTestCasesRaw.forEach(r => {
        plannedMap[(r.sprint || '').toString()] = r.total_tests || 0;
      });
      // Total planned test cases across all sprints
      const totalPlannedTests = Object.values(plannedMap).reduce((a, b) => a + (Number(b) || 0), 0);
      // Expose in summary as `testCasesPlanned` so frontend can read planned totals
      try { summary.testCasesPlanned = totalPlannedTests; } catch (e) { /* noop */ }
      const testCasesPerSprint = Array.from(new Set([
        ...executedTestCasesRaw.map(r => (r.sprint || '').toString()),
        ...plannedTestCasesRaw.map(r => (r.sprint || '').toString())
      ])).map(sprintName => ({
        sprint: sprintName,
        sprint_num: (plannedTestCasesRaw.find(r => (r.sprint || '').toString() === sprintName) || executedTestCasesRaw.find(r => (r.sprint || '').toString() === sprintName) || {}).sprint_num || 0,
        testCases: executedMap[sprintName] || 0, // keep existing meaning: executed
        testCasesExecuted: executedMap[sprintName] || 0,
        testCasesPlanned: plannedMap[sprintName] || 0
      }));
      
      // Bugs críticos pendientes por sprint
      const criticalBugsPendingRaw = await DAL.getCriticalBugsPendingBySprint();
      const criticalBugsPendingMap = {};
      criticalBugsPendingRaw.forEach(row => {
        criticalBugsPendingMap[row.sprint] = row.critical_pending || 0;
      });
      
      // Bugs críticos por sprint desglosados por estado
      const criticalBugsByStateRaw = await DAL.getCriticalBugsBySprintAndState();
      const criticalBugsByStateMap = {};
      criticalBugsByStateRaw.forEach(row => {
        criticalBugsByStateMap[row.sprint] = {
          tareasPorHacer: row.tareasPorHacer || 0,
          enProgreso: row.enProgreso || 0,
          reabierto: row.reabierto || 0
        };
      });
      
      // Asegurarse de incluir sprints que están en testCasesPerSprint pero no en sprintData
      const sprintNames = new Set(sprintData.map(s => (s.sprint || '').toString()));
      testCasesPerSprint.forEach(tc => {
        const name = (tc.sprint || '').toString();
        if (!sprintNames.has(name)) {
          sprintData.push({
            sprint: tc.sprint,
            sprint_num: tc.sprint_num || 0,
            total: 0,
            critical: 0,
            pending: 0,
            canceled: 0,
            bugs: 0
          });
          sprintNames.add(name);
        }
      });
      // Ordenar por sprint_num para mantener consistencia
      sprintData.sort((a, b) => (Number(a.sprint_num) || 0) - (Number(b.sprint_num) || 0));

      // Enriquecer sprintData con testCases, criticalBugsPending y desglose por estado
      const enrichedSprintData = sprintData.map(sprint => {
        const testData = testCasesPerSprint.find(t => t.sprint === sprint.sprint);
        const stateData = criticalBugsByStateMap[sprint.sprint] || {
          tareasPorHacer: 0,
          enProgreso: 0,
          reabierto: 0
        };
        return {
          ...sprint,
          testCases: testData?.testCases || 0,
          testCasesExecuted: testData?.testCasesExecuted || 0,
          testCasesPlanned: testData?.testCasesPlanned || 0,
          criticalBugsPending: criticalBugsPendingMap[sprint.sprint] || 0,
          criticalBugsByState: stateData
        };
      });
      
      // Metadata
      const metadata = await DAL.getDataSourceInfo();
      return {
        summary,
        bugsByPriority,
        bugsByModule,
        bugsByCategory,
        developerData,
        sprintData: enrichedSprintData,
        metadata
      };
    },
  getDatabase,
  runQuery,
  runScalar,
  
  // Resumen
  getBugsSummary,
  getTotalBugs,
  getTotalSprints,
  getStatistics,
  
  // Por Sprint
  getBugsBySprint,
  getBugsBySprintIncludingSuggestions,
  getTestCasesBySprint,
  getPlannedTestCasesBySprint,
  getBugsBySprintAndStatus,
  getBugsBySprintNumber,
  getCriticalBugsPendingBySprint,
  getCriticalBugsBySprintAndState,
  
  // Por Desarrollador
  getBugsByDeveloper,
  getBugsByDeveloperName,
  
  // Por Prioridad
  getBugsByPriority,
  getCriticalBugs,
  
  // Por Módulo
  getBugsByModule,
  getDeveloperModulesSummary,
  
  // Por Categoría
  getBugsByCategory,
  
  // Detalles
  getBugDetail,
  getBugsByState,
  
  // Sprints
  getSprintInfo,
  getAllSprints,
  
  // Filtrado
  getBugsFiltered,
  
  // Metadata de origen de datos
  recordDataSourceMetadata,
  getLatestDataSourceMetadata,
  getAllDataSourceMetadata,
  getDataSourceInfo,
  
  // Team analysis
  getDevelopersAnalysis,
  getDeveloperByName,
  getTeamSummary
};

export default DAL;
